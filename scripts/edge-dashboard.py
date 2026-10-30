#!/usr/bin/env python3
"""Small ANSI host/emulator dashboard; never presents host metrics as guest data."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage', type=Path, default=Path('/var/lib/bkc/tabor-qemu/attempt-005'))
base = parser.parse_args().stage
def cpu():
    values = list(map(int, Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))
    return sum(values), values[3] + values[4]
previous = cpu()
try:
    while True:
        time.sleep(2)
        current = cpu()
        delta = current[0] - previous[0]
        usage = 100 * (1 - (current[1] - previous[1]) / delta) if delta else 0
        previous = current
        mem = dict((line.split(':')[0], int(line.split()[1])) for line in Path('/proc/meminfo').read_text().splitlines())
        receipt = base / 'results/boot-001/receipt.json'
        stage = 'KERNEL BUILD / waiting for emulator boot'
        if (base / 'results/boot-001/serial.log').exists():
            stage = 'QEMU BOOT TEST RUNNING'
        if receipt.exists():
            try:
                stage = 'BOOT TEST: ' + json.loads(receipt.read_text())['status'].upper()
            except json.JSONDecodeError:
                stage = 'BOOT TEST: writing final receipt'
        rows = ['A1222 / SPE LAB — EDGE TEST MONITOR', time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                '', stage, '', f'EDGE HOST CPU: {usage:5.1f}% (all host workloads)',
                f'EDGE HOST RAM: {(mem["MemTotal"]-mem["MemAvailable"])/1048576:.2f} / {mem["MemTotal"]/1048576:.2f} GiB',
                f'EDGE ROOT FREE: {shutil.disk_usage(base).free/1024**3:.2f} GiB', '',
                'ISOLATED CONTAINERS (100% CPU = one host core):']
        try:
            result = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{.Name}} | CPU {{.CPUPerc}} | RAM {{.MemUsage}}'], capture_output=True, text=True, timeout=8)
            rows += [line for line in result.stdout.splitlines() if line.startswith('tabor-qemu-')] or ['No active build/VM container']
        except subprocess.TimeoutExpired:
            rows += ['Container metrics temporarily unavailable']
        spe = 'Selected SPE arithmetic: NOT TESTED'
        spe_receipt = base / 'results/boot-spe-001/receipt.json'
        if spe_receipt.exists():
            try:
                passed = json.loads(spe_receipt.read_text()).get('selected_spe_arithmetic_passed', False)
                spe = 'Selected SPE arithmetic: ' + ('PASS (single/double add)' if passed else 'FAILED / inspect log')
            except json.JSONDecodeError:
                spe = 'Selected SPE arithmetic: writing receipt'
        rows += ['', 'Guest CPU utilisation: not instrumented yet', spe,
                 'Full SPE ABI / modern glibc: NOT VALIDATED', 'Physical A1222 / AMD graphics: NOT TESTED',
                 '', 'Serial console is in the companion terminal.', 'Ctrl-C closes this monitor.']
        print('\033[H\033[2J' + '\n'.join(rows), flush=True)
except KeyboardInterrupt:
    print('\nMonitor stopped.')
