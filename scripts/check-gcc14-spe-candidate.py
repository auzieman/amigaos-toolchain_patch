#!/usr/bin/env python3
"""Qualify selected candidate compiler behavior without installing an SDK.

Run on the build worker, normally inside the pinned native-tools container.
This is a freestanding C check, not libc/libgcc/C++ or system acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--binutils-prefix", default="powerpc-linux-gnu-")
    parser.add_argument("--qemu")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    compiler = args.compiler.resolve()
    source = Path(__file__).resolve().parents[1] / "bench/gcc14-spe-freestanding.c"
    loop = source.with_name("gcc14-spe-vector.c")
    flags = [f"-B{compiler.parent}/", "-mcpu=8548", "-mabi=spe", "-mspe",
             "-mfloat-gprs=double", "-mhard-float", "-mlong-double-128",
             "-ffreestanding", "-fno-builtin", "-fno-stack-protector",
             "-fno-pie", "-fno-asynchronous-unwind-tables", "-O2"]
    results = []

    def run(name, command, expected=0):
        process = subprocess.run([str(c) for c in command], capture_output=True,
                                 text=True, timeout=90)
        (out / (name + ".stdout.txt")).write_text(process.stdout)
        (out / (name + ".stderr.txt")).write_text(process.stderr)
        ok = process.returncode == expected if expected is not None else process.returncode != 0
        results.append({"check": name, "command": [str(c) for c in command],
                        "exit_code": process.returncode, "passed": ok})
        return process.stdout

    run("version", [compiler, "-dumpfullversion"])
    target = run("target", [compiler, "-dumpmachine"]).strip()
    results.append({"check": "target-tuple", "passed": target == "powerpc-linux-gnuspe"})
    run("assembly", [compiler, *flags, "-S", source, "-o", out / "probe.s"])
    run("object", [compiler, *flags, "-c", source, "-o", out / "probe.o"])
    vector_flags = [*flags, "-O3", "-fopt-info-vec-all=" + str(out / "vector-info.txt")]
    run("vector-loop", [compiler, *vector_flags, "-S", loop, "-o", out / "vector-loop.s"])
    run("vector-object", [compiler, *flags, "-O3", "-c", loop, "-o", out / "vector-loop.o"])
    alias_loop = out / "vector-alias-regression.c"
    alias_loop.write_text("void add(float *a, const float *b, const float *c, unsigned n)\n"
                          "{ for (unsigned i=0; i<n; ++i) a[i] = b[i] + c[i]; }\n")
    run("vector-alias-regression", [compiler, *flags, "-O3", "-S", alias_loop,
                                    "-o", out / "vector-alias-regression.s"])
    run("link", [args.binutils_prefix + "ld", "-static", "-e", "_start",
                 "--build-id=none", "-o", out / "probe", out / "probe.o", out / "vector-loop.o"])
    header = run("elf-header", [args.binutils_prefix + "readelf", "-h", out / "probe"])
    run("disassembly", [args.binutils_prefix + "objdump", "-d", out / "probe"])
    results.append({"check": "BE-PPC32-ELF", "passed": all(
        token in header for token in ("ELF32", "big endian", "PowerPC"))})
    assembly = (out / "probe.s").read_text() if (out / "probe.s").exists() else ""
    results.append({"check": "ordinary-C-emits-SPE-adds", "passed": all(
        re.search(r"\b" + op + r"\b", assembly) for op in ("efsadd", "efdadd"))})
    run("target-options", [compiler, *flags, "-Q", "--help=target", "-c", "-x", "c",
                           "/dev/null", "-o", out / "empty.o"])
    macros = run("macros", [compiler, *flags, "-dM", "-E", "-x", "c", "/dev/null"])
    results.append({"check": "SPE-data-model", "passed": all(token in macros for token in
                    ("#define __SPE__ 1", "#define __NO_FPRS__ 1",
                     "#define __SIZEOF_POINTER__ 4", "#define __SIZEOF_LONG_DOUBLE__ 16",
                     "#define __BYTE_ORDER__ __ORDER_BIG_ENDIAN__"))})
    default_params = run("default-params", [compiler, *flags, "-Q", "--help=params", "-c",
                                            "-x", "c", "/dev/null", "-o", out / "params.o"])
    explicit_params = run("override-params", [compiler, *flags,
                                              "--param=max-grow-copy-bb-insns=31", "-Q",
                                              "--help=params", "-c", "-x", "c", "/dev/null",
                                              "-o", out / "params-override.o"])
    def parameter(text):
        match = re.search(r"--param=max-grow-copy-bb-insns=\s+(\d+)", text)
        return int(match.group(1)) if match else None
    results.append({"check": "legacy-tuning-default-and-user-override",
                    "default": parameter(default_params), "override": parameter(explicit_params),
                    "passed": parameter(default_params) == 16 and parameter(explicit_params) == 31})
    run("reject-invalid-float-gprs", [compiler, *flags, "-mfloat-gprs=invalid-mode",
                                      "-S", source, "-o", out / "invalid.s"], expected=None)
    if args.qemu and (out / "probe").exists():
        output = run("qemu", [args.qemu, "-cpu", "e500v2", out / "probe"])
        results.append({"check": "qemu-selected-C-ABI", "passed":
                        "GCC14_SPE_FREESTANDING_PASS" in output})
    receipt = {"status": "passed" if all(r["passed"] for r in results) else "failed",
               "checks": results, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
               "vector_source_sha256": hashlib.sha256(loop.read_bytes()).hexdigest(),
               "compiler_sha256": hashlib.sha256(compiler.read_bytes()).hexdigest(),
               "limits": "Selected freestanding C only; full runtimes, fenv, signals, TLS, C++ and system validation remain separate"}
    (out / "result.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "checks": len(results),
                      "failed": [r["check"] for r in results if not r["passed"]]}))
    return int(receipt["status"] != "passed")


if __name__ == "__main__":
    raise SystemExit(main())
