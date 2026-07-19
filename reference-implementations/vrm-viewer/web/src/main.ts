import { ControlBridge } from './bridge/ControlBridge'
import { VrmStage } from './stage/VrmStage'

const MODEL_URL = '/models/avatar.vrm'
const IDLE_URL = '/models/idle.vrma'
const BRIDGE_URL = `ws://${location.hostname}:8765`

const app = document.getElementById('app')!
const statusEl = document.getElementById('status')!

let bridgeConnected = false
let modelStatus = 'loading model…'

function renderStatus(): void {
  const dot = (on: boolean) => `<span class="dot ${on ? 'on' : 'off'}"></span>`
  statusEl.innerHTML = [
    `${dot(modelStatus === 'ready')}${modelStatus}`,
    `${dot(bridgeConnected)}python bridge: ${bridgeConnected ? 'connected' : `waiting (${BRIDGE_URL})`}`,
  ].join('\n')
}

async function main(): Promise<void> {
  const stage = new VrmStage(app)
  stage.start()
  renderStatus()

  try {
    await stage.loadModel(MODEL_URL, (r) => {
      modelStatus = `loading model… ${Math.round(r * 100)}%`
      renderStatus()
    })
    await stage.playAnimation(IDLE_URL, true)
    modelStatus = 'ready'
    renderStatus()
  }
  catch (err) {
    modelStatus = `model error: ${String(err)}`
    renderStatus()
    console.error(err)
  }

  const bridge = new ControlBridge(BRIDGE_URL, stage, (connected) => {
    bridgeConnected = connected
    renderStatus()
  })
  bridge.connect()

  // Expose for manual poking from the browser console.
  ;(window as unknown as { stage: VrmStage }).stage = stage
}

void main()
