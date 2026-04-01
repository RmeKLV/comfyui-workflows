# ComfyUI Workflows

A collection of ComfyUI workflows for AI-generated room transformation and video generation.

---

## Room Transformation Pipeline

A two-stage pipeline that takes an empty room and progressively furnishes it across 7 images, then renders those images into a smooth transition video.

### Stage 1 — FLF2V_Image

Generates 7 images of the same room, each building on the previous by adding new elements as described in the green prompt nodes on the left side of the canvas.

**The 7 stages (bathroom example):**
1. Empty room — bare walls, travertine floor, frosted window
2. Adds a freestanding matte white oval soaking bathtub
3. Adds a solid oak vanity with undermount basin and brass tap
4. Adds brass wall sconces and a pendant light
5. Adds a round brass mirror, linen towels, and a bath mat
6. Adds a ceramic tray, pothos plant, and glass apothecary bottles
7. Adds a frameless glass shower panel with rain shower head

**Output:** Images auto-save to a new VidGen/ folder in your ComfyUI output directory.
Frame 1 → VidGen/Frame-1, frames 2–7 → VidGen/Frame-2 through Frame-7.

**Models required:**
- flux-2-klein-4b.safetensors (diffusion, fp8_e4m3fn)
- qwen_3_4b.safetensors (CLIP)
- flux2-vae.safetensors (VAE)

**Settings:** 720x1280, 6 steps, CFG 1.0, Euler sampler

### Stage 2 — FLF2V_Video

*(workflow file coming soon)*

Takes the 7 images from Stage 1 and generates a smooth transition video using FLF2V.

---

## How to use

1. Install required models into your ComfyUI models folder
2. Open FLF2V_Image.json in ComfyUI (drag and drop onto the canvas)
3. Edit the green text nodes on the left to describe your room stages
4. Hit Run — images save to ComfyUI/output/VidGen/
5. Once Stage 2 is uploaded: open FLF2V_Video.json, point it at the VidGen folder, run to generate video

---

## Requirements

- ComfyUI (https://github.com/comfyanonymous/ComfyUI)
- ROCm or CUDA GPU (workflow uses ROCmDiffusionLoader — swap for UNETLoader on NVIDIA)
- 12GB+ VRAM recommended (tested on AMD RX 7900 XTX)
