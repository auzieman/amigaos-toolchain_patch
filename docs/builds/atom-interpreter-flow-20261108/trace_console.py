"""R730: retain source anchors for the actual legacy fbdev/console call chain."""
from pathlib import Path
import re,json,hashlib
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-007/source');W=Path('/srv/data1/tabor-build/source-review/atom-interpreter-flow-20261108')
groups={
 'drivers/gpu/drm/amd/amdgpu/amdgpu_drv.c':['amdgpu_pci_probe'],
 'drivers/gpu/drm/amd/amdgpu/amdgpu_kms.c':['amdgpu_driver_load_kms'],
 'drivers/gpu/drm/amd/amdgpu/amdgpu_device.c':['amdgpu_device_init','amdgpu_device_ip_init','amdgpu_device_ip_late_init','amdgpu_device_delayed_init_work_handler'],
 'drivers/gpu/drm/drm_fbdev_ttm.c':['drm_fbdev_ttm_setup','drm_fbdev_ttm_client_hotplug','drm_fbdev_ttm_driver_fbdev_probe','drm_fbdev_ttm_helper_fb_dirty','drm_fbdev_ttm_damage_blit','drm_fbdev_ttm_damage_blit_real'],
 'drivers/gpu/drm/drm_client.c':['drm_client_register','drm_client_framebuffer_create'],
 'drivers/gpu/drm/drm_fb_helper.c':['drm_fb_helper_initial_config','__drm_fb_helper_initial_config_and_unlock','drm_fb_helper_single_fb_probe','drm_fb_helper_fill_info','drm_fb_helper_set_par','drm_fb_helper_deferred_io','drm_fb_helper_damage_area'],
 'drivers/gpu/drm/drm_client_modeset.c':['drm_client_modeset_probe','drm_client_modeset_commit_legacy'],
 'drivers/gpu/drm/drm_crtc.c':['drm_mode_set_config_internal'],
 'drivers/gpu/drm/drm_crtc_helper.c':['drm_crtc_helper_set_config','drm_crtc_helper_set_mode'],
 'drivers/gpu/drm/amd/amdgpu/amdgpu_display.c':['amdgpu_display_crtc_set_config'],
 'drivers/gpu/drm/amd/amdgpu/amdgpu_gem.c':['amdgpu_mode_dumb_create'],
 'drivers/gpu/drm/amd/amdgpu/dce_v11_0.c':['dce_v11_0_sw_init','dce_v11_0_hw_init','dce_v11_0_crtc_mode_fixup','dce_v11_0_crtc_mode_set','dce_v11_0_crtc_do_set_base','dce_v11_0_crtc_commit','dce_v11_0_encoder_prepare','dce_v11_0_encoder_mode_set','dce_v11_0_encoder_commit'],
 'drivers/gpu/drm/amd/amdgpu/atombios_crtc.c':['amdgpu_atombios_crtc_program_pll','amdgpu_atombios_crtc_set_dce_clock','amdgpu_atombios_crtc_set_dtd_timing'],
 'drivers/gpu/drm/amd/amdgpu/atom.c':['amdgpu_atom_execute_table','amdgpu_atom_execute_table_locked','atom_get_src_int','atom_put_dst'],
 'drivers/video/fbdev/core/fbmem.c':['register_framebuffer','do_register_framebuffer'],
 'drivers/video/fbdev/core/fbcon.c':['fbcon_fb_registered','fbcon_init','fbcon_putcs'],
 'drivers/video/fbdev/core/bitblit.c':['bit_putcs'],
 'drivers/video/fbdev/core/sysimgblt.c':['sys_imageblit','fast_imageblit','slow_imageblit'],
}
rows=[];missing=[]
for file,names in groups.items():
 t=(S/file).read_text()
 for name in names:
  m=re.search(r'\b'+name+r'\s*\([^;{}]*\)\s*\{',t)
  if not m:missing.append([file,name]);continue
  a=m.start();i=t.index('{',m.start())+1;d=1
  while d:d+=(t[i]=='{')-(t[i]=='}');i+=1
  rows.append(dict(function=name,file=file,line=t[:a].count('\n')+1,body_sha256=hashlib.sha256(t[a:i].encode()).hexdigest()))
assert not missing,missing
(W/'console-source-chain.json').write_text(json.dumps({'source_root':str(S),'functions':rows,'hardware_accessed':False,'note':'Source anchors for reviewed direct and callback handoffs; not a runtime execution trace.'},indent=2)+'\n');print('Source anchors:',len(rows))
