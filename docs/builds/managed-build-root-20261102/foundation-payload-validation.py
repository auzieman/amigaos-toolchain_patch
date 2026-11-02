from pathlib import Path
import subprocess,tarfile,json,hashlib
base=Path("/base/work");results={}
for name in ["attr","libxcrypt","fribidi","pixman","mtdev"]:
 r=json.loads((base/("debian-"+name+"-401")/"receipt.json").read_text());assert r["status"]=="debian-packages-built-not-target-installed"
 found=[]
 for filename,info in r["packages"].items():
  p=base/("debian-"+name+"-401")/filename;assert hashlib.sha256(p.read_bytes()).hexdigest()==info["sha256"]
  proc=subprocess.Popen(["dpkg-deb","--fsys-tarfile",str(p)],stdout=subprocess.PIPE)
  with tarfile.open(fileobj=proc.stdout,mode="r|") as tar:
   for member in tar:
    if not member.isfile():continue
    h=tar.extractfile(member).read(20)
    if h[:4]!=b"\x7fELF":continue
    assert h[4:6]==bytes([1,2]) and int.from_bytes(h[18:20],"big")==20,(name,filename,member.name,h.hex())
    found.append({"package":filename,"file":member.name,"elf":"ELF32 big-endian PowerPC"})
  assert proc.wait()==0
 assert found,name
 results[name]=found
print(json.dumps({"status":"five-source-elf-payload-validation-passed","target_execution":False,"source_outputs":results},indent=2))
