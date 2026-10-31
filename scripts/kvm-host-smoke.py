#!/usr/bin/env python3
"""Execute a diskless x86 ROM under KVM and check VMX exposure to that guest."""
import json
import pathlib
import socket
import subprocess
import tempfile
import time

ROM = r'''
.code16
.global _start
_start:
 cli
 push %cs
 pop %ds
 mov $1, %eax
 cpuid
 bt $5, %ecx
 jnc failed
 mov $message, %si
print:
 lodsb
 test %al, %al
 jz done
 out %al, $0xe9
 jmp print
done:
 mov $0x10, %ax
 out %ax, $0xf4
 hlt
failed:
 mov $0x11, %ax
 out %ax, $0xf4
 hlt
message: .asciz "KVM_GUEST_VMX_EXPOSED\n"
.org 0xfff0
 ljmp $0xf000, $_start
.org 0x10000
'''


def main():
    with tempfile.TemporaryDirectory(prefix="tabor-kvm-") as name:
        root = pathlib.Path(name)
        (root / "rom.s").write_text(ROM)
        subprocess.run(["as", "--32", "-o", str(root / "rom.o"), str(root / "rom.s")], check=True)
        subprocess.run(["ld", "-m", "elf_i386", "-Ttext", "0", "--oformat", "binary",
                        "-o", str(root / "rom.bin"), str(root / "rom.o")], check=True)
        command = ["qemu-system-x86_64", "-machine", "q35", "-accel", "kvm",
                   "-cpu", "host", "-m", "128M", "-smp", "1", "-nodefaults",
                   "-display", "none", "-nic", "none", "-no-reboot", "-S",
                   "-bios", str(root / "rom.bin"), "-qmp", f"unix:{root}/qmp,server=on,wait=off",
                   "-debugcon", f"file:{root}/guest.log",
                   "-device", "isa-debug-exit,iobase=0xf4,iosize=0x04"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            with socket.socket(socket.AF_UNIX) as sock:
                sock.settimeout(10)
                deadline = time.monotonic() + 10
                while not (root / "qmp").exists():
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError("QEMU did not open QMP")
                    time.sleep(0.05)
                sock.connect(str(root / "qmp"))
                stream = sock.makefile("rwb", buffering=0)
                json.loads(stream.readline())

                def execute(command):
                    stream.write(json.dumps({"execute": command}).encode() + b"\n")
                    while True:
                        result = json.loads(stream.readline())
                        if "error" in result:
                            raise RuntimeError(result)
                        if "return" in result:
                            return result["return"]

                execute("qmp_capabilities")
                kvm = execute("query-kvm")
                assert kvm["enabled"] and kvm["present"], kvm
                execute("cont")
            stdout, stderr = process.communicate(timeout=10)
            guest = (root / "guest.log").read_text()
            receipt = {"qemu_version": subprocess.check_output(
                ["qemu-system-x86_64", "--version"], text=True).splitlines()[0],
                "query_kvm": kvm, "guest_output": guest, "exit_code": process.returncode,
                "stderr": stderr.decode(errors="replace"),
                "nested_guest_boot_tested": False}
            print(json.dumps(receipt, indent=2))
            assert process.returncode == 33 and "KVM_GUEST_VMX_EXPOSED" in guest
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()


if __name__ == "__main__":
    main()
