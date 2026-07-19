import type { VRM } from '@pixiv/three-vrm'

import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm'
import { VRMAnimationLoaderPlugin, VRMLookAtQuaternionProxy } from '@pixiv/three-vrm-animation'
import { Box3, Group, Quaternion, Vector3 } from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

// Spec §3.1 — one process-wide GLTFLoader registered with the VRM plugins so the
// same loader parses both .vrm models and .vrma animation files.
let loader: GLTFLoader | undefined

export function getLoader(): GLTFLoader {
  if (loader)
    return loader

  loader = new GLTFLoader()
  loader.crossOrigin = 'anonymous'
  loader.register(parser => new VRMLoaderPlugin(parser))
  loader.register(parser => new VRMAnimationLoaderPlugin(parser))
  return loader
}

export interface LoadedVrm {
  vrm: VRM
  /** Transform handle the app moves/rotates; the avatar scene stays at local origin. */
  group: Group
  modelSize: Vector3
  modelCenter: Vector3
  /** World Y of the head bone — used to seat the camera and the default gaze target. */
  eyeHeight: number
}

// Spec §3.2 — load a VRM, run the mandatory perf/normalization passes, and frame it.
export async function loadVrm(
  url: string,
  onProgress?: (ratio: number) => void,
): Promise<LoadedVrm> {
  const gltf = await getLoader().loadAsync(url, (e) => {
    if (onProgress && e.total)
      onProgress(e.loaded / e.total)
  })

  const vrm = gltf.userData.vrm as VRM | undefined
  if (!vrm)
    throw new Error(`File is not a VRM: ${url}`)

  // Big FPS wins — see spec §3.2 step 2.
  VRMUtils.removeUnnecessaryVertices(vrm.scene)
  VRMUtils.combineSkeletons(vrm.scene)

  // Avatar parts must never get culled at the frame edge.
  vrm.scene.traverse((o) => { o.frustumCulled = false })

  // Required for look-at to be drivable; harmless when lookAt is absent.
  if (vrm.lookAt) {
    const proxy = new VRMLookAtQuaternionProxy(vrm.lookAt)
    proxy.name = 'lookAtQuaternionProxy'
    vrm.scene.add(proxy)
  }

  const group = new Group()
  group.add(vrm.scene)

  // Normalize facing so the avatar's faceFront aligns with world -Z (spec §3.2 step 6).
  if (vrm.lookAt) {
    const target = new Vector3(0, 0, -1)
    const q = new Quaternion().setFromUnitVectors(vrm.lookAt.faceFront.clone().normalize(), target)
    group.quaternion.premultiply(q)
  }

  vrm.springBoneManager?.reset()
  group.updateMatrixWorld(true)

  // Bounding box (skip spring-bone colliders) for camera framing.
  const box = new Box3()
  const childBox = new Box3()
  vrm.scene.traverse((obj) => {
    const mesh = obj as unknown as { isMesh?: boolean, name: string, geometry?: { boundingBox: Box3 | null, computeBoundingBox: () => void }, matrixWorld: import('three').Matrix4 }
    if (!mesh.isMesh || !mesh.geometry)
      return
    if (mesh.name.startsWith('VRMC_springBone_collider'))
      return
    if (!mesh.geometry.boundingBox)
      mesh.geometry.computeBoundingBox()
    childBox.copy(mesh.geometry.boundingBox!).applyMatrix4(mesh.matrixWorld)
    box.union(childBox)
  })

  const modelSize = new Vector3()
  const modelCenter = new Vector3()
  box.getSize(modelSize)
  box.getCenter(modelCenter)

  const headNode = vrm.humanoid?.getNormalizedBoneNode('head')
  const eyeHeight = headNode
    ? headNode.getWorldPosition(new Vector3()).y
    : modelCenter.y

  return { vrm, group, modelSize, modelCenter, eyeHeight }
}
