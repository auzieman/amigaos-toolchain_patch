#!/usr/bin/env python3
"""Capture a loopback RFB3.8 raw framebuffer to PNG with standard library only."""
import socket,struct
from pathlib import Path
import argparse,zlib
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
s=socket.create_connection(('127.0.0.1',a.port),timeout=5);s.settimeout(10)
def get(n):
 out=b''
 while len(out)<n:
  b=s.recv(n-len(out));assert b;out+=b
 return out
assert get(12).startswith(b'RFB ');s.sendall(b'RFB 003.008\n')
types=get(get(1)[0]);assert 1 in types;s.sendall(b'\x01');assert get(4)==b'\0'*4
s.sendall(b'\x01');header=get(24);w,h=struct.unpack('>HH',header[:4]);get(struct.unpack('>I',header[20:24])[0])
s.sendall(b'\0\0\0\0'+struct.pack('>BBBBHHHBBBxxx',32,24,0,1,255,255,255,16,8,0))
s.sendall(b'\x02\0\0\x01'+struct.pack('>i',0));s.sendall(b'\x03\0'+struct.pack('>HHHH',0,0,w,h))
image=bytearray(w*h*3)
while True:
 t=get(1)[0]
 if t==2:continue
 if t==3:get(3);get(struct.unpack('>I',get(4))[0]);continue
 assert t==0,t
 n=struct.unpack('>H',get(3)[1:])[0]
 for i in range(n):
  xx,yy,ww,hh,enc=struct.unpack('>HHHHi',get(12));assert enc==0,enc
  data=get(ww*hh*4)
  for row in range(hh):
   line=data[row*ww*4:(row+1)*ww*4];rgb=bytearray(ww*3)
   rgb[0::3]=line[2::4];rgb[1::3]=line[1::4];rgb[2::3]=line[0::4]
   image[((yy+row)*w+xx)*3:((yy+row)*w+xx+ww)*3]=rgb
 if n:break
def chunk(kind,data):
 return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
rows=b''.join(b'\0'+image[y*w*3:(y+1)*w*3] for y in range(h))
a.output.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows,1))+chunk(b'IEND',b''))
print('Captured',w,h,'to',a.output)
