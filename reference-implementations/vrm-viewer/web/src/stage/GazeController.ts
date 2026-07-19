import type { VRM } from '@pixiv/three-vrm'
import type { PerspectiveCamera } from 'three'

import { Object3D, Vector3 } from 'three'

import type { TrackingMode, Vec3 } from './types'

// Spec §5.5 — gaze / look-at with idle saccades.
// modes: 'camera' (eye contact), 'fixed' (explicit world target), 'none' (straight ahead).
export class GazeController {
  private mode: TrackingMode = 'camera'
  private readonly fixation = new Vector3()
  private readonly desired = new Vector3()
  private targetNode: Object3D | undefined
  private sinceSaccade = 0
  private nextSaccadeAt = 0

  constructor(private camera: PerspectiveCamera, private eyeHeight: number) {
    this.fixation.set(0, eyeHeight, -1)
  }

  setMode(mode: TrackingMode): void {
    this.mode = mode
  }

  setFixedTarget(t: Vec3): void {
    this.mode = 'fixed'
    this.fixation.set(t.x, t.y, t.z)
  }

  setEyeHeight(y: number): void {
    this.eyeHeight = y
  }

  update(vrm: VRM, delta: number): void {
    if (!vrm.lookAt)
      return

    if (!this.targetNode) {
      this.targetNode = new Object3D()
      vrm.lookAt.target = this.targetNode as unknown as Object3D
    }

    if (this.mode === 'camera')
      this.camera.getWorldPosition(this.desired)
    else if (this.mode === 'none')
      this.desired.set(0, this.eyeHeight, -100)
    else
      this.desired.copy(this.fixation)

    // Idle saccades: small random jitter at random intervals (spec §5.5).
    this.sinceSaccade += delta
    if (this.sinceSaccade >= this.nextSaccadeAt) {
      this.sinceSaccade = 0
      this.nextSaccadeAt = (Math.random() * 2 + 0.4) // 0.4–2.4s
      this.desired.x += (Math.random() - 0.5) * 0.25
      this.desired.y += (Math.random() - 0.5) * 0.25
    }

    // Smoothly approach the desired point, then let VRM apply it.
    this.targetNode.position.lerp(this.desired, 0.25)
    vrm.lookAt.update(delta)
  }
}
