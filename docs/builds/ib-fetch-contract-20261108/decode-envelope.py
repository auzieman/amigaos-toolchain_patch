#!/usr/bin/env python3
"""Decode CPU-captured LE GFX8 packet bytes; never opens a device or submits work."""
import argparse,json,re,struct
NAMES={0x10:'NOP',0x22:'COND_EXEC',0x37:'WRITE_DATA',0x3c:'WAIT_REG_MEM',0x3f:'INDIRECT_BUFFER',0x43:'SURFACE_SYNC',0x47:'EVENT_WRITE_EOP',0x8b:'SWITCH_BUFFER'}
def decode(words):
 result=[];i=0
 while i<len(words):
  header=words[i];kind=header>>30
  if kind==2:size=1
  elif kind in (0,3):size=((header>>16)&0x3fff)+2
  else:raise ValueError('Invalid packet type at word '+str(i))
  if i+size>len(words):raise ValueError('Truncated/corrupt packet at word '+str(i))
  row={'word':i,'type':kind,'size_dw':size,'words':[f'{x:08x}' for x in words[i:i+size]]}
  if kind==3:
   op=(header>>8)&255;row['opcode']=f'{op:02x}';row['name']=NAMES.get(op,'OTHER')
   if op==0x3f and size==4:row.update(address=f'{((words[i+2]&65535)<<32)|(words[i+1]&~3):012x}',swap=words[i+1]&3,length_dw=words[i+3]&0xfffff)
   if op==0x22 and size==5:row.update(predicate_address=f'{(words[i+2]<<32)|words[i+1]:012x}',skip_dw=words[i+4],skip_target=i+size+words[i+4])
  result.append(row);i+=size
 return result
def captured(text,label):
 rows={}
 for m in re.finditer(label+r' word=(\d+) bytes=((?:[0-9a-fA-F]{2}[ ]?){4})',text):
  i=int(m[1]);b=bytes.fromhex(m[2]);assert len(b)==4
  if i in rows:raise ValueError('Multiple snapshots: select exactly one submission')
  rows[i]=int.from_bytes(b,'little')
 if not rows:return []
 if sorted(rows)!=list(range(len(rows))):raise ValueError('Missing captured words')
 return [rows[i] for i in range(len(rows))]
def selftest():
 # Source-independent PM4 framing controls: header word count excludes two DWs.
 good=[0xc0034300,0xabcdef01,0xffffffff,0,10,0xc0023f00,0x0094e000,0xff,5]
 assert [x['name'] for x in decode(good)]==['SURFACE_SYNC','INDIRECT_BUFFER']
 assert decode(good)[1]['address']=='00ff0094e000'
 for bad in [good[:-1],[0x40000000]]:
  try:decode(bad)
  except ValueError:pass
  else:raise AssertionError('Malformed stream accepted')
 raw='\n'.join(f'IB_RING word={i} bytes={struct.pack("<I",x).hex(" ")}' for i,x in enumerate(good))
 assert captured(raw,'IB_RING')==good
 swapped=[int.from_bytes(x.to_bytes(4,'little'),'big') for x in good]
 try:decode(swapped)
 except ValueError:pass
 else:raise AssertionError('Swapped test stream accepted')
 print('PASS: framing, LE byte reconstruction, IB address, truncation and byte-swap negative controls')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('log',nargs='?');p.add_argument('--selftest',action='store_true');a=p.parse_args()
 if a.selftest:selftest()
 else:
  text=open(a.log).read();print(json.dumps({k:decode(captured(text,k)) for k in ['IB_RING','IB_PAYLOAD']},indent=2))
