from pathlib import Path
import subprocess,json,hashlib
w=Path('/srv/data1/tabor-build/linux-live-001/work/piglit-standard-20261109-001');r=json.loads((w/'launch.json').read_text());cmd=r['argv']
names=['python3-numpy_1%3a2.2.4+ds-1_amd64.deb','python3-numpy-dev_1%3a2.2.4+ds-1_amd64.deb','libblas3_3.12.1-6_amd64.deb','liblapack3_3.12.1-6_amd64.deb','libgfortran5_14.2.0-19_amd64.deb','libquadmath0_14.2.0-19_amd64.deb']
files={n:hashlib.sha256((Path('/var/cache/apt/archives')/n).read_bytes()).hexdigest() for n in names};(w/'native-tool-inputs.json').write_text(json.dumps({'files':files,'architecture':'amd64','purpose':'Piglit native Python generation dependencies only; no target Fortran build'},indent=2)+'\n')
cmd=[x.replace('tabor-piglit-standard-20261109-001','tabor-piglit-standard-20261109-002') for x in cmd]
i=cmd.index('--entrypoint');cmd[i:i]=['-v','/var/cache/apt/archives:/native-cache:ro']
script=cmd[-1];script=script.replace('meson setup "$w/waffle-build"','meson setup --reconfigure "$w/waffle-build"')
script=script.replace('set -e\n','set -e\napt-get -y --no-download install '+' '.join('/native-cache/'+n for n in names)+' > /work/piglit/native-tools.log 2>&1\n/usr/bin/python3 -c "import numpy,mako; print(numpy.__version__)" >> /work/piglit/native-tools.log\n',1)
cmd[-1]=script;r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch-002.json').write_text(json.dumps({'argv':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');print(r.stdout,r.stderr);r.check_returncode()
