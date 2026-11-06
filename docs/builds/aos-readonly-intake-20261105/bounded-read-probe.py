"""Bounded READ-only SFTP block-header probe; never opens a write handle."""
import subprocess,struct,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'modular-usb-update-20261105-001'))
from board_access import base
u32=lambda b,o:struct.unpack_from('>I',b,o)[0]
string=lambda b:struct.pack('>I',len(b))+b
p=subprocess.Popen(['ssh',*base,'root@192.168.1.249','-s','sftp'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
def exact(n):
 b=b''
 while len(b)<n:
  x=p.stdout.read(n-len(b));assert x,'SFTP ended';b+=x
 return b
def send(b):p.stdin.write(struct.pack('>I',len(b))+b);p.stdin.flush()
def recv():
 n=struct.unpack('>I',exact(4))[0];assert n<1024*1024;return exact(n)
send(b'\x01'+struct.pack('>I',3));assert recv()[0]==2
seq=0
def req(t,b):
 global seq
 seq+=1;send(bytes([t])+struct.pack('>I',seq)+b);r=recv();assert u32(r,1)==seq;return r
r=req(3,string(b'/dev/sda')+struct.pack('>II',1,0));assert r[0]==102,r
handle=r[9:9+u32(r,5)]
read_total=0
def read(offset,size):
 global read_total
 assert size<=65536 and read_total+size<=1024*1024
 r=req(5,string(handle)+struct.pack('>QI',offset,size));assert r[0]==103,r
 b=r[9:9+u32(r,5)];assert len(b)==size;read_total+=size;return b
def valid(b,magic):
 assert b[:4]==magic;count=u32(b,4);assert 0<count<=len(b)//4
 assert sum(struct.unpack('>'+str(count)+'I',b[:count*4]))&0xffffffff==0
try:
 first=read(0,65536);idx=next(i for i in range(16) if first[i*512:i*512+4]==b'RDSK');rdb=first[idx*512:(idx+1)*512];valid(rdb,b'RDSK');bs=u32(rdb,16);assert 512<=bs<=65536
 blk=u32(rdb,28);parts=[];seen=set()
 while blk not in [0,0xffffffff] and len(parts)<16:
  assert blk not in seen and blk*bs<240057409536;seen.add(blk)
  data=read(blk*bs,512);valid(data,b'PART');env=struct.unpack_from('>17I',data,128)
  start=env[9]*env[3]*env[5]*bs;size=(env[10]-env[9]+1)*env[3]*env[5]*bs
  assert 0<size<=240057409536 and start+size<=240057409536
  header=read(start,512)
  parts.append({'name':data[37:37+min(data[36],31)].decode('latin1'),'start_bytes':start,'size_bytes':size,'dos_type_hex':hex(env[16]),'header_magic_hex':header[:16].hex(),'filesystem_block_bytes':env[1]*4})
  blk=u32(data,16)
 result={'device':'/dev/sda','read_only':True,'rdb_block_bytes':bs,'bytes_read':read_total,'partitions':parts}
 Path(__file__).with_name('partition-metadata.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
finally:
 req(4,string(handle));p.stdin.close();p.wait(timeout=5)
