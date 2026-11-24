import re,sys
# Statement-level scan: raw reads of ATOM/SMC Hungarian fields (ulXxx/usXxx) used as values
# without le16/le32_to_cpu (or SMC/unaligned helpers) in the same statement.
SAFE=re.compile(r'le(16|32|64)_to_cpu|cpu_to_le|be(16|32)_to_cpu|cpu_to_be|unaligned|PP_(HOST_TO_SMC|SMC_TO_HOST)|CONVERT_FROM|SMC_TO_HOST|HOST_TO_SMC|sizeof|offsetof')
REF=r'(?:->|\.)((?:ul|us)[A-Z]\w*)'
for path in sys.argv[1:]:
    src=open(path,errors='replace').read()
    src=re.sub(r'/\*.*?\*/',lambda m:'\n'*m.group(0).count('\n'),src,flags=re.S)
    line=1;start=0
    for m in re.finditer(r'[;{}]',src):
        st=src[start:m.end()]; l0=line; line+=st.count('\n'); start=m.end()
        if not re.search(REF,st) or SAFE.search(st): continue
        s=' '.join(st.split())
        rhs=s.split('=',1)[1] if re.search(r'[^=!<>]=[^=]',s) else s
        refs=[r for r in re.findall(REF,rhs)]
        if not refs: continue
        if re.fullmatch(r'.*(!=|==)\s*0\s*\)?\s*[;{]?',s) or re.search(r'(if|while)\s*\(\s*!?\s*\w+(->|\.)\w+(\s*(!=|==)\s*0)?\s*\)',s): continue
        print(f'{path}:{l0}: {s[:150]}')
