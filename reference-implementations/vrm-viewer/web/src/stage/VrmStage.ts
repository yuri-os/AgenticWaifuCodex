import type { VRM } from '@pixiv/three-vrm'
import type { Group } from 'three'

import { createVRMAnimationClip } from '@pixiv/three-vrm-animation'
import {
  ACESFilmicToneMapping,
  AmbientLight,
  AnimationMixer,
  DirectionalLight,
  Euler,
  HemisphereLight,
  LoopOnce,
  LoopRepeat,
  MathUtils,
  PerspectiveCamera,
  Quaternion,
  Scene,
  Vector3,
  VectorKeyframeTrack,
  WebGLRenderer,
} from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

import type { Vec3 } from './types'

import { Blink } from './Blink'
import { EmoteController } from './EmoteController'
import { GazeController } from './GazeController'
import { getLoader, loadVrm } from './VrmLoader'

// A humanoid bone name accepted by `setBone` / `resetBone`.
type HumanoidBoneName = Parameters<NonNullable<VRM['humanoid']>['getNormalizedBoneNode']>[0]

interface UpdatableMaterial { update?: (delta: number) => void }

// Spec §8 — the standalone "VrmStage": owns the renderer/scene/camera and runs the
// manual per-frame update loop in the exact order of spec §4.
export class VrmStage {
  readonly scene = new Scene()
  readonly camera: PerspectiveCamera
  readonly renderer: WebGLRenderer
  private readonly controls: OrbitControls

  private vrm: VRM | undefined
  private group: Group | undefined
  private mixer: AnimationMixer | undefined
  private emote: EmoteController | undefined
  private readonly blink = new Blink()
  private gaze: GazeController | undefined

  // Channel: direct bone overrides (spec §5.6 seam — generic pose input).
  // Applied after the animation mixer, before humanoid.update().
  private readonly boneOverrides = new Map<HumanoidBoneName, Quaternion>()
  // Channel: simple mouth-open value (lip-sync substitute for an audio-less bridge).
  private mouth = 0
  // Persistent appearance state. Re-applied every time a model finishes loading, so a
  // recolor requested before/around load (common race: the bridge connects before the
  // .vrm finishes downloading) is not lost.
  private readonly materialColors = new Map<string, string>()

  private lastTime = performance.now()
  private running = false

  constructor(container: HTMLElement) {
    this.renderer = new WebGLRenderer({ antialias: true, alpha: true })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.setSize(container.clientWidth, container.clientHeight)
    this.renderer.toneMapping = ACESFilmicToneMapping
    container.appendChild(this.renderer.domElement)

    this.camera = new PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 100)
    this.camera.position.set(0, 1.3, -1.6)

    this.controls = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls.target.set(0, 1.2, 0)
    this.controls.enableDamping = true

    // Lighting (spec §5.7) — hemisphere + ambient + directional.
    this.scene.add(new HemisphereLight(0xFFFFFF, 0x222222, 0.6))
    const ambient = new AmbientLight(0xFFFFFF, 0.6)
    this.scene.add(ambient)
    const dir = new DirectionalLight(0xFFFBF5, 2.0)
    dir.position.set(0, 1, -1)
    this.scene.add(dir)

    window.addEventListener('resize', () => this.onResize(container))
  }

  private onResize(container: HTMLElement): void {
    this.camera.aspect = container.clientWidth / container.clientHeight
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(container.clientWidth, container.clientHeight)
  }

  async loadModel(url: string, onProgress?: (r: number) => void): Promise<void> {
    const loaded = await loadVrm(url, onProgress)

    // Tear down any previous model.
    if (this.group) {
      this.scene.remove(this.group)
      this.mixer?.stopAllAction()
    }

    this.vrm = loaded.vrm
    this.group = loaded.group
    this.scene.add(loaded.group)

    this.emote = new EmoteController(loaded.vrm)
    this.gaze = new GazeController(this.camera, loaded.eyeHeight)
    this.mixer = new AnimationMixer(loaded.vrm.scene)
    this.boneOverrides.clear()
    this.mouth = 0

    // Re-apply any persistent appearance state requested before this model was ready.
    for (const [name, hex] of this.materialColors)
      this.applyMaterialColor(name, hex)

    // Frame the camera on the upper body.
    const headY = loaded.eyeHeight || loaded.modelCenter.y
    this.camera.position.set(0, headY, -loaded.modelSize.y * 0.55)
    this.controls.target.set(0, headY - loaded.modelSize.y * 0.12, 0)
    this.controls.update()
  }

  // Spec §5.1 — load a .vrma, retarget to the current VRM, re-anchor hips, play (looped).
  async playAnimation(url: string, loop = true, fadeIn = 0.3): Promise<void> {
    if (!this.vrm || !this.mixer)
      throw new Error('No model loaded')

    const gltf = await getLoader().loadAsync(url)
    const vrmAnimation = gltf.userData.vrmAnimations?.[0]
    if (!vrmAnimation)
      throw new Error(`No VRM animation in ${url}`)

    const clip = createVRMAnimationClip(vrmAnimation, this.vrm)
    this.reAnchorHips(clip)

    const action = this.mixer.clipAction(clip)
    action.setLoop(loop ? LoopRepeat : LoopOnce, Infinity)
    action.clampWhenFinished = !loop
    this.mixer.stopAllAction()
    action.reset().fadeIn(fadeIn).play()
  }

  // Spec §5.1 step 3 — prevent the avatar teleporting to the animator's origin.
  private reAnchorHips(clip: import('three').AnimationClip): void {
    const hips = this.vrm?.humanoid?.getNormalizedBoneNode('hips')
    if (!hips)
      return
    hips.updateMatrixWorld(true)
    const restHip = hips.getWorldPosition(new Vector3())
    const track = clip.tracks.find(t => t instanceof VectorKeyframeTrack && t.name === `${hips.name}.position`) as VectorKeyframeTrack | undefined
    if (!track)
      return
    const animHip = new Vector3(track.values[0], track.values[1], track.values[2])
    const d = animHip.sub(restHip)
    for (const t of clip.tracks) {
      if (t.name.endsWith('.position') && t instanceof VectorKeyframeTrack) {
        for (let i = 0; i < t.values.length; i += 3) {
          t.values[i] -= d.x
          t.values[i + 1] -= d.y
          t.values[i + 2] -= d.z
        }
      }
    }
  }

  // ---- Control surface (called by the WebSocket bridge) ----

  setExpression(name: string, intensity = 1): void {
    this.emote?.setEmotion(name, intensity, 3000)
  }

  setExpressionRaw(values: Record<string, number>): void {
    const mgr = this.vrm?.expressionManager
    if (!mgr)
      return
    for (const [k, v] of Object.entries(values))
      mgr.setValue(k, v)
  }

  lookAtMode(mode: 'camera' | 'none'): void {
    this.gaze?.setMode(mode)
  }

  lookAtTarget(t: Vec3): void {
    this.gaze?.setFixedTarget(t)
  }

  setMouth(value: number): void {
    this.mouth = Math.min(1, Math.max(0, value))
  }

  // Tint a material by name (e.g. "Tops_01_CLOTH"). The texture is multiplied by this
  // color, so a near-white VRoid texture takes the tint cleanly. Both the lit color and
  // the MToon shade color are set so the shaded side matches. The request is remembered
  // and re-applied on every subsequent model load.
  setMaterialColor(name: string, hex: string): void {
    this.materialColors.set(name, hex)
    if (!this.vrm)
      return // applied when the model finishes loading
    const found = this.applyMaterialColor(name, hex)
    if (!found)
      console.warn(`[VrmStage] material not found: ${name} (have: ${this.materialNames().join(', ')})`)
  }

  private applyMaterialColor(name: string, hex: string): number {
    const vrm = this.vrm
    if (!vrm)
      return 0

    let found = 0
    const apply = (mat: unknown): void => {
      const m = mat as {
        name?: string
        color?: { set: (h: string) => void }
        shadeColorFactor?: { set: (h: string) => void }
      }
      if (!m || m.name !== name)
        return
      m.color?.set(hex)
      m.shadeColorFactor?.set(hex)
      found++
    }

    vrm.materials?.forEach(apply)
    if (!found) {
      vrm.scene.traverse((o) => {
        const mm = (o as { material?: unknown }).material
        if (Array.isArray(mm))
          mm.forEach(apply)
        else
          apply(mm)
      })
    }
    return found
  }

  /** Names of the loaded model's materials (for discovery from the console). */
  materialNames(): string[] {
    return (this.vrm?.materials ?? []).map(m => (m as { name?: string }).name ?? '').filter(Boolean)
  }

  // Set a humanoid bone's local rotation from Euler degrees. Generic pose seam (spec §5.6):
  // Python computes whatever rotation it wants and pushes it here each tick.
  setBone(name: string, euler: Vec3): void {
    if (!this.vrm?.humanoid?.getNormalizedBoneNode(name as HumanoidBoneName)) {
      console.warn(`[VrmStage] unknown bone: ${name}`)
      return
    }
    const q = new Quaternion().setFromEuler(new Euler(
      MathUtils.degToRad(euler.x),
      MathUtils.degToRad(euler.y),
      MathUtils.degToRad(euler.z),
      'XYZ',
    ))
    this.boneOverrides.set(name as HumanoidBoneName, q)
  }

  resetBone(name?: string): void {
    if (name)
      this.boneOverrides.delete(name as HumanoidBoneName)
    else
      this.boneOverrides.clear()
  }

  // ---- Render loop (spec §4) ----

  start(): void {
    if (this.running)
      return
    this.running = true
    this.lastTime = performance.now()
    const tick = () => {
      if (!this.running)
        return
      const now = performance.now()
      const delta = (now - this.lastTime) / 1000
      this.lastTime = now
      this.update(delta)
      this.renderer.render(this.scene, this.camera)
      requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }

  stop(): void {
    this.running = false
  }

  private update(delta: number): void {
    this.controls.update()

    const vrm = this.vrm
    if (!vrm)
      return

    // 1. body animation clip
    this.mixer?.update(delta)
    // 2. animated material uniforms (MToon/shader)
    vrm.materials?.forEach(m => (m as unknown as UpdatableMaterial).update?.(delta))
    // 4. external pose hook → direct bone overrides (after mixer, before humanoid.update)
    for (const [name, q] of this.boneOverrides) {
      const node = vrm.humanoid?.getNormalizedBoneNode(name)
      if (node)
        node.quaternion.copy(q)
    }
    // 5. flush normalized → raw skeleton
    vrm.humanoid?.update()
    // 6. gaze
    this.gaze?.update(vrm, delta)
    // 7. blink (stages 'blink')
    this.blink.update(vrm, delta)
    // 8. emotion (stages expression weights)
    this.emote?.update(delta)
    // 9. mouth (lip-sync substitute, stages 'aa')
    if (this.mouth > 0.001)
      vrm.expressionManager?.setValue('aa', this.mouth)
    // 10. commit all staged blendshape weights
    vrm.expressionManager?.update()
    // 11. constraints
    vrm.nodeConstraintManager?.update()
    // 12. spring-bone physics (last)
    vrm.springBoneManager?.update(delta)
  }
}
