import json, subprocess
cc="/tools/bin/powerpc-linux-gnuspe-gcc"
macros=subprocess.check_output([cc,"-dM","-E","-"],input="",text=True)
opts=subprocess.check_output([cc,"-Q","--help=target"],text=True)
print(json.dumps({"macros":[l for l in macros.splitlines() if any(k in l for k in ["__SPE__","__powerpc__","__NO_FPRS__","__LONG_DOUBLE_128__","__LDBL_MANT_DIG__"])],"target_options":[l for l in opts.splitlines() if any(k in l for k in ["mabi=spe","mfloat-gprs","mlong-double","mcpu="])]},indent=2))
