"""Matching anime PFP pair generator (ComfyUI HTTP API, no UI needed).

Renders a 2048x1024 two-shot per pose: 1024x512 base -> 4x-AnimeSharp ESRGAN ->
lanczos to 2048x1024 -> VAEEncode -> second sampler at denoise 0.35 -> face detailer
-> hand detailer. Split into two 1024x1024 PFPs with scripts/split_pfp.py.

Needs ComfyUI running on 127.0.0.1:8188 with ComfyUI-Impact-Pack (FaceDetailer,
UltralyticsDetectorProvider) and 4x-AnimeSharp in models/upscale_models/.

    python scripts/matching_pfp.py              # every job in JOBS
    python scripts/matching_pfp.py cat_silly_A  # just these

Leave ComfyUI running between batches; a cold model load dwarfs the render itself.
"""
import json, urllib.request, time, os, sys

SRV = "http://127.0.0.1:8188"

STYLE = """best quality, newest, very awa, rating:general,
ciloranko, hiten,
2girls, lycoris recoil, inoue takina, nishikigi chisato,
medium shot, upper body, both girls fully in frame from the waist up,
faces close together, leaning into each other, playful, energetic,
whole head and hair inside the frame, headroom above the head, wide angle,
{pose},
both girls wearing matching {outfit},
inoue takina, long black hair, low twintails, purple eyes, {et},
nishikigi chisato, blonde hair, short bob, red hair ribbon, red eyes, {ec},
sparkle, heart, blush stickers, motion lines,
white background, simple background,
flat color, cel shading, thick lineart, clean lineart, finished illustration"""

NEG = ("bad quality, worst quality, lowres, jpeg artifacts, signature, watermark, username, "
       "artist name, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, "
       "tongue, tongue out, :p, licking, saliva, drool, ahegao, "
       "close-up, giant hand, huge hand, oversized hand, hand focus, foreshortening, "
       "reaching toward viewer, pointing at viewer, "
       "border, framed, comic panel, letterbox, black bars, split screen, divider, "
       "phone screenshot, ui, user interface, toolbar, sidebar, app screen, drawing software, icons, "
       "head out of frame, cropped head, hair cut off, face focus, portrait, zoomed in, extreme close-up, "
       "serious, stoic, formal, stiff pose, posed, standing at attention, "
       "sketch, rough sketch, unfinished, extra arms, extra hands, 1girl, solo, 3girls")

# PG-cute expression pairs (takina, chisato) -- no tongue anywhere
E = {
 "grin":   ("closed eyes, happy, huge grin, ^_^",       "open mouth smile, huge grin, one eye closed, wink"),
 "wink":   ("wink, one eye closed, open mouth smile",   "closed eyes, laughing, xd, huge grin"),
 "cat":    (":3, cat smile, closed mouth smile, happy", "closed eyes, ^_^, happy, huge grin"),
 "squint": (">_<, closed eyes, laughing",               "huge grin, open mouth smile, blush"),
}

JOBS = [
 ("cheek_squish_A", "WAI",  "cheek-to-cheek, leaning together, heads tilted together", "red and blue kimono",  "grin",   411212),
 ("cheek_squish_B", "WAI",  "cheek-to-cheek, leaning together, heads tilted together", "red and blue kimono",  "wink",   412323),
 ("silly_faces_A",  "WAI",  "making silly faces at the camera, v, double v, hands beside own face",                    "cream knit sweater",   "squint", 421212),
 ("silly_faces_B",  "WAI",  "making silly faces at the camera, v, double v, hands beside own face",                    "grey hoodie",          "wink",   422323),
 ("cat_silly_A",    "WAI",  "matching cat ear hoodies, animal ear hood, paw pose, hands raised beside own face",       "cream cat ear hoodie", "cat",    431212),
 ("photobomb_A",    "WAI",  "chisato leaning into the frame from the side behind takina, both grinning at the camera", "grey hoodie",          "grin",   441212),
 ("silly_faces_C",  "WAI",  "making silly faces at the camera, v, double v, hands beside own face",                    "cream knit sweater",   "grin",   423535),
 ("cat_silly_B",    "WAI",  "matching cat ear hoodies, animal ear hood, paw pose, hands raised beside own face",       "cream cat ear hoodie", "wink",   432323),
 ("chibi_duo_A",    "NOVA", "both girls chibi, chibi, sticker style, thick white outline, hugging each other",         "pink hoodie",          "grin",   451212),
 ("chibi_duo_B",    "NOVA", "both girls chibi, chibi, sticker style, thick white outline, cheek to cheek",             "pink hoodie",          "cat",    452323),
]

CKPT = {"WAI": "waiIllustriousSDXL_v170.safetensors", "NOVA": "novaAnimeXL_IL_v19.safetensors"}


def graph(ckpt, pos, neg, seed, prefix):
    S = lambda i, o=0: [str(i), o]
    return {
        "1":  {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
        "2":  {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": S(1, 1)}},
        "3":  {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": S(1, 1)}},
        "4":  {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 512, "batch_size": 1}},
        "5":  {"class_type": "KSampler", "inputs": {"model": S(1), "positive": S(2), "negative": S(3), "latent_image": S(4),
               "seed": seed, "steps": 20, "cfg": 5.0, "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0}},
        "8":  {"class_type": "VAEDecode", "inputs": {"samples": S(5), "vae": S(1, 2)}},
        "20": {"class_type": "UpscaleModelLoader", "inputs": {"model_name": "4x-AnimeSharp.safetensors"}},
        "21": {"class_type": "ImageUpscaleWithModel", "inputs": {"upscale_model": S(20), "image": S(8)}},
        "22": {"class_type": "ImageScale", "inputs": {"image": S(21), "upscale_method": "lanczos", "width": 2048, "height": 1024, "crop": "disabled"}},
        "23": {"class_type": "VAEEncode", "inputs": {"pixels": S(22), "vae": S(1, 2)}},
        "24": {"class_type": "KSampler", "inputs": {"model": S(1), "positive": S(2), "negative": S(3), "latent_image": S(23),
               "seed": seed + 1, "steps": 18, "cfg": 5.0, "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 0.35}},
        "25": {"class_type": "VAEDecode", "inputs": {"samples": S(24), "vae": S(1, 2)}},
        "9":  {"class_type": "UltralyticsDetectorProvider", "inputs": {"model_name": "bbox/face_yolov8m.pt"}},
        "10": {"class_type": "FaceDetailer", "inputs": {"image": S(25), "model": S(1), "clip": S(1, 1), "vae": S(1, 2),
               "guide_size": 512, "guide_size_for": True, "max_size": 1024, "seed": seed + 2, "steps": 24, "cfg": 5.0,
               "sampler_name": "euler_ancestral", "scheduler": "normal", "positive": S(2), "negative": S(3),
               "denoise": 0.45, "feather": 5, "noise_mask": True, "force_inpaint": True, "bbox_threshold": 0.5,
               "bbox_dilation": 10, "bbox_crop_factor": 3.0, "sam_detection_hint": "center-1", "sam_dilation": 0,
               "sam_threshold": 0.93, "sam_bbox_expansion": 0, "sam_mask_hint_threshold": 0.7,
               "sam_mask_hint_use_negative": "False", "drop_size": 10, "bbox_detector": S(9), "wildcard": "", "cycle": 1}},
        "11": {"class_type": "UltralyticsDetectorProvider", "inputs": {"model_name": "bbox/hand_yolov8s.pt"}},
        "12": {"class_type": "FaceDetailer", "inputs": {"image": S(10), "model": S(1), "clip": S(1, 1), "vae": S(1, 2),
               "guide_size": 512, "guide_size_for": True, "max_size": 1024, "seed": seed + 3, "steps": 24, "cfg": 5.0,
               "sampler_name": "euler_ancestral", "scheduler": "normal", "positive": S(2), "negative": S(3),
               "denoise": 0.4, "feather": 5, "noise_mask": True, "force_inpaint": True, "bbox_threshold": 0.6,
               "bbox_dilation": 20, "bbox_crop_factor": 3.0, "sam_detection_hint": "center-1", "sam_dilation": 0,
               "sam_threshold": 0.93, "sam_bbox_expansion": 0, "sam_mask_hint_threshold": 0.7,
               "sam_mask_hint_use_negative": "False", "drop_size": 10, "bbox_detector": S(11), "wildcard": "", "cycle": 1}},
        "13": {"class_type": "SaveImage", "inputs": {"images": S(12), "filename_prefix": prefix}},
    }


def post(path, payload):
    req = urllib.request.Request(SRV + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    body = urllib.request.urlopen(req).read()
    return json.loads(body) if body.strip() else {}


def run(g):
    pid = post("/prompt", {"prompt": g})["prompt_id"]
    while True:
        time.sleep(3)
        h = json.load(urllib.request.urlopen(SRV + "/history/" + pid))
        if pid in h:
            st = h[pid]["status"]
            if st.get("status_str") == "error":
                raise RuntimeError(json.dumps(st)[:800])
            return [i["filename"] for n in h[pid]["outputs"].values() for i in n.get("images", [])]


only = sys.argv[1:] or None
for name, mk, pose, outfit, ex, seed in JOBS:
    if only and name not in only:
        continue
    et, ec = E[ex]
    pos = STYLE.format(pose=pose, outfit=outfit, et=et, ec=ec)
    t0 = time.time()
    try:
        outs = run(graph(CKPT[mk], pos, NEG, seed, "matching_v4/wide/" + name))
        print("OK   %-16s %-4s %6.1fs  %s" % (name, mk, time.time() - t0, outs), flush=True)
    except Exception as e:
        print("FAIL %-16s %s" % (name, e), flush=True)
    post("/free", {"unload_models": False, "free_memory": True})
print("TOTAL DONE", flush=True)
