import type { VrmStage } from '../stage/VrmStage'
import type { Command } from '../stage/types'

// Spec §6 — control input seam. The Python bridge is the WebSocket *server*;
// this viewer is a client that auto-reconnects and dispatches commands onto the stage.
export class ControlBridge {
  private ws: WebSocket | undefined
  private reconnectTimer: ReturnType<typeof setTimeout> | undefined

  constructor(
    private url: string,
    private stage: VrmStage,
    private onStatus?: (connected: boolean) => void,
  ) {}

  connect(): void {
    try {
      this.ws = new WebSocket(this.url)
    }
    catch {
      this.scheduleReconnect()
      return
    }

    this.ws.addEventListener('open', () => {
      this.onStatus?.(true)
      this.ws?.send(JSON.stringify({ type: 'hello', role: 'viewer' }))
    })

    this.ws.addEventListener('message', (ev) => {
      let cmd: Command
      try {
        cmd = JSON.parse(ev.data as string)
      }
      catch {
        console.warn('[ControlBridge] bad JSON:', ev.data)
        return
      }
      this.dispatch(cmd)
    })

    this.ws.addEventListener('close', () => {
      this.onStatus?.(false)
      this.scheduleReconnect()
    })
    this.ws.addEventListener('error', () => this.ws?.close())
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer)
      return
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = undefined
      this.connect()
    }, 1000)
  }

  private dispatch(cmd: Command): void {
    switch (cmd.type) {
      case 'expression':
        this.stage.setExpression(cmd.name, cmd.intensity ?? 1)
        break
      case 'expression_raw':
        this.stage.setExpressionRaw(cmd.values)
        break
      case 'look_at':
        if ('mode' in cmd)
          this.stage.lookAtMode(cmd.mode)
        else
          this.stage.lookAtTarget(cmd.target)
        break
      case 'bone':
        this.stage.setBone(cmd.name, cmd.euler)
        break
      case 'bone_reset':
        this.stage.resetBone(cmd.name)
        break
      case 'mouth':
        this.stage.setMouth(cmd.value)
        break
      case 'material_color':
        this.stage.setMaterialColor(cmd.material, cmd.color)
        break
      case 'animation':
        void this.stage.playAnimation(cmd.url, cmd.loop ?? true, cmd.fadeIn ?? 0.3)
        break
      case 'load_model':
        void this.stage.loadModel(cmd.url)
        break
      default:
        console.warn('[ControlBridge] unknown command:', cmd)
    }
  }
}
