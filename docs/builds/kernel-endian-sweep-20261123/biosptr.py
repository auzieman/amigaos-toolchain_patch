import re,sys
# Pointer-based scan: variables assigned from a VBIOS image source, then any field or index
# read through that variable with no le*/unaligned helper in the statement. Catches fields
# that are not Hungarian-named (DIDT_REG[], entries[], ...). One-byte fields (uc*, *Num,
# *Rev) and header/struct-size plumbing are skipped.
SRC=r'smu_atom_get_data_table|ctx->bios|->bios\s*\+|GET_IMAGE|bios_get_image|CSTR\(|amdgpu_atom_parse_data_header|get_powerplay_table|cgs_atom_get_data_table'
SAFE=re.compile(r'le(16|32|64)_to_cpu|cpu_to_le|unaligned|sizeof|offsetof|&\s*\w+(->|\.)\w+|ATOM_GET|le16_add')
BYTE=re.compile(r'^(uc|s[A-Z]|as[A-Z]|b[A-Z])|Num|Rev|Id$|^c[A-Z]')
for path in sys.argv[1:]:
    src=re.sub(r'/\*.*?\*/',lambda m:'\n'*m.group(0).count('\n'),open(path,errors='replace').read(),flags=re.S)
    src=re.sub(r'//[^\n]*','',src)
    for fm in re.finditer(r'\n\w[^\n;]*\([^;{]*\)\s*\{(.*?)\n\}',src,flags=re.S):
        body=fm.group(1); base=src[:fm.start(1)].count('\n')+1
        tainted=set(re.findall(r'(\w+)\s*=\s*[^;=]*?(?:'+SRC+')',body))
        tainted|=set(m.group(1) for m in re.finditer(r'(\w+)\s*=\s*\([^)]*\*\)\s*\(?\s*\(?(?:char|u8|uint8_t)\s*\*\)?\s*\(?\s*(\w+)',body) if m.group(2) in tainted)
        sig=src[src.rfind('\n',0,fm.start(1)-1):fm.start(1)]
        ATYPE=r'(?:const\s+)?(?:struct\s+)?_?(?:ATOM|PPTable|atom)_?\w*\s*\*\s*(?:const\s+)?(\w+)'
        tainted|=set(re.findall(ATYPE,sig))|set(re.findall(r'(?:^|[;{]\s*)'+ATYPE+r'\s*[;=,]',body,flags=re.M))
        tainted-={'result','ret','r','i','j'}
        if not tainted: continue
        line=base;start=0
        for m in re.finditer(r'[;{}]',body):
            st=body[start:m.end()]; l0=line; line+=st.count('\n'); start=m.end()
            s=' '.join(st.split())
            if SAFE.search(s) or re.search(r'\b(if|while)\s*\(\s*!',s): continue
            rhs=s.split('=',1)[1] if re.search(r'[^=!<>]=[^=]',s) else s
            hits=[f for v in tainted for f in re.findall(r'\b'+v+r'\s*(?:->|\.)\s*(\w+)(?:\[[^\]]*\])?',rhs)+(['[]'] if re.search(r'\b'+v+r'\s*\[',rhs) else []) if not BYTE.search(f)]
            if hits: print(f'{path}:{l0}: [{",".join(sorted(set(hits)))}] {s[:140]}')
