import type { VRM } from '@pixiv/three-vrm'

// Spec §5.3 — procedural blink. Random interval 1–6s, single blink 0.2s,
// weight follows sin(pi * progress). Independent of emotion/lipsync.
export class Blink {
  private readonly DURATION = 0.2
  private readonly MIN = 1
  private readonly MAX = 6
  private blinking = false
  private progress = 0
  private sinceLast = 0
  private nextAt = Math.random() * (this.MAX - this.MIN) + this.MIN

  update(vrm: VRM, delta: number): void {
    const mgr = vrm.expressionManager
    if (!mgr)
      return

    this.sinceLast += delta
    if (!this.blinking && this.sinceLast >= this.nextAt) {
      this.blinking = true
      this.progress = 0
    }
    if (!this.blinking)
      return

    this.progress += delta / this.DURATION
    mgr.setValue('blink', Math.sin(Math.PI * this.progress))

    if (this.progress >= 1) {
      this.blinking = false
      this.sinceLast = 0
      mgr.setValue('blink', 0)
      this.nextAt = Math.random() * (this.MAX - this.MIN) + this.MIN
    }
  }
}
