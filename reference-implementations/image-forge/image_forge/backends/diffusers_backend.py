"""Local diffusers backend — run any Hugging Face model on your own GPU, uncensored.

This is the fully-owned path: your hardware, your weights, no refusals, NSFW-capable
(SDXL fine-tunes like ``John6666/illustrij-v50-sdxl`` have no safety checker). It is
the in-process sibling of ``../../../YuriMedia/generate.py`` — same model registry
shape, same 16 GB-VRAM offload settings — wrapped as an image-forge backend so the
runtime calls it like any other.

Two things the user asked for, both here:

* **Configurable models + cache.** Models come from ``models.yaml`` (repo + pipeline
  + defaults); add any HF repo there. The download/cache location is set by
  ``cache_dir`` (→ ``$HF_HOME``), e.g. ``/mnt/6870C6B170C68572/AI/huggingface``.
* **Local NSFW-friendly editing for character consistency.** ``edit()`` re-renders an
  existing image with **img2img** (keep the composition, change clothes/scene), and
  both ``generate()`` and ``edit()`` can hold *her* identity with an **IP-Adapter**
  fed the character's reference images — "same Yuri, different scene/outfit" without
  training a LoRA (→ ch. 26, reference-driven consistency).

torch/diffusers are imported lazily, so importing this module (and the rest of
image-forge) costs nothing until you actually load a model.
"""

from __future__ import annotations

import logging
import os
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from ..types import Capabilities, EditRequest, GenRequest, ImageResult
from .base import ImageBackend

_LORA_TAG = re.compile(r"\s*<lora:[^>]+>\s*")
_PKG_ROOT = Path(__file__).resolve().parents[2]   # the image-forge/ folder


@contextmanager
def _quiet(*logger_names: str):
    """Temporarily raise the named libraries' loggers to ERROR, to hush *expected*
    cosmetic warnings. We use this around two unavoidable-but-benign messages:
    transformers' "Token indices sequence length is longer than 77" (fired while we
    measure a long prompt before handing it to sd_embed, which encodes it fully), and
    diffusers' "No LoRA keys associated to CLIPTextModel" (our LoRA is unet-only by
    design, so it legitimately has no text-encoder keys). Restored on exit."""
    loggers = [logging.getLogger(n) for n in logger_names]
    prev = [lg.level for lg in loggers]
    for lg in loggers:
        lg.setLevel(logging.ERROR)
    try:
        yield
    finally:
        for lg, lvl in zip(loggers, prev):
            lg.setLevel(lvl)


def clean_prompt(prompt: str) -> str:
    """Strip A1111/ComfyUI ``<lora:...>`` tags diffusers can't parse (matches YuriMedia)."""
    if "<lora:" not in prompt:
        return prompt
    prompt = _LORA_TAG.sub(" ", prompt)
    prompt = re.sub(r"\s+,", ",", prompt)        # space left before a comma
    prompt = re.sub(r",\s*,", ",", prompt)       # collapsed double comma
    return re.sub(r"\s{2,}", " ", prompt).strip()


class ModelRegistry:
    """The models.yaml table: name -> {repo, pipeline, defaults, description}."""

    def __init__(self, models: Dict[str, Dict[str, Any]]):
        self.models = models

    @classmethod
    def load(cls, path: str | Path) -> "ModelRegistry":
        path = Path(path)
        if not path.is_absolute() and not path.exists():
            alt = _PKG_ROOT / path           # fall back to the bundled registry
            if alt.exists():
                path = alt
        return cls(yaml.safe_load(path.read_text()) or {})

    def get(self, name: str) -> Dict[str, Any]:
        if name not in self.models:
            raise KeyError(f"unknown model {name!r}; have: {', '.join(self.models)}")
        return self.models[name]


class DiffusersBackend(ImageBackend):
    name = "diffusers"

    def __init__(
        self,
        model: str = "illustrij",
        *,
        registry: str | Path = "models.yaml",
        cache_dir: Optional[str] = None,
        device: str = "cuda",
        dtype: str = "float16",
        # model = move whole modules to GPU just-in-time (fits 16 GB for SDXL, fast,
        # and compatible with the long-prompt encoder). sequential = layer-by-layer
        # (lowest VRAM, but its meta-tensor weights break sd_embed's direct encoder
        # calls — use only without long prompts). none = keep all on device.
        offload: str = "model",               # model | sequential | none
        attention_slicing: bool = True,
        vae_tiling: bool = True,
        xformers: bool = True,
        ip_adapter: Optional[Dict[str, Any]] = None,  # {repo, subfolder, weight_name, scale}
        lora: Optional[Tuple[str, float]] = None,      # (path-or-name, weight) — fused at load
        quantize: Optional[str] = None,        # None | "4bit" | "8bit" (bitsandbytes)
        quantize_components: Optional[list] = None,    # e.g. ["transformer","text_encoder"]
        face_detailer: Optional[Dict[str, Any]] = None,  # {enabled, conf_threshold, ...}
        hires_fix: Optional[Dict[str, Any]] = None,       # {enabled, scale, strength, steps}
    ) -> None:
        # Set the HF cache BEFORE diffusers/huggingface_hub is imported anywhere.
        if cache_dir:
            os.environ["HF_HOME"] = cache_dir
            os.environ.setdefault("HF_HUB_CACHE", str(Path(cache_dir) / "hub"))
        self.cache_dir = cache_dir
        self.registry = ModelRegistry.load(registry)
        self.model = model
        self.config = self.registry.get(model)
        self.device = device
        # dtype / quantization can be set per-model in models.yaml (preferred for big
        # models that need bf16 + 4-bit) with the constructor value as the fallback.
        self.dtype = self.config.get("dtype", dtype)
        self.offload = offload
        self.attention_slicing = attention_slicing
        self.vae_tiling = vae_tiling
        self.xformers = xformers
        self.ip_adapter = ip_adapter
        self.lora = lora
        self._lora_loaded = False
        self.quantize = self.config.get("quantize", quantize)
        self.quantize_components = (quantize_components
                                    or self.config.get("quantize_components")
                                    or ["transformer", "text_encoder"])
        self.supports_negative = self.config.get("supports_negative", True)
        self._base = None          # cached txt2img pipeline
        self._i2i = None           # cached img2img pipeline (shares weights)
        self._ip_loaded = False
        self._warned_long = False
        # ADetailer-style face restoration (→ ch. 26, the small-face fix). Off unless
        # config.yaml passes `face_detailer: {enabled: true}`. Resolved to defaults here.
        self.face_detailer = self._resolve_face_detailer(face_detailer)
        self._face_det = None      # cached RetinaFace detector
        self._warned_fd = False
        # Hi-res fix: whole-image upscale + a second low-denoise sampler pass for global
        # crispness (→ ch. 26). Off unless config.yaml passes `hires_fix: {enabled: true}`.
        self.hires_fix = self._resolve_hires_fix(hires_fix)

    @staticmethod
    def _resolve_hires_fix(hf: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not hf or not hf.get("enabled"):
            return None
        return {
            "scale": hf.get("scale", 1.5),         # output = base dims × scale (8-aligned)
            "strength": hf.get("strength", 0.4),   # denoise of the second pass
            "steps": hf.get("steps"),              # None → model default
        }

    @staticmethod
    def _resolve_face_detailer(fd: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not fd or not fd.get("enabled"):
            return None
        return {
            # detection
            "conf_threshold": fd.get("conf_threshold", 0.7),
            "max_faces": fd.get("max_faces", 4),
            # only redraw *starved* faces — those whose longest side is below this
            # fraction of the image height. A face that already fills the frame has
            # enough pixels; set to 1.0 to detail every detected face.
            "max_face_ratio": fd.get("max_face_ratio", 0.35),
            # crop / blend
            "padding": fd.get("padding", 0.4),     # extra context around the face box
            "size": fd.get("size", 1024),          # working res the crop is redrawn at
            "feather": fd.get("feather", 0.12),    # mask-edge softness (fraction of crop)
            # img2img redraw
            "strength": fd.get("strength", 0.45),  # how far from the original to redraw
            "steps": fd.get("steps"),              # None → model default
        }

    # ---- torch/diffusers seams (monkeypatched in tests) ----

    @staticmethod
    def _diffusers():
        import diffusers
        return diffusers

    @staticmethod
    def _torch():
        import torch
        return torch

    def _torch_dtype(self):
        torch = self._torch()
        return {"float16": torch.float16, "bfloat16": torch.bfloat16,
                "float32": torch.float32}[self.dtype]

    def _quant_config(self):
        """bitsandbytes quantization for models too big for 16 GB at full precision
        (Qwen-Image, FLUX.2). Quantizes the named heavy components in place."""
        diffusers = self._diffusers()
        torch = self._torch()
        if self.quantize == "4bit":
            backend = "bitsandbytes_4bit"
            kwargs = {"load_in_4bit": True, "bnb_4bit_quant_type": "nf4",
                      "bnb_4bit_compute_dtype": torch.bfloat16}
        elif self.quantize == "8bit":
            backend = "bitsandbytes_8bit"
            kwargs = {"load_in_8bit": True}
        else:
            raise ValueError(f"unknown quantize {self.quantize!r} (4bit|8bit)")
        return diffusers.PipelineQuantizationConfig(
            quant_backend=backend, quant_kwargs=kwargs,
            components_to_quantize=self.quantize_components)

    # ---- pipeline loading ----

    def _apply_attention_settings(self, pipe) -> None:
        # attention_slicing and xformers REPLACE the attention processors, which would
        # clobber an IP-Adapter's processors — skip when IP-Adapter is set. They're
        # also SDXL-oriented; skip for quantized DiT models (Qwen/FLUX) too. VAE
        # tiling/slicing is safe either way and helps big-model VRAM.
        skip = self.ip_adapter or self.quantize
        if self.attention_slicing and not skip:
            pipe.enable_attention_slicing()
        if self.vae_tiling and hasattr(pipe, "vae"):
            pipe.vae.enable_tiling()
            pipe.vae.enable_slicing()
        if self.xformers and not skip:
            try:
                pipe.enable_xformers_memory_efficient_attention()
            except Exception:
                pass

    def _apply_offload(self, pipe) -> None:
        if self.offload == "sequential":
            pipe.enable_sequential_cpu_offload()
        elif self.offload == "model":
            pipe.enable_model_cpu_offload()
        else:
            pipe.to(self.device)

    def _maybe_load_ip_adapter(self, pipe) -> bool:
        """Load the IP-Adapter onto a pipe once; return whether it's available."""
        if not self.ip_adapter:
            return False
        if not self._ip_loaded:
            kw = {}
            # The "plus"/vit-h adapters need a different image encoder than the base
            # bigG one. When the config names it (image_encoder_subfolder), we load it
            # explicitly in _base_pipe and set it on the pipe, so here we tell
            # load_ip_adapter NOT to fetch one (image_encoder_folder=None).
            if self.ip_adapter.get("image_encoder_subfolder"):
                kw["image_encoder_folder"] = None
            pipe.load_ip_adapter(
                self.ip_adapter["repo"],
                subfolder=self.ip_adapter.get("subfolder", "sdxl_models"),
                weight_name=self.ip_adapter["weight_name"],
                **kw,
            )
            pipe.set_ip_adapter_scale(self.ip_adapter.get("scale", 0.6))
            self._ip_loaded = True
        return True

    def _normalize_scheduler(self, pipe) -> None:
        """Some community SDXL checkpoints (e.g. Nova Anime XL) ship an *EDM* scheduler
        (EDMDPMSolverMultistepScheduler, sigma_max≈80). diffusers' standard SDXL path
        mishandles those sigmas → the latent never denoises → pure-noise output. The
        model itself is ordinary epsilon SDXL, so we swap to the equivalent standard
        sampler (DPM++ 2M Karras, what the EDM config was emulating). A models.yaml
        ``scheduler:`` key (euler_a | euler | dpmpp_2m | dpmpp_2m_karras) overrides."""
        diffusers = self._diffusers()
        want = self.config.get("scheduler")
        cur = type(pipe.scheduler).__name__
        if not want and not cur.startswith("EDM"):
            return                                   # standard scheduler — leave it
        cfg = pipe.scheduler.config
        if not want:
            want = "euler_a"                          # past the guard ⇒ EDM: rescue it
        # EDM configs carry sigma_min/max + final_sigmas_type keys that trip
        # DPMSolverMultistep's sigma indexing (off-by-one); strip them so the standard
        # scheduler rebuilds its own sigma schedule from beta_* cleanly.
        cfg = {k: v for k, v in dict(cfg).items()
               if k not in ("sigma_min", "sigma_max", "sigma_data", "sigma_schedule",
                            "final_sigmas_type", "rho")}
        table = {
            "euler_a": (diffusers.EulerAncestralDiscreteScheduler, {}),
            "euler": (diffusers.EulerDiscreteScheduler, {}),
            "dpmpp_2m": (diffusers.DPMSolverMultistepScheduler, {}),
            "dpmpp_2m_karras": (diffusers.DPMSolverMultistepScheduler,
                                {"use_karras_sigmas": True, "algorithm_type": "dpmsolver++"}),
        }
        cls, extra = table.get(want, table["euler_a"])
        pipe.scheduler = cls.from_config(cfg, **extra)
        print(f"[diffusers] {self.model}: scheduler {cur} -> {type(pipe.scheduler).__name__}"
              + (f" ({want})" if extra else ""), flush=True)

    def _base_pipe(self):
        if self._base is None:
            diffusers = self._diffusers()
            pipe_cls = getattr(diffusers, self.config["pipeline"])
            load_kwargs = dict(torch_dtype=self._torch_dtype())
            if self.quantize:
                # Quantized load places weights itself; don't also pin to CPU.
                load_kwargs["quantization_config"] = self._quant_config()
            else:
                load_kwargs["device_map"] = "cpu"
            # Custom IP-Adapter image encoder (e.g. vit-h for the "plus" adapters):
            # load it here and pass it in so it's a registered pipe component (moves
            # with .to(device)/offload). Avoids load_ip_adapter's path resolution.
            if self.ip_adapter and self.ip_adapter.get("image_encoder_subfolder"):
                from transformers import CLIPVisionModelWithProjection
                load_kwargs["image_encoder"] = CLIPVisionModelWithProjection.from_pretrained(
                    self.ip_adapter.get("image_encoder_repo", self.ip_adapter["repo"]),
                    subfolder=self.ip_adapter["image_encoder_subfolder"],
                    torch_dtype=self._torch_dtype())
            repo = self.config["repo"]
            # Single-file checkpoint (a local .safetensors/.ckpt, e.g. a Civitai
            # download) vs a diffusers-format repo/folder. from_single_file builds the
            # pipeline from one file; it doesn't take device_map, so drop that.
            if str(repo).endswith((".safetensors", ".ckpt")):
                load_kwargs.pop("device_map", None)
                pipe = pipe_cls.from_single_file(repo, **load_kwargs)
            else:
                pipe = pipe_cls.from_pretrained(repo, **load_kwargs)
            self._normalize_scheduler(pipe)
            # Order matters: attention tweaks first, then IP-Adapter (so they don't
            # overwrite its processors), then offload/device last (so the IP-Adapter
            # image encoder gets the same hooks / lands on the right device).
            self._apply_attention_settings(pipe)
            if self.ip_adapter:
                self._maybe_load_ip_adapter(pipe)
            # Fuse the character LoRA BEFORE offload (offload's device hooks fight
            # load_lora_weights). fuse + unload bakes it into the base weights, so
            # the img2img pipe (from_pipe) shares it and there's no per-call scale.
            if self.lora and not self._lora_loaded:
                path, weight = self.lora
                # unet-only LoRA → diffusers warns about absent text-encoder keys; expected.
                with _quiet("diffusers"):
                    pipe.load_lora_weights(path)
                    pipe.fuse_lora(lora_scale=float(weight))
                    pipe.unload_lora_weights()
                self._lora_loaded = True
            self._apply_offload(pipe)
            self._base = pipe
        return self._base

    def _img2img_pipe(self):
        if self._i2i is None:
            diffusers = self._diffusers()
            # Share the already-loaded weights — no second copy in memory.
            self._i2i = diffusers.AutoPipelineForImage2Image.from_pipe(self._base_pipe())
        return self._i2i

    # ---- hi-res fix (whole-image upscale + refine, → ch. 26) ----

    def _hires_fix(self, image, positive: str, negative: str, seed):
        """Upscale the finished image and run a second low-denoise img2img pass over the
        whole frame, so global detail (skin, hair, fabric) is rendered at a resolution
        the base pass never had. Complements the face detailer: this lifts the *whole*
        image's crispness, the detailer fixes *small faces* specifically. Returns
        ``(image, (w, h))`` with the new size, or ``(image, None)`` when disabled."""
        hf = self.hires_fix
        if not hf:
            return image, None
        from PIL import Image
        base = self._base_pipe()
        i2i = self._img2img_pipe()
        W, H = image.size
        scale = float(hf["scale"])
        nw = max(8, int(round(W * scale / 8)) * 8)     # SDXL needs /8 dims
        nh = max(8, int(round(H * scale / 8)) * 8)
        up = image.convert("RGB").resize((nw, nh), Image.LANCZOS)
        d = self.config.get("defaults", {})
        steps = hf["steps"] or d.get("num_inference_steps", 30)
        guidance = d.get("guidance_scale", 5.0)
        kwargs: Dict[str, Any] = dict(
            image=up, strength=float(hf["strength"]),
            num_inference_steps=steps, guidance_scale=guidance,
            generator=self._generator(seed),
        )
        self._apply_prompt(kwargs, base, positive, negative)
        out = i2i(**kwargs).images[0]
        return out, (nw, nh)

    # ---- face detailer (ADetailer-style small-face fix, → ch. 26) ----

    def _detector(self):
        """Lazy-load a RetinaFace face detector (facexlib — the same one GFPGAN uses).
        Cached on the instance; weights download once under the HF cache dir."""
        if self._face_det is None:
            from facexlib.detection import init_detection_model
            root = str(Path(self.cache_dir) / "facexlib") if self.cache_dir else None
            self._face_det = init_detection_model(
                "retinaface_resnet50", device=self.device, model_rootpath=root)
        return self._face_det

    def _detail_faces(self, image, positive: str, negative: str, seed):
        """Re-render each *starved* face at full resolution and composite it back.

        Why this exists: SDXL works in a 1/8-res latent, so a small/distant face in a
        full-body shot gets only a handful of latent pixels — not enough to resolve
        eyes/pupils, which is why they degrade. A bigger/better LoRA can't fix that
        (it changes *what* is drawn, not the resolution it's drawn at). The fix is to
        detect the face, crop it, upscale the crop, redraw it with the *same fused-LoRA*
        img2img pipe (so identity carries), then feather it back in. Returns
        ``(image, faces_fixed)``."""
        fd = self.face_detailer
        if not fd:
            return image, 0
        try:
            import numpy as np
            det = self._detector()
        except Exception as e:                       # facexlib missing / no weights
            if not self._warned_fd:
                print(f"[diffusers] face-detailer unavailable ({e}); skipping. "
                      "Install with `pip install facexlib`.", flush=True)
                self._warned_fd = True
            return image, 0
        from PIL import Image, ImageDraw, ImageFilter
        torch = self._torch()
        rgb = image.convert("RGB")
        W, H = rgb.size
        bgr = np.asarray(rgb)[:, :, ::-1]            # facexlib wants BGR
        with torch.no_grad():
            boxes = det.detect_faces(bgr, conf_threshold=fd["conf_threshold"])
        if boxes is None or len(boxes) == 0:
            return image, 0
        base = self._base_pipe()
        i2i = self._img2img_pipe()
        d = self.config.get("defaults", {})
        steps = fd["steps"] or d.get("num_inference_steps", 30)
        guidance = d.get("guidance_scale", 5.0)
        size = int(fd["size"])
        out = rgb.copy()
        fixed = 0
        for row in boxes[: fd["max_faces"]]:
            x1, y1, x2, y2 = (float(row[0]), float(row[1]), float(row[2]), float(row[3]))
            fw, fh = x2 - x1, y2 - y1
            if fw <= 0 or fh <= 0:
                continue
            if max(fw, fh) / H > fd["max_face_ratio"]:
                continue                              # already big enough — leave it
            # Padded square crop, clamped fully inside the frame (keeps it square).
            side = min(max(fw, fh) * (1 + fd["padding"]), W, H)
            s = int(round(side))
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            bx = int(round(min(max(cx - side / 2, 0), W - side)))
            by = int(round(min(max(cy - side / 2, 0), H - side)))
            crop = out.crop((bx, by, bx + s, by + s))
            work = crop.resize((size, size), Image.LANCZOS)
            kwargs: Dict[str, Any] = dict(
                image=work, strength=float(fd["strength"]),
                num_inference_steps=steps, guidance_scale=guidance,
                generator=self._generator(seed),
            )
            self._apply_prompt(kwargs, base, positive, negative)
            redrawn = i2i(**kwargs).images[0].resize((s, s), Image.LANCZOS)
            # Feathered mask so the redrawn crop melts into the original (no seam).
            mask = Image.new("L", (s, s), 0)
            inset = max(1, int(s * 0.06))
            ImageDraw.Draw(mask).rectangle((inset, inset, s - inset, s - inset), fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(max(2, int(s * fd["feather"]))))
            out.paste(redrawn, (bx, by), mask)
            fixed += 1
        return (out, fixed) if fixed else (image, 0)

    # ---- request helpers ----

    def _resolve_steps_guidance(self, req) -> Tuple[int, float]:
        d = self.config.get("defaults", {})
        steps = req.steps if getattr(req, "steps", None) else d.get("num_inference_steps", 30)
        cfg = getattr(req, "cfg", None)
        guidance = cfg if cfg is not None else d.get("guidance_scale", 5.0)
        return steps, guidance

    def _generator(self, seed: Optional[int]):
        if seed is None:
            return None
        return self._torch().Generator(device="cpu").manual_seed(seed)

    def _load_refs(self, paths: List[Path]):
        from PIL import Image
        return [Image.open(p).convert("RGB") for p in paths]

    def _encode_long_prompt(self, pipe, positive: str, negative: str):
        """SDXL's CLIP truncates at 77 tokens, which silently drops most of a rich
        character+scene prompt (and its negative). For long prompts, encode the full
        text with `sd_embed` (handles SDXL's two encoders + pooled embeds) and return
        embed kwargs for the pipeline call.

        Returns None to mean "use the plain prompt strings" — for short prompts, a
        non-SDXL pipeline, or when sd_embed isn't installed (logged once, then the
        pipeline truncates as usual).
        """
        # sd_embed targets SDXL's dual-CLIP specifically. FLUX/Qwen also have a
        # text_encoder_2 but handle long prompts natively (T5/Qwen) — don't touch them.
        if "StableDiffusionXL" not in type(pipe).__name__:
            return None
        tok = getattr(pipe, "tokenizer", None)
        is_sdxl = getattr(pipe, "text_encoder_2", None) is not None
        if tok is None or not is_sdxl:
            return None
        # Measuring length tokenizes the full prompt → transformers warns it's >77;
        # that's exactly why we route to sd_embed below, so the warning is noise.
        with _quiet("transformers"):
            n_tokens = len(tok(positive).input_ids)
        if n_tokens <= tok.model_max_length:                 # fits in 77 — plain path
            return None
        try:
            from sd_embed.embedding_funcs import get_weighted_text_embeddings_sdxl
        except ImportError:
            if not self._warned_long:
                print(f"[diffusers] prompt is {n_tokens} tokens (>{tok.model_max_length}); "
                      "install sd_embed for full-length prompts "
                      "(`pip install --no-deps git+https://github.com/xhinker/sd_embed.git`) "
                      "— truncating for now.", flush=True)
                self._warned_long = True
            return None
        # sd_embed re-tokenizes the full text to chunk it (same >77 warning) — hush it.
        with _quiet("transformers"):
            pos_embeds, neg_embeds, pos_pooled, neg_pooled = get_weighted_text_embeddings_sdxl(
                pipe, prompt=positive, neg_prompt=negative or "")
        return dict(
            prompt_embeds=pos_embeds, pooled_prompt_embeds=pos_pooled,
            negative_prompt_embeds=neg_embeds, negative_pooled_prompt_embeds=neg_pooled,
        )

    def _apply_prompt(self, kwargs: Dict[str, Any], pipe, positive: str, negative: str) -> None:
        """Put either embeds (long prompts) or plain strings into the call kwargs."""
        embeds = self._encode_long_prompt(pipe, positive, negative)
        if embeds:
            kwargs.update(embeds)
        else:
            kwargs["prompt"] = positive
            kwargs["negative_prompt"] = negative or None

    # ---- backend API ----

    def generate(self, req: GenRequest) -> ImageResult:
        # Honour a character LoRA passed via the request (service fills this from
        # characters/*.yaml) when one wasn't set on the backend directly.
        if getattr(req, "lora", None) and not self.lora and not self._lora_loaded:
            self.lora = req.lora
        pipe = self._base_pipe()
        steps, guidance = self._resolve_steps_guidance(req)
        kwargs: Dict[str, Any] = dict(
            width=req.width, height=req.height,
            num_inference_steps=steps, guidance_scale=guidance,
            generator=self._generator(req.seed),
        )
        # Pass through any other call kwargs declared in the model's defaults
        # (e.g. Qwen-Image's true_cfg_scale).
        for k, v in self.config.get("defaults", {}).items():
            if k not in ("num_inference_steps", "guidance_scale"):
                kwargs.setdefault(k, v)
        self._apply_prompt(kwargs, pipe, clean_prompt(req.prompt), req.negative_prompt)
        if not self.supports_negative:
            kwargs.pop("negative_prompt", None)      # FLUX is guidance-distilled
        if req.reference_images and self._maybe_load_ip_adapter(pipe):
            kwargs["ip_adapter_image"] = self._load_refs(req.reference_images)
        image = pipe(**kwargs).images[0]
        pos = clean_prompt(req.prompt)
        hires = None
        if self.hires_fix:
            image, dims = self._hires_fix(image, pos, req.negative_prompt, req.seed)
            hires = f"{dims[0]}x{dims[1]}" if dims else None
        faces = None
        if self.face_detailer:
            image, n = self._detail_faces(image, pos, req.negative_prompt, req.seed)
            faces = n
        fw, fh = image.size
        return self._result(image, req.seed, req.prompt, req.negative_prompt,
                            steps=steps, guidance=guidance,
                            width=fw, height=fh, faces_detailed=faces, hires=hires)

    def edit(self, req: EditRequest) -> ImageResult:
        from PIL import Image
        base = self._base_pipe()
        pipe = self._img2img_pipe()
        source = Image.open(req.image).convert("RGB")
        steps, guidance = self._resolve_steps_guidance(req)
        kwargs: Dict[str, Any] = dict(
            image=source, strength=req.strength,
            num_inference_steps=steps, guidance_scale=guidance,
            generator=self._generator(req.seed),
        )
        self._apply_prompt(kwargs, base, clean_prompt(req.instruction), req.negative_prompt)
        refs = getattr(req, "reference_images", None) or []
        if refs and self._maybe_load_ip_adapter(base):
            kwargs["ip_adapter_image"] = self._load_refs(refs)
        image = pipe(**kwargs).images[0]
        faces = None
        if self.face_detailer:
            image, n = self._detail_faces(
                image, clean_prompt(req.instruction), req.negative_prompt, req.seed)
            faces = n
        return self._result(image, req.seed, req.instruction, req.negative_prompt,
                            steps=steps, guidance=guidance, edit=True, faces_detailed=faces)

    def _result(self, pil_image, seed, prompt, negative, **meta) -> ImageResult:
        import io
        buf = io.BytesIO()
        pil_image.save(buf, "PNG")
        model_id = f"diffusers:{self.model}" + ("-img2img" if meta.pop("edit", False) else "")
        # Record the exact identity machinery so a saved image is fully reproducible:
        # which LoRA (path + fused weight) and/or IP-Adapter steered this render.
        if self.lora:
            meta["lora"] = str(self.lora[0])
            meta["lora_weight"] = float(self.lora[1])
        if self.ip_adapter:
            meta["ip_adapter"] = str(self.ip_adapter)
        return ImageResult.new(buf.getvalue(), self.name, model=model_id, repo=self.config["repo"],
                               seed=seed, prompt=prompt, negative=negative, **meta)

    def capabilities(self) -> Capabilities:
        return Capabilities(
            name=self.name, supports_edit=True,
            supports_reference_images=self.ip_adapter is not None, max_reference_images=4,
            supports_lora=True, uncensored=True,
            notes=f"local diffusers; model={self.model} ({self.config['repo']})"
                  + (" +IP-Adapter" if self.ip_adapter else ""),
        )

    def health(self) -> bool:
        try:
            return bool(self._torch().cuda.is_available())
        except Exception:
            return False
