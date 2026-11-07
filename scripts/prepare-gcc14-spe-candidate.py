#!/usr/bin/env python3
"""Reconstruct the experimental GCC14 backend from verified extracted sources.

Run on the build server against a disposable, unmodified GCC14 source tree.
This prepares sources only; it does not install or qualify an SDK.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gcc8", type=Path, required=True)
    parser.add_argument("--gcc14", type=Path, required=True)
    args = parser.parse_args()
    patches = Path(__file__).resolve().parents[1] / "patches/gcc/gcc14-spe-candidate"
    manifest = json.loads((patches / "imports.json").read_text())
    files = manifest["files"]
    renames = {Path(f["source"]).name: Path(f["destination"]).name
               for f in files if f["source"].endswith(".c")}
    prepared = []
    # Validate every input and destination before making any changes.
    for item in files:
        source = args.gcc8 / item["source"]
        destination = args.gcc14 / item["destination"]
        data = source.read_bytes()
        if digest(data) != item["source_sha256"]:
            raise SystemExit(f"Reference hash mismatch: {source}")
        if destination.exists():
            raise SystemExit(f"Requires a fresh GCC14 tree: {destination}")
        for old, new in renames.items():
            data = data.replace(old.encode(), new.encode())
        if digest(data) != item["output_sha256"]:
            raise SystemExit(f"Import transformation mismatch: {source}")
        prepared.append((source, destination, data))
    for source, destination, data in prepared:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        shutil.copymode(source, destination)
    for name in (patches / "series").read_text().splitlines():
        if name and not name.startswith("#"):
            subprocess.run(["patch", "--batch", "--forward", "--no-backup-if-mismatch", "-p1"],
                           cwd=args.gcc14, input=(patches / name).read_bytes(), check=True)
    # Debian's DFSG tarball deliberately omits the GFDL manual. Use its
    # existing build adaptation, rather than inventing target hook docs.
    subprocess.run(["patch", "--batch", "--forward", "--no-backup-if-mismatch", "-p2"],
                   cwd=args.gcc14,
                   input=(patches / "debian-gcc-gfdl-build.diff").read_bytes(), check=True)
    backend = args.gcc14.resolve() / "gcc/config/powerpcspe"
    generated = subprocess.check_output(["sh", str(backend / "genopt.sh"), str(backend)])
    (backend / "powerpcspe-tables.opt").write_bytes(generated)
    print(f"Prepared {len(files)} verified imports; experimental compiler, not an accepted SDK.")


if __name__ == "__main__":
    main()
