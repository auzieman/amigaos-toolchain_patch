#!/usr/bin/env python3
"""Verify a captured fractal run and render an ASCII report and standalone SVG."""
import argparse
import base64
import colorsys
import hashlib
import json
from pathlib import Path
import re
import statistics
import struct
import zlib
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--run',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
r=json.loads((a.run/'receipt.json').read_text());raw=(a.run/'serial.log').read_bytes()
assert r['status']=='passed' and hashlib.sha256(raw).hexdigest()==r['serial_sha256']
assert b'FRACTAL_PASS identical escape-count images' in raw and b'FRACTAL_FAIL' not in raw
samples={mode:[] for mode in ['SOFT','SPE']};checks=[]
for mode,trial,us,checksum in re.findall(rb'FRACTAL_TIME mode=(SOFT|SPE) trial=(\d+) us=(\d+) checksum=(\d+)',raw):
 samples[mode.decode()].append((int(trial),int(us)));checks.append(int(checksum))
assert all(sorted(t for t,_ in v)==[1,2,3] for v in samples.values()) and len(set(checks))==1
pixels={mode.decode():bytes.fromhex(data.decode()) for mode,data in re.findall(rb'FRACTAL_PIXELS mode=(SOFT|SPE) ([0-9a-f]+)',raw)}
assert len(pixels['SOFT'])==128*96 and pixels['SOFT']==pixels['SPE']
checksum=2166136261
for n in pixels['SOFT']:checksum=((checksum^n)*16777619)&0xffffffff
assert checksum==checks[0]
medians={k:statistics.median(t for _,t in v) for k,v in samples.items()}
assert all(t>0 for v in samples.values() for _,t in v)
ratio=medians['SOFT']/medians['SPE']
a.output.mkdir(parents=True,exist_ok=False)
def png(data):
 rgb=bytearray()
 for y in range(96):
  rgb.append(0)
  for n in data[y*128:(y+1)*128]:
   color=(0,0,0) if n==96 else tuple(round(c*255) for c in colorsys.hsv_to_rgb((0.58+n*0.013)%1,0.82,0.96))
   rgb.extend(color)
 def chunk(kind,body):return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',128,96,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rgb))+chunk(b'IEND',b'')
for mode,data in pixels.items():(a.output/(mode.lower()+'.png')).write_bytes(png(data))
lines=['A1222 / e500v2 - MATCHED MANDELBROT DEMO','QEMU 10.0.13 TCG | Linux 6.12.113 | single render thread','128x96 | 96 iterations max | 1 warmup + 3 timed trials per path','', '+----------------------+------------------+------------------+', '| Metric               | Software FP      | SPE instructions |', '+----------------------+------------------+------------------+']
for trial in [1,2,3]:
 values=[dict(samples[k])[trial]/1000 for k in ['SOFT','SPE']]
 lines.append(f'| Trial {trial:<14} | {values[0]:>13.3f} ms | {values[1]:>13.3f} ms |')
lines += [f'| Median               | {medians["SOFT"]/1000:>13.3f} ms | {medians["SPE"]/1000:>13.3f} ms |','+----------------------+------------------+------------------+',f'SPE median speedup in this run: {ratio:.2f}x',f'Image match: PASS (all 12,288 escape counts; FNV32 {checksum:08x})','', 'Guest CLOCK_MONOTONIC time64; excludes boot and serial transfer.','Same kernel, grid and algorithm; explicit SPE vs GNU software FP.','QEMU timing is NOT physical A1222 performance.','No GL, libc or restored SPE compiler ABI is exercised.']
(a.output/'results-ascii.txt').write_text('\n'.join(lines)+'\n')
summary={'status':'passed','samples_us':{k:[u for _,u in sorted(v)] for k,v in samples.items()},'median_us':medians,'median_speedup':ratio,'images_equal':True,'pixel_sha256':hashlib.sha256(pixels['SOFT']).hexdigest(),'fnv32':f'{checksum:08x}','kernel_sha256':r['kernel_sha256'],'init_sha256':r['init_sha256'],'serial_sha256':r['serial_sha256'],'environment':'QEMU TCG e500v2; not physical A1222','scope':'Selected FP32 operations, no libc, GL or restored SPE ABI'}
(a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
uri='data:image/png;base64,'+base64.b64encode(png(pixels['SOFT'])).decode()
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="820" viewBox="0 0 1280 820">','<rect width="1280" height="820" fill="#111923"/>','<g font-family="DejaVu Sans,sans-serif" fill="#e8f0f5">','<text x="48" y="60" font-size="30" font-weight="bold">A1222 / SPE - Mandelbrot comparison</text>','<text x="48" y="94" font-size="17" fill="#aebdcb">QEMU 10.0.13 TCG / e500v2 / Linux 6.12.113 / single render thread</text>']
for x,mode,title,color in [(48,'SOFT','Software floating point','#ffbd69'),(664,'SPE','SPE instructions','#73e0ad')]:
 svg += [f'<text x="{x}" y="138" font-size="23" fill="{color}">{title}</text>',f'<image x="{x}" y="154" width="568" height="426" href="{uri}" style="image-rendering:pixelated"/>',f'<text x="{x}" y="620" font-size="30" fill="{color}">{medians[mode]/1000:.3f} ms median</text>',f'<rect x="{x}" y="640" width="{520*medians[mode]/medians["SOFT"]:.2f}" height="12" rx="6" fill="{color}"/>']
svg += [f'<text x="48" y="700" font-size="25" fill="#73e0ad">{ratio:.2f}x SPE speedup in this run - images match byte-for-byte</text>','<text x="48" y="735" font-size="16">128 x 96 pixels, max 96 iterations. One warmup and three measured trials per path.</text>','<text x="48" y="764" font-size="16" fill="#aebdcb">Guest render timing only. QEMU results are not physical A1222 performance.</text>','<text x="48" y="793" font-size="16" fill="#aebdcb">Explicit SPE vs GNU software FP; no GL, libc or restored compiler SPE ABI.</text>','</g></svg>']
(a.output/'comparison.svg').write_text('\n'.join(svg)+'\n')
print('\n'.join(lines))
