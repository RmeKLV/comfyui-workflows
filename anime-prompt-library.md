# Anime prompt library — WAI Illustrious / NoobAI

Prompts, poses and failure modes for `WAI_Illustrious_BEST.json` and
`NoobAI_VPred_Anime.json`, plus the matching-PFP-pair pipeline built on top of them.
Everything here was rendered and checked at fixed seeds on an RX 7900 XTX; the dead
ends are recorded alongside the wins because they cost the most time to find.

Scripts: [`scripts/matching_pfp.py`](scripts/matching_pfp.py) (generator) and
[`scripts/split_pfp.py`](scripts/split_pfp.py) (face-centred splitter + contact sheet).

---

Built for a "cute anime pic, and it must not look like AI" brief. All rendered and
checked; outputs in `ComfyUI/output/anime_pfp/`.

**Settings:** `WAI_Illustrious_BEST.json` with **cfg 6 -> 5**, 20 steps,
euler_ancestral/normal, hires denoise 0.45. 1024x1024 for a PFP, 832x1216 portrait.
**Keep the hand detailer pass** (`bbox/hand_yolov8s.pt`) — without it any visible
hand comes out mangled.

## Shared negative

```
worst quality, low quality, lowres, jpeg artifacts, signature, watermark, username, artist name,
bad anatomy, bad hands, extra digits, fewer digits, mutated hands,
3d, render, realistic, photo, chromatic aberration, lens flare, bokeh, glowing,
oversaturated, gradient background, text, error
```

## 1 — Cute PFP, white background  *(best general-purpose result)*

```
best quality, newest, very awa, rating:general,
kantoku, ningen mame,
1girl, solo, upper body, looking at viewer, soft smile, light blush,
short brown hair, hair clip, oversized cream knit sweater, sweater paws,
head tilt, hand up near face,
white background, simple background,
flat color, cel shading, thick lineart, soft warm palette
```

## 2 — Chibi sticker set  *(9-up expression sheet, best effort-to-risk ratio)*

Use the **ESRGAN refine** path for this one — thick outlines need crisp edges.

```
best quality, newest, rating:general,
chibi, mini girl, multiple views, expression sheet,
1girl, solo, brown hair, cute, blush stickers,
:3, heart, sparkle, waving, sitting, sleeping,
white background, simple background, thick outline, flat color, sticker
```

## 3 — 90s screencap  *(least AI-looking mode there is)*

```
best quality, newest, rating:general,
anime screencap, retro artstyle, 1990s (style),
1girl, solo, upper body, looking to the side, gentle smile,
brown bob cut, cardigan, sitting by a window, evening light, curtains,
flat color, limited palette, thick lineart, film grain, halftone
```

## 4 — Chisato Nishikigi (Lycoris Recoil) — tag renders correctly

```
best quality, newest, very awa, rating:general,
ciloranko, hiten,
nishikigi chisato, lycoris recoil, 1girl, solo,
blonde hair, red eyes, hair ribbon, school uniform, bright grin, one eye closed,
peace sign, leaning toward viewer, dutch angle, upper body,
simple background, pale mint background,
flat color, cel shading, anime screencap
```

## 5 — Takina Inoue (Lycoris Recoil) — tag renders correctly

```
best quality, newest, very awa, rating:general,
ciloranko, hiten,
inoue takina, lycoris recoil, 1girl, solo,
long black hair, purple eyes, school uniform, expressionless, slight blush,
looking away, hands clasped in front, upper body,
simple background, soft grey background,
flat color, cel shading, muted palette
```

## 6 — NoobAI v-pred, painterly  *(bigger piece, not a PFP)*

`NoobAI_VPred_Anime.json`, cfg 5, euler/normal, `ModelSamplingDiscrete` v_prediction + zsnr.

```
masterpiece, best quality, newest, absurdres, very awa, rating:general,
fuzichoco, ask (askzy),
1girl, solo, long light brown hair, hazel eyes, soft smile,
white sundress, straw hat, standing in a field of cosmos flowers, wind,
late afternoon, warm rim light,
painterly, soft shading, muted palette
```

## 7 — Template: match someone's existing PFP

```
best quality, newest, very awa, rating:general,
kantoku, omutatsu,
1girl, solo, upper body, looking at viewer, [expression],
[hair length + color], [eye color], [hairstyle], [accessory],
[outfit],
white background, simple background,
flat color, cel shading, thick lineart, [palette] palette
```

## Known-bad

- `takagi (karakai jouzu no takagi-san)` — renders a generic dark-blue-haired girl in
  a classroom, not the character. Weak tag; needs a character LoRA.
- SD1.5 negative embeddings (EasyNegative, badhandv4, Deep Negative, FastNegativeV2)
  **will not load on SDXL**. SDXL ones (negativeXL, unaestheticXL) add ~nothing because
  Illustrious has quality scoring baked into its tag vocabulary.
- Detail-enhancer LoRAs (Detail Tweaker XL) push toward the over-rendered AI look —
  wrong direction here. Only interesting at *negative* strength (-0.5 to -1.0) to flatten.


---

## Matching PFP pair — Chisato x Takina (2026-08-26)

Wide 2:1 two-shot, split into two 1024x1024 PFPs. See the README for the recipe and the face-centred cropping rule. Scripts: `scripts/matching_pfp.py` + `scripts/split_pfp.py`. Best seeds: **22222** (canon kimono colours),
33333 (clearer half-hearts, colours swapped).

Shared style + character block:

```
best quality, newest, very awa, rating:general,
ciloranko, hiten,
2girls, lycoris recoil, inoue takina, nishikigi chisato,
<POSE>,
inoue takina, long black hair, low twintails, purple eyes, blue kimono, expressionless, light blush,
nishikigi chisato, blonde hair, short bob, red hair ribbon, red eyes, red kimono,
white background, simple background,
flat color, cel shading, thick lineart
```

Negative adds `extra arms, extra hands, 1girl, solo, 3girls` to the standard one.

### POSE — splits cleanly (use for a pair)

```
heart hands duo, heart hands, upper body, facing viewer,
standing close together, both arms forward, chisato grin, one eye closed
```

### POSE — does NOT split (use as one shared image)

```
cheek-to-cheek, leaning together, peace sign, double peace, upper body, facing viewer,
chisato open mouth, wink, tongue out
```

```
hug from behind, chisato hugging takina, arms around neck, upper body, facing viewer,
chisato happy, closed eyes, smile
```

The hug version nails their actual dynamic — Chisato beaming with her eyes shut, Takina
deadpan at the camera. Seed 77777.

---

## Matching PFP pair — round 2, 11 cute poses (2026-08-28)

Outputs in `ComfyUI/output/matching_v2/` (`wide/` 2048x1024 sources, `pfp/` 1024x1024
face-centred crops, `_contact_sheet_v2.png` circular previews).
Generator: `scripts/matching_pfp.py`  ·  splitter/cleanup: `scripts/split_pfp.py`.

**Chain (replaces the latent hires fix):** 1024x512 base -> VAEDecode -> `4x-AnimeSharp`
-> `ImageScale` lanczos 2048x1024 -> VAEEncode -> KSampler **denoise 0.35** -> face
detailer -> **hand detailer**. cfg 5, euler_ancestral/normal. ~75s per candidate.

**Give both girls the SAME outfit.** Illustrious swaps outfit colours between characters
about half the time; identical outfits make the swap invisible, and hair/eye colour
(always correct) still tells them apart. And do not fight canon — "navy sailor uniform"
made Chisato's canon grey Lycoris uniform bleed into her top mid-torso.

Shared style block:
```
best quality, newest, very awa, rating:general,
ciloranko, hiten,
2girls, lycoris recoil, inoue takina, nishikigi chisato,
wide shot, both girls fully in frame, side by side, evenly spaced,
balanced symmetrical composition,
whole head and hair inside the frame, headroom above the head,
<POSE>,
both girls wearing matching <OUTFIT>,
inoue takina, long black hair, low twintails, purple eyes, <EXPR>,
nishikigi chisato, blonde hair, short bob, red hair ribbon, red eyes, <EXPR>,
white background, simple background,
flat color, cel shading, thick lineart, clean lineart, finished illustration
```

Negative adds (each one fixed an observed failure):
```
giant hand, huge hand, oversized hand, hand focus, foreshortening,
reaching toward viewer, pointing at viewer,
border, framed, comic panel, letterbox, black bars, split screen, divider,
head out of frame, cropped head, hair cut off,
sketch, rough sketch, unfinished, extra arms, extra hands, 1girl, solo, 3girls
```

### Poses that SPLIT into two independent PFPs (faces >=0.30*W apart)
| pose | prompt core | outfit |
|---|---|---|
| pinky promise | `pinky swear, interlocked pinkies between them, hands at chest height, arms bent, standing apart facing each other, heads turned toward viewer` | light grey school uniform |
| half heart | `each girl making a half heart with her inner hand, hands meeting at chest height, other hand on own hip, standing apart` | white knit sweater |
| back-to-back | `back-to-back, arms folded across chest, heads turned toward viewer, confident` | black bomber jacket |
| cat paws | `matching cat ear hoodies, animal ear hood, paw pose, hands raised beside own face, cat smile, gap between them` | cream cat ear hoodie |
| peace signs | `v, double v, peace sign, each girl making a v sign beside her own face, gap between them` | navy tracksuit |

**Never write "peace sign" alone** — it gave a three-fingered hand. Use danbooru `v` / `double v`.
**Never write "arms extended toward each other"** — read as toward CAMERA, giant foreshortened hand.

### Poses that stay together (one shared look, both faces in both crops)
| pose | prompt core | outfit |
|---|---|---|
| bubble tea | `sharing bubble tea, two straws, holding the cup at chest height, leaning in close` | oversized cream knit sweater, sweater paws |
| shared earphones | `sharing earphones, one earbud each, a single cable running between them, heads tilted together` | grey hoodie |
| jump hug | `chisato jumping into takina's arms, hugging tightly around the neck, takina catching her, motion lines` | school uniform |
| sleepy | `takina asleep leaning on chisato's shoulder, chisato holding a warm mug at chest height, cozy` | cream pajamas |
| heart balloons | `each girl holding the string of a large red heart-shaped balloon between them, hands at shoulder height` | cream cardigan |

### Verify by LOOKING — the QC script cannot see these
Automated checks (face count, oversized hand, hand count, head clipped at top edge,
all-four-edges-dark border) caught roughly half the failures. These needed eyes:
a **mint-green** panel border (passed the dark-edge test), floating disembodied eye
shapes in the background, **Takina rendered with red hair**, and garment colour bleed.

---

## Round 3 — "silly cutie patootie" (2026-08-28)

Round 2 came back rejected: the poses read as *normal*, not silly.
Diagnosis was in my own prompts, not the model. Outputs: `output/matching_v3/`.

**The composition tags I added in round 2 to fix crowding are what made it "normal":**
`standing apart, evenly spaced, balanced symmetrical composition` produces a posed
group photo. Round 1's winners were the opposite — faces squished together doing
something goofy. Replace with:
```
upper body, both girls fully in frame from the waist up,
faces close together, leaning into each other, playful, energetic,
whole head and hair inside the frame, headroom above the head,
```
and push expressions hard: `tongue out, wink, one eye closed, open mouth, >_<, xd,
huge grin, :3` plus `sparkle, heart, blush stickers, motion lines`.
Negative gains `serious, stoic, formal, stiff pose, posed, standing at attention`.

**Do NOT use `close-up`.** It zooms so hard both heads clip the top edge every time.
It is in the negative now.

### Pose results
| pose | verdict |
|---|---|
| `chibi_duo` | **best of the batch** — sticker outline, hearts, blush stickers |
| `cheek_squish` | the round-1 formula, kimono. 3 keepers, reliable |
| `cat_silly` / `silly_faces` / `photobomb` | all good, 2 keepers each |
| `selfie` | 1/4 — `one arm extended toward camera` is the giant-hand trigger AGAIN |
| `piggyback` | weak; crops small with too much white |
| `bunny_ears` | **tag collision** — "bunny ears" is the ANIMAL-EAR tag, model drew real ears |
| `cheek_pinch` | **DEAD END, 0/8.** "squishing cheeks" forces a PROFILE two-shot facing each other, losing both faces for a PFP |

### Recurring failure: Takina's hair drifts red or green
Seen 4+ times across rounds (red in `pinky`, red in `bunny_ears`, dark green twice in the
swap test, green on REED). Almost certainly bleed from Chisato's adjacent red ribbon /
red eyes. No prompt fix found; **check hair colour on every frame.**

---

## Character-swap rate — MEASURED, n=11 per arm (2026-08-28)

Tested three ways at 11 seeds each, WAI Illustrious, identical everything else.

| arm | Takina lands LEFT | outfit bound to the right girl |
|---|---|---|
| identical outfits | 6/11 (55%) | n/a — a swap is invisible |
| **different outfits, plain prompt** | 6/11 (55%) | **7/11 (64%)** |
| regional area conditioning | — | **BROKEN** |

- **Side assignment is a coin flip and cannot be prompted.** Both arms 55%. Confirms the
  older note. Read the layout off the render; never trust "X on the left".
- **Different outfits swap ~36% of the time** even with the outfit written *inside* each
  girl's own attribute block next to her name. Better than chance, not reliable.
  **So identical outfits remain the correct recipe for a matching pair** — the swap
  becomes invisible instead of wrong.
- An early n=3 sample showed 3/3 correct and I nearly wrote that up as a fix. It was
  noise. **n=3 is not a result on a ~50/50 process.**

### Regional conditioning is a DEAD END here
`ConditioningSetAreaPercentage` (base `2girls` prompt + left region = Takina +
right region = Chisato, `ConditioningCombine`) rendered **three girls in all 3 seeds** —
an extra red-haired character every time. Base + 2 regional conditionings reads as
*more subjects*, not as placement. Not worth further tuning.

---

## Anime checkpoint shootout — 4 models, fixed seeds (2026-08-28)

24 renders: WAI / REED / Nova / NoobAI x 3 silly prompts x 2 seeds. New models are on
disk (`REED_Illustration_IL_v7`, `novaAnimeXL_IL_v19`, both Illustrious base, so all
existing tag prompting and cfg 5 carry over unchanged).

**Speed is not a differentiator** — 92-145s for all four. Pick on looks, as with the
earlier SDXL trio.

| model | verdict |
|---|---|
| **Nova Anime XL IL v19** | most saturated, strongest outlines. **Best for the chibi/sticker look** |
| **WAI Illustrious v17** | most consistent across seeds. Nothing broken either seed. Safe default |
| REED_Illustration IL v7 | very close to WAI, slightly softer — but gave Takina GREEN hair on one seed |
| NoobAI v-pred | least reliable here: heavy red-orange wash on one seed, Takina's hair drifted brown on the other. Needs `ModelSamplingDiscrete(v_prediction,zsnr)` + `RescaleCFG 0.7` + plain `euler` or it is far worse |

**Model-independent finding:** `chibi` + `2girls` is seed-fragile. At one seed WAI, REED
and Nova ALL rendered one chibi Chisato in front of a *full-size* Takina with her face
cropped out. Say `both girls chibi` explicitly.

---

## VRAM: the ESRGAN refine chain will OOM on a long session
`HIP out of memory ... 5.17 GiB reserved but unallocated` after ~2h of continuous
rendering — allocator fragmentation, not a true capacity limit (the ESRGAN pass expands
1024x512 -> 4096x2048). Two fixes, both applied:
1. launch with `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` (and the HIP alias)
2. `POST /free {"unload_models":false,"free_memory":true}` between renders — empties the
   cache without unloading models, so no model-switch tax.
Zero recurrences afterwards.

### The QC gate produces FALSE POSITIVES too — review the rejects, not just the keepers
The `oversized hand` rule (largest hand box > 4.5% of frame) rejected several perfectly
clean frames — a `selfie` and a `cat_silly` were binned with no oversized hand anywhere
in the image; the detector had merged two hands, or latched onto a face. Two of 17
rejects were recovered by eye and are now in `matching_v3/`.

**So the QC gate is a triage tool, not a verdict.** It is right about the direction
(defects cluster in what it flags) but wrong often enough in both directions that the
final call is always visual:
- it MISSES: light-coloured panel borders, floating artifacts, wrong hair colour, garment colour bleed
- it FALSE-POSITIVES: oversized hand, and head-clipping near the threshold
Always sheet the rejects and glance at them before deleting.

---

## Round 4 — "keep it PG", tongue removed (2026-08-28)

Feedback on the round-3 favourites: the tongue-out expression read as odd on some of
them, even though those were otherwise the picks. So: same silly energy, no tongue.
Outputs `output/matching_v4/` (`wide/` keepers, `pfp/` face-centred crops,
`rejects/`, `_contact_sheet_v4.png`). Generator `scripts/matching_pfp.py`, splitter `scripts/split_pfp.py`. **~75-111s per candidate** (WAI + Nova) when the
queue is clear. The 165-215s figures in this session's first log are a measurement
artifact — two copies of the batch were queued at once (see the method note below), so
every render in it was fighting the other for the GPU. Same lesson as always: one job at
a time or the numbers are fiction.

**`tongue out` is not load-bearing — the goofiness comes from the eyes.** Replacing it
with an eye-driven expression pair lost nothing:
```
grin    takina: closed eyes, happy, huge grin, ^_^     chisato: open mouth smile, huge grin, one eye closed, wink
wink    takina: wink, one eye closed, open mouth smile chisato: closed eyes, laughing, xd, huge grin
cat     takina: :3, cat smile, closed mouth smile      chisato: closed eyes, ^_^, happy, huge grin
squint  takina: >_<, closed eyes, laughing             chisato: huge grin, open mouth smile, blush
```
Negative gained `tongue, tongue out, :p, licking, saliva, drool, ahegao` — belt and
braces; the positive change alone was already enough.

### Results
| render | verdict |
|---|---|
| **cat_silly_A** | **best of the batch, and the only clean SPLIT** — paw pose keeps a real gap between them |
| **silly_faces_C** | closest match to the round-3 favourite, double `v`, clean hands |
| silly_faces_B / cat_silly_B / chibi_duo_B | good, shared (both faces in both crops) |
| cheek_squish_A/B | cute but framed too tight, see below |
| photobomb_A | REJECT — red-orange wash, red streaks bleeding into Chisato's hair |
| chibi_duo_A | REJECT — the known `chibi`+`2girls` failure, plus extreme zoom |
| silly_faces_A | REJECT — see the UI-bar hallucination below |

### `cheek-to-cheek` always goes close-up at 1024x512 — tags cannot fix it
Both cheek_squish seeds clipped the tops of both heads even with `medium shot`,
`wide angle`, `headroom above the head` positive AND `close-up, portrait, zoomed in,
extreme close-up, cropped head` negative. Two faces touching simply do not fit a 2:1
frame with headroom. **Fix is geometry, not prompt: render cheek-to-cheek on a taller
base** (1024x640+) and crop to 2:1 after. Poses with a gap (paw pose, `v` beside own
face) frame correctly at 1024x512.

### NEW failure mode: the model drew a phone/drawing-app UI
`silly_faces_A` came back with a dark **app toolbar down both edges** — plus/undo/layer
icons, like a screenshot of a drawing app. The art itself was fine. This passes every
automated check and the face crops looked clean, because the crop windows sit inside the
bars. Negative now carries `phone screenshot, ui, user interface, toolbar, sidebar,
app screen, drawing software, icons`; a reseed with it was clean.
**Always look at the WIDE image, not just the crops.**

### Model notes
WAI Illustrious v17 for everything except the chibi/sticker look; Nova Anime XL for that
(`chibi_duo_B` is Nova). Matches the shootout verdict — no change.

### Method note — `nohup ... &` inside a backgrounded harness call runs the job TWICE
Launching the batch as `nohup python gen.py > log &` while the harness itself was already
backgrounding the call made the wrapper exit 0 instantly with an empty log, which looked
exactly like "the child was killed". It had not been: it was still queueing to ComfyUI.
Relaunching produced a second concurrent batch — 16 renders instead of 8, pairwise
byte-identical (same seeds are deterministic), each roughly 2x slower from GPU contention.
**Give the harness the bare command and let it background it. No `&`, no `nohup`.**
An empty log plus exit 0 is not proof a job died — check `GET /queue` before relaunching.
