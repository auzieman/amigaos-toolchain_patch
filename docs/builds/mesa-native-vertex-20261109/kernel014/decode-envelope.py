"""Decode kernel014 CPU-captured GFX envelopes; never accesses hardware."""
import argparse
import importlib.util
import json
import re
import struct
from pathlib import Path


def decode(text):
    envelopes = {}
    for line in text.splitlines():
        match = re.search(r'SUBMIT_ENV(?:_(FENCE|IB|DW))? (.*)', line)
        if not match:
            continue
        kind, body = match.groups()
        fields = dict(re.findall(r'(\w+)=([^ ]+)', body))
        entry = envelopes.setdefault(int(fields['id']), {'words': {}, 'ibs': []})
        if kind in ('DW', 'FENCE'):
            raw = re.search(r'bytes=((?:[0-9a-fA-F]{2} ){3}[0-9a-fA-F]{2})', body)
            if not raw:
                raise ValueError('missing four raw bytes: '+line)
            value = int.from_bytes(bytes.fromhex(raw[1]), 'little')
            if kind == 'DW':
                index = int(fields['n'])
                if index in entry['words']:
                    raise ValueError('duplicate word')
                entry['words'][index] = value
            else:
                entry['fence'] = {'address': int(fields['addr'],16), 'decoded': int(fields['decoded']), 'raw_le': value}
                if value != entry['fence']['decoded']:
                    raise ValueError('kernel fence decode disagrees with raw bytes')
        elif kind == 'IB':
            entry['ibs'].append({key: int(fields[key],16 if key in ('addr','flags') else 10) for key in ('n','addr','dw','flags','le')})
        else:
            entry['metadata'] = fields
    spec = importlib.util.spec_from_file_location('framing', Path(__file__).resolve().parent.parent/'check-packet-bounds.py')
    framing=importlib.util.module_from_spec(spec);spec.loader.exec_module(framing)
    output=[]
    for identifier, entry in sorted(envelopes.items()):
        meta=entry.get('metadata', {})
        expected=int(meta.get('count',-1))
        if set(entry['words']) != set(range(expected)):
            output.append({'id':identifier,'status':'INCOMPLETE','received':len(entry['words']),'expected':expected});continue
        words=[entry['words'][i] for i in range(expected)]
        packets=framing.decode(struct.pack('<%dI'%len(words),*words))
        relevant=[]
        for packet in packets:
            offset=packet['offset_dw'];p=words[offset:offset+packet['size_dw']];op=packet.get('opcode')
            if op in ('0x3f','0x33') and len(p)==4:
                addr=(p[1]&~3)|((p[2]&0xffff)<<32)
                relevant.append({'offset':offset,'kind':'IB','address':hex(addr),'swap':p[1]&3,'length_dw':p[3]&0xfffff,'vmid':(p[3]>>24)&15,'valid':(p[3]>>23)&1,'chain':(p[3]>>20)&1,'matches_logged_ib':any(i['addr']==addr and i['dw']==(p[3]&0xfffff) for i in entry['ibs'])})
            elif op=='0x3c' and len(p)==7:
                addr=p[2]|(p[3]<<32)
                relevant.append({'offset':offset,'kind':'WAIT','function':p[1]&7,'space':(p[1]>>4)&3,'operation':(p[1]>>6)&3,'engine':(p[1]>>8)&3,'address_or_register':hex(addr),'reference':hex(p[4]),'mask':hex(p[5]),'poll':p[6],'targets_kernel_fence':addr==entry.get('fence',{}).get('address') and ((p[1]>>4)&3)==1})
            elif op=='0x47' and len(p)==6:
                relevant.append({'offset':offset,'kind':'EOP','address':hex((p[2]&~3)|((p[3]&0xffff)<<32)),'data_select':(p[3]>>29)&7,'interrupt_select':(p[3]>>24)&3,'value':hex(p[4]|(p[5]<<32)),'event':p[1]&63,'event_index':(p[1]>>8)&15})
        output.append({'id':identifier,'status':'TRUNCATED' if meta.get('truncated')=='1' else 'DECODED','metadata':meta,'fence':entry.get('fence'),'ibs':entry['ibs'],'packets':relevant})
    return {'scope':'CPU-published packet fields; no proof of GPU fetch/progress','envelopes':output}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('log',type=Path);args=parser.parse_args()
    print(json.dumps(decode(args.log.read_text()),indent=2))
