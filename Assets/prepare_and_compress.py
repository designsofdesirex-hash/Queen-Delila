"""
Pipeline complet en un seul script :

  1) Trie un dossier de téléchargement en vrac (images + vidéos mélangées)
  2) Renomme chaque fichier en slug SEO-friendly (mot-clé + description + numéro)
  3) Compresse les images en WebP (recherche SSIM -> qualité max sans perte visible)
  4) Compresse les vidéos en AV1 + H264 (recherche SSIM sur un segment -> CRF max sans perte visible)

Dépendances : ffmpeg (libsvtav1 + libx264), pip install pillow numpy scikit-image
"""

from pathlib import Path
from PIL import Image, ImageOps
import io
import os
import re
import shutil
import subprocess
import tempfile
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from skimage.metrics import structural_similarity as ssim

# ==========================================
# CONFIGURATION — À ADAPTER
# ==========================================

# Dossier où tu déposes ton téléchargement en vrac (images + vidéos mélangées,
# sous-dossiers acceptés).
SOURCE_DIR = Path("assets/downloads")

# Mot-clé SEO principal à intégrer dans chaque nom de fichier.
# Ex : "canapé-velours-bleu", "mariage-casablanca-2026", "sneaker-blanche"
SEO_KEYWORD = "mon-mot-cle"

# Copie (garde SOURCE_DIR intact) ou déplace (vide SOURCE_DIR) les fichiers triés.
MOVE_INSTEAD_OF_COPY = False

# Dossiers de travail (pas besoin d'y toucher, alignés avec le reste du pipeline)
IMG_DIR = Path("assets/img")                  # images triées + renommées
WEBP_DIR = Path("assets/webp")                # images compressées (sortie finale)
VID_DIR = Path("assets/Vid")                  # vidéos triées + renommées
VID_OUT_DIR = Path("assets/Vid_optimized")    # vidéos compressées (sortie finale)

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".jfif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".m4v", ".flv", ".webm"}

# --- réglages qualité image (identiques au script précédent) ---
LOSSLESS_KEYWORDS = [
    "logo", "icon", "diagram", "schematic", "pcb",
    "layout", "drawing", "graph", "chart", "screenshot",
]
TARGET_SSIM_IMG = 0.985
MIN_QUALITY, MAX_QUALITY = 60, 95
KEEP_SMALLER_ORIGINAL = True
MAX_WORKERS = os.cpu_count() or 4

# --- réglages qualité vidéo (identiques au script précédent) ---
SKIP_EXISTING_VIDEO = True
USE_QUALITY_SEARCH = True
TARGET_SSIM_VIDEO = 0.975
PROBE_DURATION = 12
SAMPLE_FRAMES = 5
MAX_SEARCH_ITERS = 6
AV1_CRF_RANGE = (20, 45)
H264_CRF_RANGE = (18, 30)
AV1_PRESET = "6"
H264_PRESET = "slow"
FALLBACK_AV1_CRF = 30
FALLBACK_H264_CRF = 22

# ==========================================
# PHASE 1 — TRI + RENOMMAGE SEO
# ==========================================

CAMERA_DEFAULT_PATTERNS = [
    r"^img[_-]?\d+$", r"^dsc[_-]?\d+$", r"^dcim[_-]?\d+$",
    r"^vid[_-]?\d+$", r"^mov[_-]?\d+$", r"^video[_-]?\d+$",
    r"^screenshot.*$", r"^whatsapp.*$", r"^photo[_-]?\d+$",
    r"^[\d-]+$", r"^signal-\d+.*$", r"^snapchat.*$",
]


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def is_generic_filename(slug: str) -> bool:
    return any(re.match(p, slug) for p in CAMERA_DEFAULT_PATTERNS) or not slug


def build_seo_name(original_stem: str, keyword: str, index: int, total: int) -> str:
    pad = max(2, len(str(total)))
    counter = str(index).zfill(pad)
    slug = slugify(original_stem)
    if is_generic_filename(slug):
        # nom d'origine inutile pour le SEO (IMG_1234, capture d'écran...) -> mot-clé + numéro
        return f"{keyword}-{counter}"
    return f"{keyword}-{slug}-{counter}"


def dedupe_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix, parent = path.stem, path.suffix, path.parent
    n = 2
    while (parent / f"{stem}-{n}{suffix}").exists():
        n += 1
    return parent / f"{stem}-{n}{suffix}"


def sort_and_rename():
    if not SOURCE_DIR.exists():
        raise SystemExit(f"SOURCE_DIR introuvable : {SOURCE_DIR.resolve()}")

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    VID_DIR.mkdir(parents=True, exist_ok=True)

    all_files = sorted(f for f in SOURCE_DIR.rglob("*") if f.is_file())
    images = [f for f in all_files if f.suffix.lower() in PHOTO_EXTENSIONS]
    videos = [f for f in all_files if f.suffix.lower() in VIDEO_EXTENSIONS]
    others = [f for f in all_files if f not in images and f not in videos]

    log_rows = []

    def place(files, dest_dir):
        for i, f in enumerate(files, start=1):
            new_stem = build_seo_name(f.stem, SEO_KEYWORD, i, len(files))
            dest = dedupe_path(dest_dir / f"{new_stem}{f.suffix.lower()}")
            if MOVE_INSTEAD_OF_COPY:
                shutil.move(str(f), str(dest))
            else:
                shutil.copy2(f, dest)
            log_rows.append((str(f.relative_to(SOURCE_DIR)), dest.name))
            print(f"  {f.name}  ->  {dest.name}")

    print(f"Images trouvées : {len(images)}")
    place(images, IMG_DIR)
    print(f"\nVidéos trouvées : {len(videos)}")
    place(videos, VID_DIR)

    if others:
        print(f"\nIgnorés (ni image ni vidéo) : {len(others)} fichier(s)")

    log_path = Path("rename_log.csv")
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nom_original", "nouveau_nom"])
        writer.writerows(log_rows)
    print(f"\nJournal de renommage : {log_path.resolve()}")


# ==========================================
# PHASE 2 — COMPRESSION IMAGES (WebP, qualité garantie par SSIM)
# ==========================================

def to_comparable_array(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("RGB"), dtype=np.float32)


def encode_at_quality(img: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


def measure_ssim_img(reference_arr: np.ndarray, candidate_bytes: bytes) -> float:
    candidate_img = Image.open(io.BytesIO(candidate_bytes))
    candidate_arr = to_comparable_array(candidate_img)
    score, _ = ssim(reference_arr, candidate_arr, channel_axis=2, full=True, data_range=255)
    return score


def find_best_quality(img: Image.Image):
    reference_arr = to_comparable_array(img)
    lo, hi = MIN_QUALITY, MAX_QUALITY

    top_bytes = encode_at_quality(img, hi)
    top_score = measure_ssim_img(reference_arr, top_bytes)
    if top_score < TARGET_SSIM_IMG:
        return top_bytes, hi, top_score

    best_bytes, best_q, best_score = top_bytes, hi, top_score
    while lo <= hi:
        mid = (lo + hi) // 2
        data = encode_at_quality(img, mid)
        score = measure_ssim_img(reference_arr, data)
        if score >= TARGET_SSIM_IMG:
            best_bytes, best_q, best_score = data, mid, score
            hi = mid - 1
        else:
            lo = mid + 1
    return best_bytes, best_q, best_score


def process_image(file: Path):
    relative = file.relative_to(IMG_DIR)
    output_webp = WEBP_DIR / relative.with_suffix(".webp")
    output_fallback = WEBP_DIR / relative
    output_webp.parent.mkdir(parents=True, exist_ok=True)

    if output_webp.exists() or output_fallback.exists():
        return None

    use_lossless = any(k in file.name.lower() for k in LOSSLESS_KEYWORDS)

    try:
        with Image.open(file) as raw_img:
            img = ImageOps.exif_transpose(raw_img)
            if img.mode not in ("RGB", "RGBA"):
                has_alpha = "transparency" in img.info or img.mode in ("LA", "PA")
                img = img.convert("RGBA" if has_alpha else "RGB")

            if use_lossless:
                buf = io.BytesIO()
                img.save(buf, "WEBP", lossless=True, quality=100, method=6, exact=True)
                data, quality_used, score = buf.getvalue(), "lossless", 1.0
            else:
                data, quality_used, score = find_best_quality(img)

            original = file.stat().st_size

            if KEEP_SMALLER_ORIGINAL and len(data) >= original:
                output_fallback.write_bytes(file.read_bytes())
                new_size = original
                note = "original conservé (WebP plus lourd)"
            else:
                output_webp.write_bytes(data)
                new_size = len(data)
                note = f"q={quality_used} SSIM={score:.4f}"

        reduction = 100 * (1 - new_size / original) if original else 0
        return {"relative": str(relative), "original": original, "new": new_size,
                "reduction": reduction, "note": note, "error": None}
    except Exception as e:
        return {"relative": str(relative), "error": str(e)}


def compress_images():
    files = [f for f in IMG_DIR.rglob("*") if f.suffix.lower() in PHOTO_EXTENSIONS]
    if not files:
        print("Aucune image à compresser.")
        return

    total_original = total_new = converted = kept_original = 0
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_image, f): f for f in files}
        for future in as_completed(futures):
            result = future.result()
            if result is None:
                continue
            if result["error"]:
                print(f"ERROR {futures[future]}")
                print(result["error"])
                continue
            total_original += result["original"]
            total_new += result["new"]
            converted += 1
            if "conservé" in result["note"]:
                kept_original += 1
            print(f"OK {result['relative']} | {result['original']/1024:.1f} KB -> "
                  f"{result['new']/1024:.1f} KB ({result['reduction']:.1f}% smaller) | {result['note']}")

    print("\n--- Images ---")
    print(f"Converties        : {converted}")
    print(f"Original conservé : {kept_original}")
    print(f"Original          : {total_original/1024/1024:.2f} MB")
    print(f"Compressé         : {total_new/1024/1024:.2f} MB")
    if total_original:
        print(f"Gain              : {(1-total_new/total_original)*100:.1f}%")


# ==========================================
# PHASE 3 — COMPRESSION VIDEOS (AV1 + H264, qualité garantie par SSIM)
# ==========================================

def ffprobe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def build_encode_cmd(input_file, output_file, codec, crf, preset, verbose=True):
    loglevel = ["-stats"] if verbose else []
    common = ["ffmpeg", "-hide_banner", "-loglevel", "error", *loglevel, "-y", "-i", str(input_file)]
    if codec == "av1":
        return [*common, "-map_metadata", "-1", "-c:v", "libsvtav1", "-crf", str(crf),
                "-preset", str(preset), "-svtav1-params", "tune=0", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output_file)]
    return [*common, "-map_metadata", "-1", "-c:v", "libx264", "-preset", str(preset),
            "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(output_file)]


def encode(input_file, output_file, codec, crf, preset, verbose=True):
    cmd = build_encode_cmd(input_file, output_file, codec, crf, preset, verbose=verbose)
    if verbose:
        subprocess.run(cmd, check=True)
    else:
        subprocess.run(cmd, check=True, capture_output=True)


def extract_frames(video: Path, out_dir: Path, n: int):
    out_dir.mkdir(parents=True, exist_ok=True)
    duration = ffprobe_duration(video)
    frames = []
    for i in range(n):
        t = duration * (i + 0.5) / n
        fp = out_dir / f"f{i}.png"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                         "-ss", str(t), "-i", str(video), "-frames:v", "1", str(fp)],
                        check=True, capture_output=True)
        frames.append(fp)
    return frames


def average_ssim_video(frames_a, frames_b) -> float:
    scores = []
    for a, b in zip(frames_a, frames_b):
        ia = np.asarray(Image.open(a).convert("RGB"), dtype=np.float32)
        ib_img = Image.open(b).convert("RGB")
        if ib_img.size != Image.open(a).size:
            ib_img = ib_img.resize(Image.open(a).size)
        ib = np.asarray(ib_img, dtype=np.float32)
        score, _ = ssim(ia, ib, channel_axis=2, full=True, data_range=255)
        scores.append(score)
    return sum(scores) / len(scores)


def find_best_crf(source_file, codec, crf_range, preset, workdir):
    try:
        duration = ffprobe_duration(source_file)
        probe_len = min(PROBE_DURATION, duration)
        start = max(0, (duration - probe_len) / 2)

        probe_src = workdir / "probe_src.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                         "-ss", str(start), "-i", str(source_file), "-t", str(probe_len),
                         "-c", "copy", str(probe_src)], check=True, capture_output=True)
        ref_frames = extract_frames(probe_src, workdir / "ref", SAMPLE_FRAMES)

        lo, hi = crf_range
        best_crf, best_score = lo, None
        for _ in range(MAX_SEARCH_ITERS):
            if lo > hi:
                break
            mid = (lo + hi) // 2
            candidate = workdir / f"probe_{codec}_{mid}.mp4"
            encode(probe_src, candidate, codec, mid, preset, verbose=False)
            cand_frames = extract_frames(candidate, workdir / f"cand_{codec}_{mid}", SAMPLE_FRAMES)
            score = average_ssim_video(ref_frames, cand_frames)
            print(f"    essai CRF={mid} -> SSIM={score:.4f}")
            if score >= TARGET_SSIM_VIDEO:
                best_crf, best_score = mid, score
                lo = mid + 1
            else:
                hi = mid - 1

        if best_score is None:
            best_crf, best_score = crf_range[0], None
        return best_crf, best_score
    except Exception as e:
        print(f"    recherche de qualité impossible ({e}), repli sur CRF fixe")
        return None


def process_video(file: Path):
    relative = file.relative_to(VID_DIR)
    av1_out = VID_OUT_DIR / relative.with_suffix(".av1.mp4")
    h264_out = VID_OUT_DIR / relative.with_suffix(".mp4")
    av1_out.parent.mkdir(parents=True, exist_ok=True)

    if SKIP_EXISTING_VIDEO and av1_out.exists() and h264_out.exists():
        print(f"SKIP {relative} (déjà encodé)")
        return

    print(f"\nEncodage {file.name}")
    av1_crf, h264_crf = FALLBACK_AV1_CRF, FALLBACK_H264_CRF

    if USE_QUALITY_SEARCH:
        workdir = Path(tempfile.mkdtemp(prefix="probe_"))
        try:
            print("  Recherche du CRF AV1...")
            result = find_best_crf(file, "av1", AV1_CRF_RANGE, AV1_PRESET, workdir)
            if result:
                av1_crf, score = result
                print(f"  -> CRF AV1 retenu : {av1_crf}" + (f" (SSIM={score:.4f})" if score else " (plafond de la plage)"))
            print("  Recherche du CRF H264...")
            result = find_best_crf(file, "h264", H264_CRF_RANGE, H264_PRESET, workdir)
            if result:
                h264_crf, score = result
                print(f"  -> CRF H264 retenu : {h264_crf}" + (f" (SSIM={score:.4f})" if score else " (plafond de la plage)"))
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    encode(file, av1_out, "av1", av1_crf, AV1_PRESET)
    encode(file, h264_out, "h264", h264_crf, H264_PRESET)

    original = file.stat().st_size
    print(f"Original : {original/1024/1024:.2f} MB")
    print(f"AV1      : {av1_out.stat().st_size/1024/1024:.2f} MB (CRF={av1_crf})")
    print(f"H264     : {h264_out.stat().st_size/1024/1024:.2f} MB (CRF={h264_crf})")


def compress_videos():
    VID_OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = [f for f in VID_DIR.rglob("*") if f.suffix.lower() in VIDEO_EXTENSIONS]
    if not files:
        print("Aucune vidéo à compresser.")
        return
    for file in files:
        process_video(file)


# ==========================================
# MAIN
# ==========================================

def main():
    print("=" * 60)
    print("PHASE 1/3 — Tri + renommage SEO")
    print("=" * 60)
    sort_and_rename()

    print("\n" + "=" * 60)
    print("PHASE 2/3 — Compression des images")
    print("=" * 60)
    compress_images()

    print("\n" + "=" * 60)
    print("PHASE 3/3 — Compression des vidéos")
    print("=" * 60)
    compress_videos()

    print("\nTerminé. Images -> ", WEBP_DIR.resolve(), " | Vidéos -> ", VID_OUT_DIR.resolve())


if __name__ == "__main__":
    main()
