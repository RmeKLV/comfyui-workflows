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

- ---

## Kokoro TTS & FL-ClearVoice Audio Pipeline

A high-fidelity AI voice generation and super-resolution pipeline. It generates realistic, natural-sounding narration for commentary videos, voiceovers, or podcasts, and automatically upscales the audio to studio-standard resolution.

### Nodes required:
* [ComfyUI-Geeky-Kokoro-TTS](https://github.com/GeekyGhost/ComfyUI-Geeky-Kokoro-TTS) — for voice generation & voice blending
* [ComfyUI_FL-ClearVoice](https://github.com/filliptm/ComfyUI_FL-ClearVoice) — for audio upscaling & neural mastering
* [ComfyUI-Documents](https://github.com/Excidos/ComfyUI-Documents) — for automatic script chunking (optional)

### Setup & Requirements (Windows / AMD Optimized):

1. **The `PosixPath` Windows/Portable Bug Fix:**
   Because Resemble-Enhance config files are built on Linux, you must patch Python's path library to prevent a `NotImplementedError` crash when loading the model on Windows:
   * Open `ComfyUI_windows_portable\ComfyUI\custom_nodes\comfyui_fl-clearvoice\__init__.py` in Notepad.
   * Add this exact line to the **very top** (Line 1):
     ```python
     import pathlib; pathlib.PosixPath = pathlib.Path
     ```
   * Save and close the file.

2. **Resemble-Enhance No-DeepSpeed Windows Workaround:**
   DeepSpeed is designed for Linux and fails to compile natively on Windows. Because DeepSpeed is only used for training and not for running inference, you can safely force-install the model dependencies without it.
   * Open a Command Prompt in your `ComfyUI_windows_portable` root directory and run:
     ```cmd
     .\python_embeded\python.exe -m pip install resemble-enhance --no-deps
     .\python_embeded\python.exe -m pip install celluloid
     ```

### Settings & Punctuation Tips for Realism:
* **Natural Pacing:** AI voices use punctuation as physical breathing cues. 
  * Use semicolons `;` or ellipses `...` for medium/long natural pauses.
  * Use exclamation marks `!` and question marks `?` to dynamically raise voice pitch and inflection.
  * Spell out abbreviations phonetically (e.g., use `A.I.` instead of `AI`) and write out numerical figures.
* **Vocal Quality:**
  * Keep `reverb_room_size` set strictly to `0.00` in the advanced voice node to ensure a dry, close-mic podcast studio feel.
  * Set your `voice_profile` to `Cinematic` or `None` when running `Resemble_Enhance` (avoid `Singer` to prevent auto-tune speech glitches).
  * Use the `Resemble_Enhance` model for warm, full vocal re-synthesis, or `MossFormer2_SR_48K` for completely stable, glitch-free 48kHz upscaling.

Example:
"Hello! ... I am an A.I. voice model; created directly from this workflow... Would you like me... to narrate your next video? ... Let's make; something amazing; today."

### Example Script:

"Hello! ... I am an A.I. voice model; created directly from this workflow... Would you like me... to narrate your next video? ... Let's make; something amazing; today."

### Audio Comparison:

**Before (Raw Kokoro AI Output):**
[Before.mp3](https://github.com/user-attachments/files/28664086/Before.mp3)

**After (FL-ClearVoice Upscaled & Mastered):**
[After.mp3](https://github.com/user-attachments/files/28664088/After.mp3)

---

## Qwen3-TTS Voice Clone & Script Reader (Automated Loop Pipeline)

`QWEN3-TTS Voice Clone & Script Reader.json`

An automated local voiceover pipeline built to clone a speaker's unique physical vocal identity and generate long, continuous scripts. It features a modular, clean canvas layout using a packaged **Factory Subgraph** and an automatic **Script Reader** looping system.

Instead of running parallel test configurations or manually pasting individual text chunks, this workflow dynamically splits entire multiline scripts, calculates your exact paragraph count, and automatically generates sequential audio files using ComfyUI's native batch queue.

### Nodes required:
* [ComfyUI-QWEN3_TTS](https://github.com/crt-nodes/ComfyUI-QWEN3_TTS) — for 1.7B-Base voice cloning & text-to-speech
* [ComfyUI_FL-ClearVoice](https://github.com/filliptm/ComfyUI_FL-ClearVoice) — for audio upscaling & neural mastering
* [ComfyUI-basic-data-handling](https://github.com/TheStableLlama/ComfyUI-basic-data-handling) — for StringSplitlinesList & ListLength nodes
* [qq-nodes-comfyui](https://github.com/nkreipke/qq-nodes-comfyui) — for Any List Iterator & Axis To Any nodes
* [was-node-suite-comfyui](https://github.com/WASasquatch/was-node-suite-comfyui) — for Text Multiline node

*(Note: The `RegexReplace` nodes used in this workflow are built-in ComfyUI core nodes and do not require separate custom installations).*

---

### Setup & Requirements (Windows / AMD Optimized):

Because deep-learning audio libraries often have complex dependencies, follow these steps to prevent crashes on Windows portable builds:

1. **The `PosixPath` Windows/Portable Bug Fix:**
   Because Resemble-Enhance config files are built on Linux, you must patch Python's path library to prevent a `NotImplementedError` crash when loading the model on Windows:
   * Open `ComfyUI_windows_portable\ComfyUI\custom_nodes\comfyui_fl-clearvoice\__init__.py` in Notepad.
   * Add this exact line to the **very top** (Line 1):
     ```python
     import pathlib; pathlib.PosixPath = pathlib.Path
     ```
   * Save and close the file.

2. **Resemble-Enhance No-DeepSpeed Windows Workaround:**
   DeepSpeed is designed for Linux and fails to compile natively on Windows. Because DeepSpeed is only used for training and not for running inference, you can safely force-install the model dependencies without it.
   * Open a Command Prompt in your `ComfyUI_windows_portable` root directory and run:
     ```cmd
     .\python_embeded\python.exe -m pip install resemble-enhance --no-deps
     .\python_embeded\python.exe -m pip install celluloid
     ```

3. **NumPy 2.x Dependency Conflict Fix:**
   Installing some TTS dependencies (like `LangSegment`) may silently force-upgrade your environment's NumPy version to `2.x`. Because other ComfyUI libraries are pre-compiled for NumPy `1.x`, this mismatch will trigger a fatal `access violation` crash inside `pyarrow` or `torchcodec` on launch.
   * If ComfyUI crashes immediately on startup after installing, run this command to force your environment back to the stable standard:
     ```cmd
     .\python_embeded\python.exe -m pip install numpy==1.26.4 --force-reinstall
     ```

---

### The Advanced Serial Audio Chain

The script reading and vocal enhancement pipeline has been optimized into a clean, automated loop featuring on-canvas text sanitization:
[Text Multiline] ➔ [Regex 1 (Newlines)] ➔ [Regex 2 (Spaces)] ➔ [StringSplitlinesList] ➔ [Any List Iterator] ➔ [Factory Subgraph] ➔ [SaveAudio]
▲
[Starting Point]
code
Code
#### 1. The Automated Script Reader & Sanitization Chain
* **`Text Multiline`:** Holds your entire voiceover script.
* **`Replace Text (Regex) 1` (Newline Cleaner):** Automatically sanitizes paragraph gaps by searching for the pattern `\n\s*\n` and replacing it with a single `\n`. This successfully collapses double-enters, carriage returns, and hidden non-breaking space characters (`\xa0`) commonly generated by browser-based editors like Microsoft Word Online, keeping your generated audio free of empty, silent runs [1.2.1, 1.2.2].
* **`Replace Text (Regex) 2` (Space Cleaner):** Automatically sanitizes horizontal spacing anomalies using the pattern `[ \t]+` and replacing it with a single space (` `). This collapses double-space typos or large tab gaps inside the text into standard single spacing.
* **`StringSplitlinesList`:** Automatically parses the fully sanitized text block line-by-line.
* **`ListLength` & `Batch Count` Preview:** Instantly calculates the total number of paragraphs and outputs the value to a dark visual helper on your canvas, showing you exactly how many runs to queue.
* **`PrimitiveInt` ("Starting Point"):** A core ComfyUI node wired directly to the list iterator. You can manually change the value to resume generation from a specific paragraph index, or set it to `0` to start from the beginning.
* **`Any List Iterator` & `Axis To Any`:** Steps through the list index-by-index with each queue run.

#### 2. The Factory Subgraph
To keep the main canvas clean and modular, the generation and upscaling processors are packaged inside a single **New Subgraph ("Factory")** node:
* **`Qwen3TTSVoiceClone`:** Clips are generated using a local `1.7B-Base` model.
* **`FL_ClearVoice_Process` (`MossFormer2_SR_48K`):** Dynamically reconstructs high-frequency details, upscaling the raw, lower-sample-rate cloned speech to stable, broadcast-standard 48kHz audio.

---

### Step-by-Step Looping Instructions

To process long scripts without manual copy-pasting, follow these steps:

1. **Paste your text:** Paste your full script into the **Text Multiline** node.
2. **First Run (Bypass):** 
   * Right-click the **Factory** node and select **Bypass** (or press `Ctrl + B`).
   * Click **Run** on ComfyUI once. This evaluates your text size, sanitizes the spacing, and updates the visual **Batch Count** preview box on your canvas.
3. **Configure your Loop:**
   * Un-bypass the **Factory** node (press `Ctrl + B` again).
   * Reset your **Starting Point** value to `0` in your primitive node.
   * Look at the **Batch Count** preview box. Type that exact number into ComfyUI's native **Batch Count** input box (the input box right next to the blue **`Run`** button on your top-right menu panel).
4. **RUN:** Click **`Run`** (or Queue Prompt). ComfyUI will run exactly the designated amount of times, generating and saving your sequential voiceover files (e.g., `ComfyUI_00001.flac`, `ComfyUI_00002.flac`) to your `output` directory without overwriting.

---

### Cloning & Cross-Lingual Tips

* **Vocal Reference Sweet Spot:** For zero-shot cloning, use a clean **10 to 15-second** reference clip. Record in a quiet room with no background noise or echo. 
* **The `ref_text` Rule:** The top text box inside the cloning node is the reference transcript. It **must** match the exact spoken words inside your reference audio file word-for-word, or the vocal alignment will fail.
* **Cross-Lingual Cloning:** Qwen3-TTS is highly multilingual. If you are not confident in your English pronunciation, **you can record your 10-second reference clip in your native language (e.g., Latvian)**. Put the Latvian transcript in the `ref_text` box, put your English script in the bottom `text` box, and keep the target language set to `English`. The AI will extract your unique vocal characteristics and apply them to perfectly pronounced, fluent English.
* **Slowing Down Fast Speech:** Cross-lingual outputs can sometimes sound rushed. Use punctuation like commas `,` and ellipses `...` to force natural "breathing" pauses. Lower the node's `temperature` to **`0.70` or `0.75`** to stabilize the reading speed.
