import type { VRM } from '@pixiv/three-vrm'

// Spec §5.2 — emotion blendshape state machine with smooth eased blending.
// Port of packages/stage-ui-three/src/composables/vrm/expression.ts (useVRMEmote).

interface EmotionState {
  expression: { name: string, value: number }[]
  blendDuration: number
}

const lerp = (a: number, b: number, t: number) => a + (b - a) * t
const easeInOutCubic = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2)
const clamp01 = (v: number) => Math.min(1, Math.max(0, v))

// Values are deliberately < 1.0 to avoid an over-expressive face (spec §5.2).
const EMOTIONS = new Map<string, EmotionState>([
  ['happy', { expression: [{ name: 'happy', value: 0.7 }, { name: 'aa', value: 0.2 }], blendDuration: 0.4 }],
  ['sad', { expression: [{ name: 'sad', value: 0.7 }, { name: 'oh', value: 0.15 }], blendDuration: 0.4 }],
  ['angry', { expression: [{ name: 'angry', value: 0.7 }, { name: 'ee', value: 0.3 }], blendDuration: 0.3 }],
  ['surprised', { expression: [{ name: 'surprised', value: 0.8 }, { name: 'oh', value: 0.4 }], blendDuration: 0.15 }],
  ['neutral', { expression: [{ name: 'neutral', value: 1.0 }], blendDuration: 0.6 }],
  ['relaxed', { expression: [{ name: 'relaxed', value: 0.75 }], blendDuration: 0.5 }],
])

export class EmoteController {
  private current: string | null = null
  private transitioning = false
  private progress = 0
  private start = new Map<string, number>()
  private target = new Map<string, number>()
  private resetTimer: ReturnType<typeof setTimeout> | undefined

  constructor(private vrm: VRM) {}

  /** Apply an emotion. When `resetAfterMs` is set, return to neutral afterwards. */
  setEmotion(name: string, intensity = 1, resetAfterMs?: number): void {
    if (this.resetTimer) {
      clearTimeout(this.resetTimer)
      this.resetTimer = undefined
    }

    const state = EMOTIONS.get(name)
    if (!state) {
      console.warn(`[EmoteController] unknown emotion: ${name}`)
      return
    }

    this.current = name
    this.transitioning = true
    this.progress = 0
    this.start.clear()
    this.target.clear()

    const k = clamp01(intensity)
    const mgr = this.vrm.expressionManager
    if (mgr) {
      // Start the lerp from the actual displayed values (avoids snap-to-zero).
      for (const exprName of Object.keys(mgr.expressionMap)) {
        this.start.set(exprName, mgr.getValue(exprName) ?? 0)
        this.target.set(exprName, 0)
      }
    }
    for (const e of state.expression)
      this.target.set(e.name, e.value * k)

    if (resetAfterMs && name !== 'neutral')
      this.resetTimer = setTimeout(() => this.setEmotion('neutral'), resetAfterMs)
  }

  /** Per-frame (spec §4 step 8). Only stages values; expressionManager.update() commits. */
  update(delta: number): void {
    if (!this.transitioning || !this.current)
      return
    const state = EMOTIONS.get(this.current)!
    this.progress += delta / state.blendDuration
    if (this.progress >= 1) {
      this.progress = 1
      this.transitioning = false
    }
    const eased = easeInOutCubic(this.progress)
    const mgr = this.vrm.expressionManager
    if (!mgr)
      return
    for (const [name, tgt] of this.target)
      mgr.setValue(name, lerp(this.start.get(name) ?? 0, tgt, eased))
  }
}

export const KNOWN_EMOTIONS = [...EMOTIONS.keys()]
