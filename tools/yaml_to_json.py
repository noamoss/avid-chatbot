#!/usr/bin/env python
import os
import re
from pathlib import Path
from hashlib import md5
from slugify import slugify
import glob
import yaml
import json
import requests
import sys

def calc_hash(s):
    ret = md5(s.encode('utf8')).hexdigest()[:10]
    return ret

HEB = re.compile('[א-ת]')
def has_hebrew(s):
    return len(HEB.findall(s)) > 0

def get_field(x, f):
    parts = f.split('.')
    while len(parts) > 0:
        p = parts.pop(0)
        x = x.get(p, {})
    return x


def get_uid(x, stack, index=None):
    try:
        FIELDS = ['name', 'wait.variable', 'say', 'switch.arg', 'do.cmd', 'do.variable', 'match', 'pattern', 'default', 'show']
        values = [get_field(x, f) for f in FIELDS]
        values = ','.join([str(v) for v in values if v is not None])
        assert len(values) > 0
        current_hash = ''.join(stack)
        key = '{}|{}|{}'.format(current_hash, values, index)
        ret = calc_hash(key)
        return ret
    except:
        print(x, stack)
        raise


def assign_ids(x, stack=[]):
    if isinstance(x, dict):
        uid = None
        for k, v in x.items():
            if k == 'steps':
                uid = get_uid(x, stack)
                for i, s in enumerate(v):
                    new_stack = stack + [uid, str(i)]
                    s['uid'] = get_uid(s, new_stack, i)
                    assign_ids(s, new_stack)    
            else:
                assign_ids(v, stack)
        if uid is not None:
            x['uid'] = uid
    elif isinstance(x, list):
        for xx in x:
            assign_ids(xx, stack)
    else:
        return

if __name__=='__main__':
    if len(sys.argv) > 1:
        f_in = Path(sys.argv[1])
    else:
        f_in = Path('scripts/script.yaml')

    if len(sys.argv) > 2:
        f_out = Path(sys.argv[2])
    else:
        f_out = Path('src/assets/script.json')

    scripts = yaml.load(f_in.open(encoding="utf8"), Loader = yaml.SafeLoader)
    assign_ids(scripts, [str(f_in)])
    scripts = dict(s=scripts)
    f_out.open('w', encoding="utf8").write(json.dumps(
        scripts, ensure_ascii=False, sort_keys=True, indent=2)

    )

