# ComfyUI Workflows

A collection of ComfyUI workflows for AI-generated room/space transformation and video generation.

---

## Room Transformation Pipeline

A two-stage pipeline. Stage 1 generates 7 progressive images of a space being furnished. Stage 2 takes those images and renders each consecutive pair into a short video clip, producing a smooth transformation from empty room to fully furnished.

---

### Stage 1 — FLF2V_Image.json

Generates 7 images of the same space, each building on the previous by adding new elements as described in the green prompt nodes on the left side of the canvas.

**The 7 stages (bathroom example included in workflow):**
1. Empty room — bare walls, travertine floor, frosted window
2. Freestanding matte white oval soaking bathtub added
3. Oak vanity with undermount basin and brass tap added
4. Brass wall sconces and pendant light added
5. Round brass mirror, linen towels, bath mat added
6. Ceramic tray, pothos plant, apothecary bottles added
7. Frameless glass shower panel with rain shower head added

**Output:** Images auto-save to `ComfyUI/output/VidGen/`
- Frame 1 → `VidGen/Frame-1`
- Frames 2–7 → `VidGen/Frame-2` through `Frame-7`

**Models required:**
- `flux-2-klein-4b.safetensors` — diffusion model (fp8_e4m3fn)
- `qwen_3_4b.safetensors` — CLIP
- `flux2-vae.safetensors` — VAE

**Settings:** 720×1280, 6 steps, CFG 1.0, Euler sampler

---

### Stage 2 — FLF2V_Video.json

Takes the 7 images from Stage 1 and generates 7 video clips:
- Clips 1–6: animated transition between consecutive image pairs (1→2, 2→3, 3→4, 4→5, 5→6, 6→7)
- Clip 7 (7-end): no end image — just animates the final frame freely based on the prompt

Each clip has its own positive prompt describing what happens in that transition, and a shared negative prompt blocking camera shake, flickering, hands, watermarks etc.

**Reads images from:** `./output/VidGen/` (auto-populated by Stage 1)

**Output:** 7 video files saved as `Video-1-2`, `Video-2-3` ... `Video-7-end` in h264/yuv420p

**Models required:**
- `wan2.1_vace_14B_fp8_scaled.safetensors` — main diffusion model
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors` — CLIP (WAN)
- `pig_wan_vae_fp32-f16.gguf` — VAE
- `Wan21_CausVid_14B_T2V_lora_rank32_v2.safetensors` — LoRA (end clip)
- `Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors` — LoRA (transition clips)

**Settings:** 832×480, 81 frames (≈3s at 24fps), 8 steps (end) / 4 steps (transitions), CFG 1.0, DPM++ 2M sampler, Beta scheduler

---

## How to use

1. Install all required models into your ComfyUI models folders
2. Run **Stage 1** — drag `FLF2V_Image.json` onto the ComfyUI canvas, edit the green prompt nodes for your space, hit Run
3. Check `ComfyUI/output/VidGen/` — you should have 7 images
4. Run **Stage 2** — drag `FLF2V_Video.json` onto the canvas, hit Run
5. 7 video clips will be saved, one per transition

---

## Requirements

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI-Inspire-Pack](https://github.com/ltdrdata/ComfyUI-Inspire-Pack) — for LoadImageListFromDir node
- ROCm or CUDA GPU (workflows use ROCmDiffusionLoader — swap for UNETLoader on NVIDIA)
- 16GB+ VRAM recommended for Stage 2 (WAN 14B model)
- Tested on AMD RX 7900 XTX