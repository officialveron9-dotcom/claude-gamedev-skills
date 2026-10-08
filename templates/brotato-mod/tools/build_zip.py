"""Builds the Workshop zip for one mod: root entries are mods-unpacked/ (and .import/ for shipped assets).
Run from the repo root that contains mods-unpacked/:
    python tools/build_zip.py <Namespace-ModName> <version> [asset-prefix]
Deterministic order, forward slashes, no .md files. Same layout as the brotato-modding skill describes."""
import os
import sys
import zipfile

if len(sys.argv) < 3:
    sys.exit("usage: build_zip.py <Namespace-ModName> <version> [asset-prefix]")
mod_id, version = sys.argv[1], sys.argv[2]
asset_prefix = sys.argv[3] if len(sys.argv) > 3 else None
src = os.path.join("mods-unpacked", mod_id)
if not os.path.isdir(src):
    sys.exit(f"missing folder: {src}")
if not os.path.isfile(os.path.join(src, "manifest.json")):
    sys.exit(f"missing manifest.json in {src}")
os.makedirs("dist", exist_ok=True)
out = f"dist/{mod_id}-{version}.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(src):
        dirs.sort()
        for f in sorted(files):
            if f.endswith(".md") or f.startswith("."):
                continue
            p = os.path.join(root, f)
            z.write(p, p.replace(os.sep, "/"))
    if asset_prefix and os.path.isdir(".import"):
        for f in sorted(os.listdir(".import")):
            if f.startswith(asset_prefix):
                z.write(os.path.join(".import", f), ".import/" + f)
print(out)
