// Control command protocol shared between the Python bridge and the viewer.
// Python sends these as JSON over the WebSocket; ControlBridge dispatches them
// onto the VrmStage. Keep this in sync with server/vrm_control/controller.py.

export interface Vec3 { x: number, y: number, z: number }

export type TrackingMode = 'camera' | 'none' | 'fixed'

export type Command
  = | { type: 'expression', name: string, intensity?: number }
    | { type: 'expression_raw', values: Record<string, number> }
    | { type: 'look_at', mode: 'camera' | 'none' }
    | { type: 'look_at', target: Vec3 }
    | { type: 'bone', name: string, euler: Vec3 }
    | { type: 'bone_reset', name?: string }
    | { type: 'mouth', value: number }
    | { type: 'material_color', material: string, color: string }
    | { type: 'animation', url: string, loop?: boolean, fadeIn?: number }
    | { type: 'load_model', url: string }
