# ComFlameUI ZDepth

An Autodesk Pybox handler integrating ComfyUI ZDepth Marigold and Depth Anything workflows

## Inputs

- `Front` input to ComfyUI EXR loader
  - The image coming from Flame batch upstream node

Input images are written on the ComfyUI server disk
`<COMFYUI_SERVER_MOUNTING>/in/<FLAME_PROJECT>/zdepth_marigold/` or

`<COMFYUI_SERVER_MOUNTING>/in/<FLAME_PROJECT>/zdepth_depth_anything/`

## Outputs

- `Result` output from ComfyUI EXR Saver
  - The black & white depth map of the source image
  

Output images are read on the ComfyUI server disk
`<COMFYUI_SERVER_MOUNTING>/out/<FLAME_PROJECT>/zdepth_marigold/` or

`<COMFYUI_SERVER_MOUNTING>/out/<FLAME_PROJECT>/zdepth_depth_anything/`
