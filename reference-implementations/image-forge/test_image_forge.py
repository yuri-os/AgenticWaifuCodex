"""Unit + integration tests for image-forge.

Run from this folder:  python -m pytest          (or just `pytest`)

These run entirely on the mock backend and offline checks — no GPU, no API key,
no network — so CI and a fresh laptop both pass. The guarantees they lock in:

  * the locked register is assembled in the right order, and the clothing/anatomy
    guard is applied only when a figure is in frame (the generate.py rule);
  * selfie composition is deterministic, honours pinned slots, and rotates the
    rest from a seed (the anti-collapse mechanism);
  * provenance strips or embeds metadata as asked;
  * every backend constructs, reports honest capabilities, and the networked ones
    fail closed (health() false) without credentials;
  * the full service turns a high-level ask into a valid, correctly-sized,
    on-register PNG, and a runtime backend swap actually changes the generator.
"""

import contextlib
import io
import json
import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # make the package importable standalone

from PIL import Image  # noqa: E402

from image_forge import (  # noqa: E402
    Capabilities, Character, GenRequest, ImageForge, ImageResult, SelfieBook,
    make_backend,
)
from image_forge import provenance  # noqa: E402
from image_forge.backends.mock import MockBackend  # noqa: E402
from image_forge.types import EditRequest  # noqa: E402

CHAR = HERE / "characters" / "yuri.yaml"
TEMPLATES = HERE / "templates" / "selfie.yaml"
CONFIG = HERE / "config.yaml"


# ---------------------------------------------------------------- fixtures

@pytest.fixture
def character() -> Character:
    return Character.load(CHAR)


@pytest.fixture
def book() -> SelfieBook:
    return SelfieBook.load(TEMPLATES)


@pytest.fixture
def forge(tmp_path) -> ImageForge:
    # The shipped config defaults to the diffusers+LoRA backend (needs a GPU); these
    # service tests run offline, so swap in the deterministic mock generator. The
    # diffusers backend constructs without importing torch (lazy), so from_config is
    # still exercised; set_backend("mock") then makes generation offline.
    f = ImageForge.from_config(CONFIG)
    f.set_backend("mock")
    f.out_dir = tmp_path            # don't litter the real out/
    return f


def _png_size(data: bytes):
    im = Image.open(io.BytesIO(data))
    return im.size


# ---------------------------------------------------------------- character

def test_character_loads_locked_register(character):
    assert character.name == "Yuri"
    assert "2.5D" in character.quality_preamble          # D-011 register present
    assert "cat ears" in character.identity
    assert character.width == 832 and character.height == 1216


def test_assemble_orders_preamble_identity_scene(character):
    pos, neg = character.assemble("SCENE_MARKER")
    assert pos.index(character.quality_preamble.strip()[:20]) \
        < pos.index(character.identity.strip()[:20]) \
        < pos.index("SCENE_MARKER")


def test_assemble_includes_character_guard_only_with_figure(character):
    _, neg_with = character.assemble("scene", include_character=True)
    _, neg_without = character.assemble("scene", include_character=False)
    assert "dark skin" in neg_with                       # skin/anatomy guard (no nudity guard)
    assert "dark skin" not in neg_without                # dropped for scenery
    assert "watermark" in neg_with and "watermark" in neg_without  # base always


def test_assemble_drops_identity_for_scenery(character):
    pos, _ = character.assemble("a city", include_character=False)
    assert "cat ears" not in pos                         # no figure primed in
    assert character.quality_preamble.strip()[:20] in pos  # register still applied


def test_assemble_negative_extra_appended(character):
    _, neg = character.assemble("scene", negative_extra="EXTRA_NEG")
    assert "EXTRA_NEG" in neg


def test_trigger_token_prepended_when_set(tmp_path):
    cfg = tmp_path / "c.yaml"
    cfg.write_text(
        "name: T\nquality_preamble: PRE\nidentity: ID\n"
        "base_negative: BN\ntrigger: my_token\n")
    c = Character.load(cfg)
    pos, _ = c.assemble("scene")
    assert pos.index("my_token") < pos.index("ID")


# ---------------------------------------------------------------- templates

def test_compose_respects_pinned_slots(book):
    prompt, chosen = book.compose(scene="window", mood="happy", wardrobe="cozy", seed=0)
    assert chosen["scene"] == "window"
    assert chosen["mood"] == "happy"
    assert chosen["wardrobe"] == "cozy"
    assert book.scenes["window"] in prompt


def test_compose_is_deterministic_for_a_seed(book):
    a = book.compose(seed=42)
    b = book.compose(seed=42)
    assert a == b


def test_compose_rotates_unpinned_slots(book):
    # Different seeds should (very likely) pick different scenes.
    picks = {book.compose(seed=s)[1]["scene"] for s in range(8)}
    assert len(picks) > 1


def test_compose_unknown_option_raises(book):
    with pytest.raises(KeyError):
        book.compose(scene="nonexistent")


def test_intimate_tier_is_available_not_gated(book):
    prompt, chosen = book.compose(scene="bed", wardrobe="intimate", seed=1)
    assert chosen["wardrobe"] == "intimate"
    assert book.wardrobe["intimate"] in prompt           # composed, not refused


# ---------------------------------------------------------------- provenance

def test_strip_removes_metadata():
    src = Image.new("RGB", (8, 8))
    from PIL import PngImagePlugin
    info = PngImagePlugin.PngInfo()
    info.add_text("secret", "leak")
    buf = io.BytesIO(); src.save(buf, "PNG", pnginfo=info)
    out = provenance.apply(buf.getvalue(), {}, "strip")
    assert "secret" not in Image.open(io.BytesIO(out)).info


def test_embed_writes_content_credentials():
    src = io.BytesIO(); Image.new("RGB", (8, 8)).save(src, "PNG")
    out = provenance.apply(src.getvalue(), {"backend": "mock", "model": "m"}, "embed")
    info = Image.open(io.BytesIO(out)).info
    assert "content_credentials" in info
    assert "mock" in info["content_credentials"]


def test_raw_passes_bytes_through():
    data = b"not even a png"
    assert provenance.apply(data, {}, "raw") == data


def test_unknown_provenance_mode_raises():
    src = io.BytesIO(); Image.new("RGB", (8, 8)).save(src, "PNG")
    with pytest.raises(ValueError):
        provenance.apply(src.getvalue(), {}, "bogus")


# ---------------------------------------------------------------- mock backend

def test_mock_generate_is_deterministic():
    b = MockBackend()
    r1 = b.generate(GenRequest(prompt="hello", seed=5))
    r2 = b.generate(GenRequest(prompt="hello", seed=5))
    assert r1.data == r2.data
    assert b.generate(GenRequest(prompt="hello", seed=6)).data != r1.data


def test_mock_respects_dimensions():
    r = MockBackend().generate(GenRequest(prompt="x", width=512, height=768))
    assert _png_size(r.data) == (512, 768)


def test_mock_seed_derived_from_prompt_when_absent():
    b = MockBackend()
    assert b.generate(GenRequest(prompt="abc")).data == b.generate(GenRequest(prompt="abc")).data


def test_mock_edit_overlays_on_source(tmp_path):
    b = MockBackend()
    src = tmp_path / "s.png"
    b.generate(GenRequest(prompt="base", width=256, height=256)).save(src)
    out = b.edit(EditRequest(image=src, instruction="change it"))
    assert _png_size(out.data) == (256, 256)             # same canvas, edited


def test_mock_capabilities_are_uncensored():
    c = MockBackend().capabilities()
    assert isinstance(c, Capabilities)
    assert c.supports_edit and c.uncensored is True


# ---------------------------------------------------------------- registry

@pytest.mark.parametrize("name", ["mock", "openrouter", "comfyui", "replicate", "diffusers"])
def test_every_backend_constructs_and_reports_caps(name):
    cap = make_backend(name).capabilities()
    assert cap.name == name
    assert isinstance(cap.supports_edit, bool)


def test_unknown_backend_raises():
    with pytest.raises(KeyError):
        make_backend("does-not-exist")


def test_networked_backends_fail_closed_without_credentials(monkeypatch):
    monkeypatch.delenv("OPENROUTER_TOKEN", raising=False)
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    monkeypatch.setattr(Path, "home", lambda: Path("/nonexistent-home-xyz"))
    assert make_backend("openrouter").health() is False
    assert make_backend("replicate").health() is False
    # ComfyUI points at a port nothing is listening on.
    assert make_backend("comfyui", port=59999).health() is False


def test_generate_only_backend_refuses_edit():
    b = make_backend("openrouter")                       # riverflow default, edit off
    with pytest.raises(NotImplementedError):
        b.edit(EditRequest(image=Path("x.png"), instruction="y"))


# ---------------------------------------------------------------- comfyui graph

def test_comfyui_fill_yields_valid_json_with_int_types():
    b = make_backend("comfyui", checkpoint="model.safetensors")
    g = b._fill(b.workflow, {
        "%POSITIVE%": 'a "quoted" prompt, masterpiece',
        "%NEGATIVE%": "bad", "%SEED%": "12345",
        "%WIDTH%": "832", "%HEIGHT%": "1216", "%CKPT%": "model.safetensors",
    })
    assert g["3"]["inputs"]["seed"] == 12345             # int, not "12345"
    assert isinstance(g["5"]["inputs"]["width"], int)
    assert g["6"]["inputs"]["text"] == 'a "quoted" prompt, masterpiece'
    assert g["4"]["inputs"]["ckpt_name"] == "model.safetensors"


def test_comfyui_edit_requires_edit_workflow():
    b = make_backend("comfyui")                          # no edit_workflow set
    with pytest.raises(NotImplementedError):
        b.edit(EditRequest(image=Path("x.png"), instruction="y"))


# ---------------------------------------------------------------- ImageResult

def test_imageresult_save_and_meta(tmp_path):
    r = ImageResult.new(b"data", "mock", model="m", seed=3)
    assert r.meta["backend"] == "mock" and r.meta["seed"] == 3
    assert "request_id" in r.meta and "created_at" in r.meta
    p = r.save(tmp_path / "sub" / "x.png")
    assert p.read_bytes() == b"data" and r.path == p


def test_imageresult_new_drops_none_values():
    r = ImageResult.new(b"d", "mock", seed=None, model="m")
    assert "seed" not in r.meta and r.meta["model"] == "m"


# ---------------------------------------------------------------- service (integration)

def test_from_config_loads_everything():
    # Build straight from the shipped config (no mock override) to verify it parses
    # character, templates, and the configured default backend. Constructing the
    # diffusers backend doesn't import torch, so this stays offline.
    f = ImageForge.from_config(CONFIG)
    assert f.character.name == "Yuri"
    assert f.character.trigger == "yuri_v2"          # the trained LoRA is wired in
    assert "window" in f.book.scenes
    assert f.backend.capabilities().name == "diffusers"   # the shipped default


def test_selfie_produces_valid_onregister_png(forge):
    r = forge.selfie(scene="window", mood="happy", seed=1)
    assert _png_size(r.data) == (832, 1216)
    assert r.path.exists()
    assert r.meta["template"]["scene"] == "window"
    assert r.meta["character"] == "Yuri"
    assert r.meta["provenance"] == "strip"


def test_selfie_is_reproducible_by_seed(forge):
    a = forge.selfie(scene="window", seed=7, save=False)
    b = forge.selfie(scene="window", seed=7, save=False)
    assert a.data == b.data


def test_portrait_uses_signature_wardrobe(forge):
    r = forge.portrait(save=False)
    assert r.meta["template"]["wardrobe"] == "signature"


def test_scenery_has_no_figure_and_no_guard(forge, monkeypatch):
    captured = {}
    orig = forge.backend.generate

    def spy(req):
        captured["req"] = req
        return orig(req)

    monkeypatch.setattr(forge.backend, "generate", spy)
    forge.scenery("a wide city skyline", save=False)
    assert "cat ears" not in captured["req"].prompt        # no figure primed
    assert "no nudity" not in captured["req"].negative_prompt  # guard dropped


def test_edit_holds_through_service(forge):
    base = forge.selfie(scene="window", seed=1)
    out = forge.edit(base.path, "her in the rain", save=False)
    assert _png_size(out.data) == (832, 1216)


def test_provenance_strip_applied_to_output(forge):
    r = forge.selfie(scene="window", seed=1, save=False)
    assert Image.open(io.BytesIO(r.data)).info == {}       # nothing leaks


def test_embed_mode_stamps_credentials(forge):
    forge.provenance_mode = "embed"
    r = forge.selfie(scene="window", seed=1, save=False)
    assert "content_credentials" in Image.open(io.BytesIO(r.data)).info


def test_set_backend_swaps_generator_live(forge):
    assert forge.capabilities().name == "mock"
    sentinel = make_backend("mock")
    returned = forge.set_backend(sentinel)
    assert forge.backend is sentinel and returned is sentinel
    forge.set_backend("comfyui", port=8188)
    assert forge.capabilities().name == "comfyui"


def test_save_filename_encodes_label_and_seed(forge):
    r = forge.selfie(scene="kitchen", wardrobe="cozy", seed=2)
    assert "kitchen" in r.path.name and r.path.name.endswith("-2.png")


def test_save_writes_provenance_sidecar_and_ledger(forge):
    """Every saved image gets a .json sidecar (full how-it-was-made record) plus
    one appended line in out/generations.jsonl — the reproducibility log."""
    r = forge.selfie(scene="window", mood="happy", seed=5)

    sidecar = r.path.with_suffix(".json")
    assert sidecar.exists(), "expected a per-image provenance sidecar"
    rec = json.loads(sidecar.read_text())
    assert rec["image"] == r.path.name
    for key in ("backend", "model", "seed", "prompt", "negative", "character"):
        assert key in rec, f"sidecar missing {key}"
    assert rec["seed"] == 5

    ledger = forge.out_dir / "generations.jsonl"
    assert ledger.exists()
    last = json.loads(ledger.read_text().splitlines()[-1])
    assert last["image"] == r.path.name


def test_no_provenance_files_when_not_saving(forge):
    forge.selfie(scene="window", seed=1, save=False)
    assert not (forge.out_dir / "generations.jsonl").exists()
    assert not list(forge.out_dir.glob("*.json"))


def test_edit_forwards_character_reference_images(tmp_path):
    """The service hands the character's identity anchors to the backend's edit
    (so IP-Adapter etc. can hold her across the change)."""
    captured = {}

    class Recorder(MockBackend):
        def edit(self, req):
            captured["refs"] = list(req.reference_images)
            captured["strength"] = req.strength
            return super().edit(req)

    book = SelfieBook.load(TEMPLATES)
    char = Character.load(CHAR)
    char.reference_images = [Path("ref-a.png"), Path("ref-b.png")]
    f = ImageForge(char, book, Recorder(), out_dir=tmp_path)
    src = f.selfie(scene="window", seed=1)
    f.edit(src.path, "her in a red dress", strength=0.55, save=False)
    assert captured["refs"] == [Path("ref-a.png"), Path("ref-b.png")]
    assert captured["strength"] == 0.55
    # use_identity=False suppresses them
    f.edit(src.path, "her", use_identity=False, save=False)
    assert captured["refs"] == []


# ---------------------------------------------------------------- diffusers backend (local, no GPU needed)

import types as _types  # noqa: E402

from image_forge.backends.diffusers_backend import (  # noqa: E402
    DiffusersBackend, ModelRegistry, clean_prompt,
)


class _FakePipe:
    """Records calls; returns a PIL image so the result path is exercised."""

    def __init__(self):
        self.calls = []
        self.ip_loaded = False
        self.ip_scale = None
        self.vae = _types.SimpleNamespace(enable_tiling=lambda: None, enable_slicing=lambda: None)
        # _normalize_scheduler reads pipe.scheduler.config; a non-EDM-named fake with a
        # plain-dict config exercises the real swap path (illustrij pins scheduler: euler).
        self.scheduler = _types.SimpleNamespace(config={"beta_start": 0.00085, "beta_end": 0.012})

    # memory-setting no-ops
    def enable_sequential_cpu_offload(self): pass
    def enable_model_cpu_offload(self): pass
    def enable_attention_slicing(self): pass
    def enable_xformers_memory_efficient_attention(self): pass
    def to(self, _): return self

    def load_ip_adapter(self, *a, **k): self.ip_loaded = True
    def set_ip_adapter_scale(self, s): self.ip_scale = s

    def __call__(self, **kw):
        self.calls.append(kw)
        if "image" in kw and hasattr(kw["image"], "size"):   # img2img
            size = kw["image"].size
        else:
            size = (kw.get("width", 64), kw.get("height", 64))
        return _types.SimpleNamespace(images=[Image.new("RGB", size)])


def _fake_modules():
    base = _FakePipe()
    i2i = _FakePipe()

    pipe_cls = _types.SimpleNamespace(from_pretrained=lambda *a, **k: base)
    auto_i2i = _types.SimpleNamespace(from_pipe=lambda p: i2i)
    # _normalize_scheduler builds a new scheduler via diffusers.<Cls>.from_config(cfg);
    # fake those classes so the swap path runs without real diffusers.
    _sched_cls = lambda: _types.SimpleNamespace(
        from_config=lambda cfg, **extra: _types.SimpleNamespace(config=dict(cfg)))
    diffusers = _types.SimpleNamespace(
        StableDiffusionXLPipeline=pipe_cls, AutoPipelineForImage2Image=auto_i2i,
        EulerAncestralDiscreteScheduler=_sched_cls(), EulerDiscreteScheduler=_sched_cls(),
        DPMSolverMultistepScheduler=_sched_cls())

    torch = _types.SimpleNamespace(
        float16="f16", bfloat16="bf16", float32="f32",
        Generator=lambda device=None: _types.SimpleNamespace(manual_seed=lambda s: f"gen{s}"),
        no_grad=contextlib.nullcontext,                  # for the face-detailer pass
        cuda=_types.SimpleNamespace(is_available=lambda: True))
    return diffusers, torch, base, i2i


@pytest.fixture
def diff(monkeypatch):
    b = DiffusersBackend(model="illustrij")
    diffusers, torch, base, i2i = _fake_modules()
    monkeypatch.setattr(b, "_diffusers", lambda: diffusers)
    monkeypatch.setattr(b, "_torch", lambda: torch)
    return b, base, i2i


def test_clean_prompt_strips_lora_tags():
    assert clean_prompt("a girl <lora:foo:0.8>, masterpiece") == "a girl, masterpiece"
    assert clean_prompt("plain prompt") == "plain prompt"


def test_registry_loads_illustrij():
    reg = ModelRegistry.load(HERE / "models.yaml")
    assert reg.get("illustrij")["repo"] == "John6666/illustrij-v50-sdxl"
    with pytest.raises(KeyError):
        reg.get("nope")


def test_cache_dir_sets_hf_home(monkeypatch):
    monkeypatch.delenv("HF_HOME", raising=False)
    DiffusersBackend(model="illustrij", cache_dir="/tmp/hf-test")
    assert os.environ["HF_HOME"] == "/tmp/hf-test"


def test_diffusers_caps_are_local_and_uncensored():
    c = DiffusersBackend(model="illustrij").capabilities()
    assert c.uncensored is True and c.supports_lora and c.supports_edit
    assert c.supports_reference_images is False                 # no IP-Adapter configured
    assert "illustrij" in c.notes


def test_diffusers_generate_uses_model_defaults(diff):
    b, base, _ = diff
    r = b.generate(GenRequest(prompt="yuri <lora:x:1>", width=832, height=1216, seed=3))
    call = base.calls[-1]
    assert call["prompt"] == "yuri"                             # lora tag stripped
    assert call["num_inference_steps"] == 25 and call["guidance_scale"] == 7.0  # illustrij defaults
    assert call["generator"] == "gen3"
    assert _png_size(r.data) == (832, 1216)
    assert r.meta["repo"] == "John6666/illustrij-v50-sdxl"


def test_diffusers_request_overrides_defaults(diff):
    b, base, _ = diff
    b.generate(GenRequest(prompt="x", steps=12, cfg=8.5))
    assert base.calls[-1]["num_inference_steps"] == 12
    assert base.calls[-1]["guidance_scale"] == 8.5


def test_ip_adapter_engaged_only_with_refs_and_config(diff, tmp_path, monkeypatch):
    b, base, _ = diff
    ref = tmp_path / "r.png"; Image.new("RGB", (64, 64)).save(ref)
    # No ip_adapter configured -> refs ignored.
    b.generate(GenRequest(prompt="x", reference_images=[ref]))
    assert "ip_adapter_image" not in base.calls[-1]
    # Configure IP-Adapter -> refs drive identity.
    b.ip_adapter = {"repo": "h94/IP-Adapter", "weight_name": "w.bin", "scale": 0.6}
    b.generate(GenRequest(prompt="x", reference_images=[ref]))
    assert base.ip_loaded and base.ip_scale == 0.6
    assert len(base.calls[-1]["ip_adapter_image"]) == 1


def test_diffusers_edit_is_img2img(diff, tmp_path):
    b, base, i2i = diff
    src = tmp_path / "s.png"; Image.new("RGB", (832, 1216)).save(src)
    r = b.edit(EditRequest(image=src, instruction="her in a red dress", strength=0.55, seed=9))
    call = i2i.calls[-1]
    assert call["strength"] == 0.55 and call["prompt"] == "her in a red dress"
    assert call["image"].size == (832, 1216)
    assert _png_size(r.data) == (832, 1216)
    assert "img2img" in r.meta["model"]


def test_diffusers_edit_uses_ip_adapter_for_identity(diff, tmp_path):
    b, base, i2i = diff
    b.ip_adapter = {"repo": "h94/IP-Adapter", "weight_name": "w.bin", "scale": 0.7}
    src = tmp_path / "s.png"; Image.new("RGB", (256, 256)).save(src)
    ref = tmp_path / "r.png"; Image.new("RGB", (64, 64)).save(ref)
    b.edit(EditRequest(image=src, instruction="x", reference_images=[ref]))
    assert base.ip_loaded                                       # adapter loaded on the base pipe
    assert "ip_adapter_image" in i2i.calls[-1]


def test_diffusers_health_false_without_torch(monkeypatch):
    b = DiffusersBackend(model="illustrij")

    def boom():
        raise ImportError("no torch")

    monkeypatch.setattr(b, "_torch", boom)
    assert b.health() is False


# ---- face detailer (ADetailer-style small-face fix) ----

def _enable_detailer(b, boxes, **opts):
    """Turn the detailer on and stub the detector to return fixed boxes (no GPU/net).
    boxes are [x1, y1, x2, y2, score] rows."""
    import numpy as np
    b.face_detailer = DiffusersBackend._resolve_face_detailer({"enabled": True, **opts})
    b._face_det = _types.SimpleNamespace(
        detect_faces=lambda img, conf_threshold=0.7: np.array(boxes, dtype="float32"))


def test_face_detailer_resolves_defaults_and_disables():
    assert DiffusersBackend._resolve_face_detailer(None) is None
    assert DiffusersBackend._resolve_face_detailer({"enabled": False}) is None
    fd = DiffusersBackend._resolve_face_detailer({"enabled": True, "strength": 0.6})
    assert fd["strength"] == 0.6                          # override honoured
    assert fd["max_face_ratio"] == 0.35 and fd["size"] == 1024   # defaults filled


def test_face_detailer_redraws_small_face(diff):
    b, base, i2i = diff
    # ~100px face in an 832x1216 frame → 0.08 of height, well under max_face_ratio.
    _enable_detailer(b, [[400, 120, 500, 220, 0.99]])
    r = b.generate(GenRequest(prompt="x", width=832, height=1216, seed=1))
    assert r.meta["faces_detailed"] == 1
    redraw = i2i.calls[-1]                                # the crop was redrawn img2img
    assert redraw["image"].size == (1024, 1024)          # at the working resolution
    assert redraw["strength"] == 0.45


def test_face_detailer_skips_large_face(diff):
    b, base, i2i = diff
    # A face filling most of the frame already has enough pixels — leave it.
    _enable_detailer(b, [[100, 100, 800, 1100, 0.99]])
    r = b.generate(GenRequest(prompt="x", width=832, height=1216, seed=1))
    assert r.meta["faces_detailed"] == 0
    assert i2i.calls == []                                # no redraw ran


def test_face_detailer_noop_when_no_faces(diff):
    b, base, i2i = diff
    _enable_detailer(b, [])                               # detector finds nothing
    r = b.generate(GenRequest(prompt="x", width=832, height=1216, seed=1))
    assert r.meta["faces_detailed"] == 0 and i2i.calls == []


# ---- hi-res fix (whole-image upscale + refine) ----

def test_hires_fix_resolves_and_disables():
    assert DiffusersBackend._resolve_hires_fix(None) is None
    assert DiffusersBackend._resolve_hires_fix({"enabled": False}) is None
    hf = DiffusersBackend._resolve_hires_fix({"enabled": True, "scale": 2.0})
    assert hf["scale"] == 2.0 and hf["strength"] == 0.4


def test_hires_fix_upscales_and_refines(diff):
    b, base, i2i = diff
    b.hires_fix = DiffusersBackend._resolve_hires_fix({"enabled": True, "scale": 1.5})
    r = b.generate(GenRequest(prompt="x", width=832, height=1216, seed=1))
    refine = i2i.calls[-1]                                # the second pass ran img2img
    assert refine["image"].size == (1248, 1824)          # 832x1216 × 1.5, 8-aligned
    assert refine["strength"] == 0.4
    assert r.meta["hires"] == "1248x1824"
    assert r.meta["width"] == 1248 and r.meta["height"] == 1824   # final dims recorded
    assert _png_size(r.data) == (1248, 1824)
