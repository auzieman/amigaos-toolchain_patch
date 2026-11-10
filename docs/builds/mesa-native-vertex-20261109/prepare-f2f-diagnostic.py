from pathlib import Path
import subprocess,json,hashlib
base=Path('/srv/data1/tabor-build/linux-live-001/work');parent=base/'native-vertex-contract-20261109-001';w=base/'f2f-contract-20261109-001';w.mkdir(exist_ok=False)
for name in ('mesa-source','build'):subprocess.run(['cp','-a','--reflink=auto',str(parent/name),str(w/name)],check=True)
p=w/'mesa-source/src/amd/compiler/aco_instruction_selection.cpp';s=p.read_text();needle='         isel_err(&instr->instr, "Unimplemented NIR instr bit size");\n      }\n      break;\n   }\n   case nir_op_f2f64:'
assert s.count(needle)==1
replacement='         fprintf(stderr, "TABOR_F2F32 source_bits=%u dest_bits=%u components=%u\\n", instr->src[0].src.ssa->bit_size, instr->def.bit_size, instr->src[0].src.ssa->num_components);\n         nir_print_instr(instr->src[0].src.ssa->parent_instr, stderr);\n         fprintf(stderr, "\\n");\n         isel_err(&instr->instr, "Unimplemented NIR instr bit size");\n      }\n      break;\n   }\n   case nir_op_f2f64:'
p.write_text(s.replace(needle,replacement))
subprocess.run(['cp',str(parent/'3d-build.exit'),str(w/'3d-build.exit')],check=True)
print('Private diagnostic source prepared')
