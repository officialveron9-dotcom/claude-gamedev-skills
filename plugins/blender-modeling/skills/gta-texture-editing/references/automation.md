# Automation scripts (run on the user's Windows machine)

Read when Claude should batch-convert, validate, or do a first-pass paint-out. All scripts are
stand-alone Python 3.10+ files. Save them into one folder (e.g. `tools/`); `make_ytd_xml.py` imports
`dds_check.py`. Setup: `py -m pip install opencv-python-headless pillow numpy`. texconv is Windows only
(`winget install Microsoft.DirectXTex.Texconv`).

Test status (2026-10-10, Linux, Python 3.13, OpenCV 5.0, Pillow 12.3, synthetic 512² brick facade with a painted
door, `_n`, `_s` with alpha, night map): `paint_out.py` clone mode brought the door region to within the noise
level of the clean wall (mean abs error 50.9 to 7.1); Telea reached only 21.2 because it blurs the brick
pattern. Pixels outside the mask were unchanged. Normal-map door bevels were removed, spec R/A were reset, the
night window went black, half-resolution maps got a scaled mask, and `--uv-rect` gave the same mask as
`--rect`. `dds_check.py`, `make_ytd_xml.py` and `rsc_gen.py` were tested on synthetic DDS/RSC7 headers and Pillow DDS
files. `png2dds.py` was tested in `--dry-run` (texconv is not available on Linux); its flags were checked
against texconv's source. The LaMa path is **untested** (model download).

Typical run:

```bat
py tools\paint_out.py --diffuse png\mymlo_facade_d.png --normal png\mymlo_facade_n.png ^
   --spec png\mymlo_facade_s.png --rect 812,1290,190,420 --mode clone --offset 256,0 --out edited
:: retouch edited\*.png by hand (mask in edited\mymlo_facade_d_mask.png), then:
py tools\png2dds.py edited work\mymlo_facade
py tools\dds_check.py work\mymlo_facade
py tools\make_ytd_xml.py work\mymlo_facade
:: CodeWalker (Legacy mode) > RPF Explorer > Import XML > work\mymlo_facade.ytd.xml -> stream\
:: Alchemist / CodeWalker Enhanced mode -> stream_enhanced\ ; then:
py tools\rsc_gen.py resources\[maps]\my_mlo
```

## paint_out.py: same mask and operation on every map

- Get pixel coordinates from GIMP (pointer dialog) or from Blender UVs of the door faces (`--uv-rect`).
- Clone offset = an integer multiple of the brick/panel period (see paint-out-workflow.md §3).
- `--tile` wraps the image edges for inpainting on tiling textures, so no seam appears at the repeat.
- Output PNGs carry no `sRGB`/`gAMA` chunk (Pillow), so texconv does not convert them.

```python
"""First-pass removal of a painted-on door/window from a GTA facade texture set.
Applies the SAME mask and the SAME operation to diffuse, normal (_n), specular (_s) and
night/emissive maps, writes a mask PNG for manual retouch, never overwrites inputs.

  python paint_out.py --diffuse wall.png --normal wall_n.png --spec wall_s.png \
      --rect 210,300,90,180 --mode clone --offset 128,0 --out edited/
  python paint_out.py --diffuse wall.png --uv-rect 0.41,0.05,0.59,0.40 --mode telea --tile --out edited/

--rect x,y,w,h in pixels (origin top-left, as in GIMP/Photoshop).
--uv-rect u0,v0,u1,v1 in Blender UV space (origin bottom-left; Sollumz flips V on import).
Modes: clone (copy from --offset dx,dy, best for brick/tile grids), telea / ns (OpenCV
inpaint, small areas), lama (diffuse only, needs `pip install simple-lama-inpainting`).
Requires: pip install opencv-python-headless pillow numpy
"""
import argparse
import pathlib

import cv2
import numpy as np
from PIL import Image


def load(path):
    img = Image.open(path)
    return np.array(img.convert("RGBA" if "A" in img.getbands() else "RGB"))


def save(arr, path):
    Image.fromarray(arr).save(path)  # Pillow writes no sRGB/gAMA chunk -> texconv sees plain UNORM data
    print("wrote", path)


def build_mask(shape, rects, uv_rects, grow):
    h, w = shape[:2]
    mask = np.zeros((h, w), np.uint8)
    for x, y, rw, rh in rects:
        mask[y:y + rh, x:x + rw] = 255
    for u0, v0, u1, v1 in uv_rects:
        fu, fv = np.floor(min(u0, u1)), np.floor(min(v0, v1))  # tiled UVs: shift into the 0..1 tile
        x0, x1 = sorted(np.clip(((u0 - fu) * w, (u1 - fu) * w), 0, w))
        y0, y1 = sorted(np.clip(((1 - (v0 - fv)) * h, (1 - (v1 - fv)) * h), 0, h))
        mask[int(y0):int(np.ceil(y1)), int(x0):int(np.ceil(x1))] = 255
    if grow:
        mask = cv2.dilate(mask, np.ones((2 * grow + 1, 2 * grow + 1), np.uint8))
    return mask


def clone(arr, mask, dx, dy, feather):
    h, w = mask.shape
    ys, xs = np.mgrid[0:h, 0:w]
    src = arr[(ys + dy) % h, (xs + dx) % w]  # wraps around: correct for tiling textures
    soft = cv2.GaussianBlur(mask, (0, 0), feather) if feather else mask
    a = (soft.astype(np.float32) / 255)[..., None]
    return (arr * (1 - a) + src * a + 0.5).astype(np.uint8)


def inpaint(arr, mask, mode, radius, tile):
    pad = radius * 4 if tile else 0
    flag = cv2.INPAINT_TELEA if mode == "telea" else cv2.INPAINT_NS
    m = np.pad(mask, pad, mode="wrap") if pad else mask
    out = []
    for c in range(arr.shape[2]):  # cv2.inpaint takes 1 or 3 channels; do each channel
        ch = np.pad(arr[..., c], pad, mode="wrap") if pad else arr[..., c]
        r = cv2.inpaint(np.ascontiguousarray(ch), m, radius, flag)
        out.append(r[pad:pad + mask.shape[0], pad:pad + mask.shape[1]] if pad else r)
    return np.dstack(out)


def lama(arr, mask, tile):
    from simple_lama_inpainting import SimpleLama  # Apache-2.0 code; check weight terms for commercial use
    pad = 64 if tile else 0
    rgb = np.pad(arr[..., :3], ((pad, pad), (pad, pad), (0, 0)), mode="wrap") if pad else arr[..., :3]
    m = np.pad(mask, pad, mode="wrap") if pad else mask
    res = np.array(SimpleLama()(Image.fromarray(rgb), Image.fromarray(m)))
    res = res[pad:pad + mask.shape[0], pad:pad + mask.shape[1]]
    out = arr.copy()
    out[..., :3] = np.where(mask[..., None] > 0, res, arr[..., :3])
    return out


def fix_normal(arr, mask):
    """GTA reads only R,G of BumpSampler and rebuilds Z; keep x^2+y^2 <= 1, rebuild B for previews.
    Touches only the (slightly grown) masked area so untouched pixels stay bit-identical."""
    n = arr.astype(np.float32) / 127.5 - 1
    xy = n[..., :2]
    length = np.maximum(np.linalg.norm(xy, axis=-1, keepdims=True), 1.0)
    xy = xy / length
    z = np.sqrt(np.clip(1 - (xy ** 2).sum(-1, keepdims=True), 0, 1))
    fixed = ((np.concatenate([xy, z], -1) + 1) * 127.5 + 0.5).clip(0, 255).astype(np.uint8)
    area = cv2.dilate(mask, np.ones((9, 9), np.uint8)) > 0
    out = arr.copy()
    out[area, :3] = fixed[area]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diffuse", required=True)
    ap.add_argument("--normal")
    ap.add_argument("--spec")
    ap.add_argument("--night", help="emissive/night map: masked area is set to black (no glow)")
    ap.add_argument("--rect", action="append", default=[], type=lambda s: tuple(map(int, s.split(","))))
    ap.add_argument("--uv-rect", action="append", default=[], type=lambda s: tuple(map(float, s.split(","))))
    ap.add_argument("--mode", choices=["clone", "telea", "ns", "lama"], default="clone")
    ap.add_argument("--offset", default="0,0", help="clone source offset dx,dy in pixels")
    ap.add_argument("--radius", type=int, default=5)
    ap.add_argument("--grow", type=int, default=2, help="dilate mask by N px (covers door frame shadow)")
    ap.add_argument("--feather", type=float, default=3.0)
    ap.add_argument("--tile", action="store_true", help="texture tiles: wrap edges when inpainting")
    ap.add_argument("--out", default="edited")
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    diffuse = load(a.diffuse)
    mask = build_mask(diffuse.shape, a.rect, a.uv_rect, a.grow)
    if not mask.any():
        raise SystemExit("empty mask: give --rect or --uv-rect")
    save(mask, out / (pathlib.Path(a.diffuse).stem + "_mask.png"))
    dx, dy = map(int, a.offset.split(","))

    for path, role in ((a.diffuse, "diffuse"), (a.normal, "normal"), (a.spec, "spec"), (a.night, "night")):
        if not path:
            continue
        arr = diffuse if role == "diffuse" else load(path)
        if arr.shape[:2] != mask.shape:  # maps of different resolution: scale the mask
            m = cv2.resize(mask, (arr.shape[1], arr.shape[0]), interpolation=cv2.INTER_NEAREST)
            sx, sy = arr.shape[1] / mask.shape[1], arr.shape[0] / mask.shape[0]
            ox, oy = round(dx * sx), round(dy * sy)
        else:
            m, ox, oy = mask, dx, dy
        if role == "night":
            res = arr.copy()
            res[m > 0, :3] = 0
        elif a.mode == "clone":
            res = clone(arr, m, ox, oy, a.feather)
        elif a.mode == "lama" and role == "diffuse":
            res = lama(arr, m, a.tile)
        else:  # lama is not suited to normal/spec data: fall back to OpenCV
            res = inpaint(arr, m, "telea" if a.mode == "lama" else a.mode, a.radius, a.tile)
        if role == "normal":
            res = fix_normal(res, m)
        save(res, out / (pathlib.Path(path).stem + ".png"))


if __name__ == "__main__":
    main()
```

LaMa on its own (Apache-2.0 code; check the weight/dataset terms for paid MLOs). Input must be RGB, and the mask is 255
where the image should be filled:

```python
from PIL import Image
from simple_lama_inpainting import SimpleLama   # pip install simple-lama-inpainting (pulls in torch)
img = Image.open("wall_d.png"); mask = Image.open("edited/wall_d_mask.png").convert("L")
out = SimpleLama()(img.convert("RGB"), mask)       # size must be a multiple of 8 (true for power-of-two maps)
if "A" in img.getbands():
    out.putalpha(img.getchannel("A"))               # LaMa drops alpha
out.save("wall_d_lama.png")
```
IOPaint batch alternative: `iopaint run --model=lama --device=cpu --image=png --mask=masks --output=out`.

## png2dds.py: batch PNG to DDS with texconv

Role by suffix (`_n`, `_s`, `script_rt_`, otherwise colour). Picks BC1/BC3 by actual alpha use, or `--bc7`. Mips stop at 4x4,
names are lower case, and only `*_UNORM` formats are written. Non-power-of-two files are refused, not stretched.

```python
"""Batch-convert edited PNGs to GTA-ready DDS with texconv (Windows, DirectXTex).
  python png2dds.py edited/ dds/ [--bc7] [--dry-run] [--texconv C:/tools/texconv.exe]
Role by file name: *_n -> normal, *_s -> specular, script_rt_* -> uncompressed, else color.
Writes *_UNORM formats only (CodeWalker maps *_SRGB DDS to an unknown format), mips down to 4x4."""
import argparse
import math
import pathlib
import shutil
import subprocess
import sys

from PIL import Image


def plan(png, bc7):
    img = Image.open(png)
    w, h = img.size
    if w & (w - 1) or h & (h - 1):
        raise ValueError(f"{png.name}: {w}x{h} is not power of two; fix the canvas, do not stretch")
    stem = png.stem.lower()
    has_alpha = "A" in img.getbands() and img.getchannel("A").getextrema()[0] < 255
    mips = max(1, int(math.log2(min(w, h))) - 1)  # last mip is 4 px on the short side
    if stem.startswith("script_rt_"):
        return ["-f", "B8G8R8A8_UNORM", "-m", "1", "--ignore-srgb"]
    fmt = "BC7_UNORM" if bc7 else ("BC3_UNORM" if has_alpha else "BC1_UNORM")  # spec alpha = gloss: keep it
    if stem.endswith(("_n", "_s")):  # data maps (GTA reads normal R,G only): never gamma-convert
        return ["-f", fmt, "-m", str(mips), "--ignore-srgb"]
    return ["-f", fmt, "-m", str(mips), "-srgb"]  # -srgb: keep 8-bit values exactly, even if PNG is tagged sRGB


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--bc7", action="store_true", help="BC7_UNORM for all compressed maps (test in game on Legacy)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--texconv", default=shutil.which("texconv") or "texconv.exe")
    a = ap.parse_args()
    dst = pathlib.Path(a.dst)
    dst.mkdir(parents=True, exist_ok=True)
    failed = False
    for png in sorted(pathlib.Path(a.src).glob("*.png")):
        if png.stem.endswith("_mask"):
            continue
        try:
            args = plan(png, a.bc7)
        except ValueError as e:
            print("SKIP", e)
            failed = True
            continue
        cmd = [a.texconv, "-nologo", "-y", "-l", "-o", str(dst), *args, str(png)]  # -l: lowercase names
        print(" ".join(cmd))
        if not a.dry_run:
            failed |= subprocess.run(cmd).returncode != 0
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
```

## dds_check.py: validate before packing

Checks the DDS header: power of two, divisible by 4, mip count (none, partial, or below 4x4), `_SRGB`/typeless
formats (CodeWalker cannot import them), more than 2048 px, more than 16 MiB, and uncompressed non-`script_rt` textures. It also sums the total size.

```python
"""Check DDS files before packing them into a GTA V .ytd.
Usage: python dds_check.py <file-or-folder> [...]
Reports size, power-of-two, mip count, format, sRGB flag, memory; exits 1 on any ERROR."""
import math
import pathlib
import struct
import sys

FOURCC = {b"DXT1": "BC1", b"DXT3": "BC2", b"DXT5": "BC3", b"ATI1": "BC4", b"BC4U": "BC4",
          b"ATI2": "BC5", b"BC5U": "BC5", b"BC7 ": "BC7"}
DXGI = {70: "BC1_TYPELESS", 73: "BC2_TYPELESS", 76: "BC3_TYPELESS", 97: "BC7_TYPELESS",
        71: "BC1", 72: "BC1_SRGB", 74: "BC2", 75: "BC2_SRGB", 77: "BC3", 78: "BC3_SRGB",
        80: "BC4", 83: "BC5", 98: "BC7", 99: "BC7_SRGB", 28: "RGBA8", 29: "RGBA8_SRGB",
        87: "BGRA8", 91: "BGRA8_SRGB", 88: "BGRX8", 61: "R8", 65: "A8"}
BYTES_PER_PIXEL = {"BC1": 0.5, "BC4": 0.5, "BC2": 1, "BC3": 1, "BC5": 1, "BC7": 1,
                   "RGBA8": 4, "BGRA8": 4, "BGRX8": 4, "R8": 1, "A8": 1}


def read_header(path):
    with open(path, "rb") as f:
        data = f.read(148)
    if len(data) < 128 or data[:4] != b"DDS ":
        raise ValueError("not a DDS file")
    height, width = struct.unpack_from("<II", data, 12)
    mips = struct.unpack_from("<I", data, 28)[0] or 1
    pf_flags, fourcc = struct.unpack_from("<I4s", data, 80)
    if pf_flags & 0x4 and fourcc == b"DX10":
        fmt = DXGI.get(struct.unpack_from("<I", data, 128)[0], f"DXGI#{data[128]}")
    elif pf_flags & 0x4:
        fmt = FOURCC.get(fourcc, fourcc.decode("latin1"))
    else:  # uncompressed legacy header: 32-bit RGB(A) masks
        bits = struct.unpack_from("<I", data, 88)[0]
        fmt = "BGRA8" if bits == 32 else f"RGB{bits}"
    return width, height, mips, fmt


def check(path):
    w, h, mips, fmt = read_header(path)
    base = fmt.replace("_SRGB", "").replace("_TYPELESS", "")
    pow2 = w & (w - 1) == 0 and h & (h - 1) == 0
    full = int(math.log2(max(w, h))) + 1          # chain down to 1x1
    to4x4 = max(1, int(math.log2(min(w, h))) - 1)  # chain stopping at 4 px on the short side
    mem = BYTES_PER_PIXEL.get(base, 4) * w * h * (4 / 3 if mips > 1 else 1) / 2**20
    issues = []
    if "SRGB" in fmt:
        issues.append("ERROR _SRGB format: CodeWalker DDS import maps only *_UNORM; re-export as UNORM")
    if "TYPELESS" in fmt or fmt.startswith("DXGI#"):
        issues.append("ERROR typeless/unknown DXGI format: re-export as BC1/BC3/BC7_UNORM")
    if not pow2:
        issues.append("ERROR size not power of two")
    if base.startswith("BC") and (w % 4 or h % 4):
        issues.append("ERROR BC format needs width/height divisible by 4")
    if mips == 1 and max(w, h) > 64:
        issues.append("ERROR no mipmaps (shimmer/moire at distance, wastes streaming memory)")
    elif base.startswith("BC") and mips > to4x4:
        issues.append(f"WARN {mips} mips go below 4x4; Sollumz clamps to {to4x4} (texconv -m {to4x4})")
    elif 1 < mips < to4x4:
        issues.append(f"WARN partial mip chain ({mips}/{to4x4})")
    if max(w, h) > 2048:
        issues.append("WARN larger than 2048 px")
    if mem > 16:
        issues.append("ERROR alone exceeds FiveM's 16 MiB per-asset warning threshold")
    if base in ("RGBA8", "BGRA8", "BGRX8") and not path.stem.lower().startswith("script_rt_"):
        issues.append("WARN uncompressed; use BC1/BC3/BC7 unless it is a script_rt_ texture")
    status = "FAIL" if any(i.startswith("ERROR") for i in issues) else "ok"
    print(f"{status:4} {path.name}: {w}x{h} {fmt} mips={mips} (full={full}, to4x4={to4x4}) ~{mem:.2f} MiB")
    for i in issues:
        print("     -", i)
    return status == "ok", mem


def main(args):
    files = []
    for a in args:
        p = pathlib.Path(a)
        files += sorted(p.rglob("*.dds")) if p.is_dir() else [p]
    ok, total = True, 0.0
    for f in files:
        try:
            good, mem = check(f)
            ok &= good
            total += mem
        except (OSError, ValueError, struct.error) as e:
            print(f"FAIL {f.name}: {e}")
            ok = False
    print(f"total ~{total:.2f} MiB for {len(files)} file(s); keep each .ytd well under 16 MiB")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1:] or ["."])
```

## make_ytd_xml.py: CodeWalker XML for a folder of DDS

Usage by suffix (`_n` NORMAL, `_s` SPECULAR, `_night`/`_em` EMISSIVE, else DIFFUSE). `UsageFlags UNK24`
mirrors common vanilla values (verify against an exported vanilla XML of the same kind).

```python
"""Write a CodeWalker <name>.ytd.xml for a folder of DDS files named like the YTD.
  python make_ytd_xml.py work/mymlo_facade      -> work/mymlo_facade.ytd.xml
CodeWalker RPF Explorer > Import XML on that file reads the DDS from the folder with the same
name (work/mymlo_facade/) and writes mymlo_facade.ytd (Gen8 or Gen9 = CodeWalker's game mode).
Size/mips/format come from the DDS files. Needs dds_check.py next to it."""
import pathlib
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from dds_check import read_header  # noqa: E402

CW_FORMAT = {"BC1": "D3DFMT_DXT1", "BC2": "D3DFMT_DXT3", "BC3": "D3DFMT_DXT5", "BC4": "D3DFMT_ATI1",
             "BC5": "D3DFMT_ATI2", "BC7": "D3DFMT_BC7", "BGRA8": "D3DFMT_A8R8G8B8", "RGBA8": "D3DFMT_A8B8G8R8"}


def usage(stem):
    s = stem.lower()
    if s.endswith("_n"):
        return "NORMAL"
    if s.endswith("_s"):
        return "SPECULAR"
    if s.endswith(("_night", "_em")):
        return "EMISSIVE"
    return "DIFFUSE"


def main(folder):
    folder = pathlib.Path(folder).resolve()
    items = []
    for dds in sorted(folder.glob("*.dds")):
        w, h, mips, fmt = read_header(dds)
        if fmt not in CW_FORMAT:
            raise SystemExit(f"{dds.name}: {fmt} cannot be imported by CodeWalker (run dds_check.py)")
        if dds.stem != dds.stem.lower():
            raise SystemExit(f"{dds.name}: use lower-case file names (texture name = file name)")
        items.append(f"""  <Item>
    <Name>{escape(dds.stem)}</Name>
    <Unk32 value="0" />
    <Usage>{usage(dds.stem)}</Usage>
    <UsageFlags>UNK24</UsageFlags>
    <ExtraFlags value="0" />
    <Width value="{w}" />
    <Height value="{h}" />
    <MipLevels value="{mips}" />
    <Format>{CW_FORMAT[fmt]}</Format>
    <FileName>{escape(dds.name)}</FileName>
  </Item>""")
    out = folder.parent / f"{folder.name}.ytd.xml"
    out.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<TextureDictionary>\n'
                   + "\n".join(items) + "\n</TextureDictionary>\n", encoding="utf-8")
    print(f"wrote {out} with {len(items)} textures")


if __name__ == "__main__":
    main(sys.argv[1])
```

## rsc_gen.py: is it Gen8 or Gen9, and is it in the right folder?

```python
"""Tell Gen8 (Legacy) from Gen9 (Enhanced) resources by their RSC7 header version.
  python rsc_gen.py <resource-folder>
Flags Gen9 files in stream/ and Gen8 files in stream_enhanced/. Versions from CodeWalker's
GetVersion(): ytd 13/5, ydr+ydd 165/159, yft 162/171, ypt 68/71 (Gen8/Gen9)."""
import pathlib
import struct
import sys

VERSIONS = {".ytd": (13, 5), ".ydr": (165, 159), ".ydd": (165, 159), ".yft": (162, 171), ".ypt": (68, 71)}


def generation(path):
    with open(path, "rb") as f:
        head = f.read(8)
    if len(head) < 8 or head[:4] != b"RSC7":
        return "no RSC7 header"
    version = struct.unpack_from("<i", head, 4)[0]
    gen8, gen9 = VERSIONS[path.suffix.lower()]
    return {gen8: "Gen8", gen9: "Gen9"}.get(version, f"unknown v{version}")


def main(root):
    bad = 0
    for p in sorted(pathlib.Path(root).rglob("*")):
        if p.suffix.lower() not in VERSIONS:
            continue
        gen = generation(p)
        parts = [s.lower() for s in p.parts]
        folder = "stream_enhanced" if "stream_enhanced" in parts else "stream" if "stream" in parts else "?"
        wrong = (folder == "stream" and gen == "Gen9") or (folder == "stream_enhanced" and gen == "Gen8")
        status = "WRONG" if wrong else "ok" if gen.startswith("Gen") else "BAD"
        bad += status != "ok"
        print(f"{status:5} {gen:14} {p}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
```
