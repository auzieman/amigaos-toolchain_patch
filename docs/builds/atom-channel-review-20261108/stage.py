"""R730-only isolated candidate; parent and accepted boot assets remain unchanged."""
from pathlib import Path
import difflib,hashlib,json,subprocess
parent=Path('/srv/data1/tabor-build/linux-live-001/work/polaris-powerplay-20261108-003')
review=Path('/srv/data1/tabor-build/source-review/atom-channel-review-20261108')
w=Path('/srv/data1/tabor-build/linux-live-001/work/atom-channel-20261108-002')
assert not w.exists(),'new candidate directory required'
assert json.loads((review/'tests.json').read_text())['status'].startswith('PASS')
assert hashlib.sha256((parent/'output/drivers/gpu/drm/amd/amdgpu/amdgpu.ko').read_bytes()).hexdigest()=='7067488b2b42329c262c8e6d65ae2c63c47c13a9370bfd88a84e302fa19db247'
w.mkdir();s=w/'source'
for n in ['source','output']:
 subprocess.run(['cp','-a','--reflink=auto',str(parent/n),str(w/n)],check=True)
patches=[Path('/srv/data1/tabor-build/source-review/dpm-contract-review-20261108/0018-polaris-dpm-prerequisite-errors.patch'),review/'0019-polaris-avfs-calibration-byte-order.patch',review/'0020-atomctrl-serialize-complete-clock-word.patch']
for p in patches:
 subprocess.run(['git','apply','--check',str(p)],cwd=s,check=True)
 subprocess.run(['git','apply',str(p)],cwd=s,check=True)
 (w/p.name).write_bytes(p.read_bytes())
changes=[]
def diff(rel,a,b):
 changes.append(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)))
 (s/rel).write_text(b)
rel='drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.c';a=(s/rel).read_text();b=a
b=b.replace('if (!hwmgr->avfs_supported)\n\t\treturn 0;', 'pr_info("SMU_CALIB avfs_supported=%u btc=%u\\n",\n\t\thwmgr->avfs_supported, smu_data->avfs_btc_param);\n\tif (!hwmgr->avfs_supported)\n\t\treturn 0;',1)
b=b.replace('efuse &= 0x00000001;', 'pr_info("SMU_CALIB efuse49=%08x feature_mask=%08x\\n",\n\t\tefuse, hwmgr->feature_mask);\n\tefuse &= 0x00000001;',1)
b=b.replace('\t\tpolaris10_avfs_event_mgr(hwmgr);','\t\tresult = polaris10_avfs_event_mgr(hwmgr);\n\t\tpr_info("SMU_CALIB event_result=%d\\n", result);',1)
# Capture whether the cold-start branch ran, without adding an SMC read.
needle='''	/* Only start SMC if SMC RAM is not running */
	if (!smu7_is_smc_ram_running(hwmgr) && hwmgr->not_vf) {'''
rep='''	bool smc_running = smu7_is_smc_ram_running(hwmgr);

	pr_info("SMU_CALIB smc_running=%u not_vf=%u\\n", smc_running, hwmgr->not_vf);
	/* Only start SMC if SMC RAM is not running */
	if (!smc_running && hwmgr->not_vf) {'''
assert needle in b;b=b.replace(needle,rep,1);diff(rel,a,b)
rel='drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.c';a=(s/rel).read_text();b=a
for name in ['atomctrl_get_engine_pll_dividers_ai','atomctrl_get_dfs_pll_dividers_vi']:
 start=b.index('int '+name+'(');end=b.index('\n}\n',start)+3;f=b[start:end]
 idx=f.index('\n\tresult = PP_INIT_CALL')
 f=f[:idx]+f'''
	if (hwmgr->chip_id == CHIP_POLARIS11)
		pr_info("ATOM_CLOCK {name} clock=%u request=%08x\\n",
			clock_value, get_unaligned_le32(&pll_patameters.ulClock));
'''+f[idx:]
 if name.endswith('_ai'):
  f=f.replace('if (0 == result) {','''if (0 == result) {
		if (hwmgr->chip_id == CHIP_POLARIS11)
			pr_info("ATOM_CLOCK ai fcw_int=%u fcw_frac=%u pll_range=%u ssc=%u\\n",
				le16_to_cpu(pll_patameters.usSclk_fcw_int),
				le16_to_cpu(pll_patameters.usSclk_fcw_frac),
				pll_patameters.ucSclkPllRange, pll_patameters.ucSscEnable);''',1)
 b=b[:start]+f+b[end:]
diff(rel,a,b)
p=w/'0021-polaris-clock-channel-evidence.patch';p.write_text(''.join(changes))
# Verify complete candidate patch application and record source identity.
receipt={'parent_module_sha256':'7067488b2b42329c262c8e6d65ae2c63c47c13a9370bfd88a84e302fa19db247','candidate':str(w),'patches':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in w.glob('*.patch')},'source_files_sha256':{r:hashlib.sha256((s/r).read_bytes()).hexdigest() for r in ['drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.c','drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.c','drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c']},'hardware_tested':False,'boot_assets_changed':False}
(w/'stage.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
