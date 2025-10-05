#! /usr/bin/python3

"""
Given a list of macros, extract the definitions from the system macro
files.
"""

import argparse
import copy
import json
import subprocess

import yaml

from norpm.macrofile import system_macro_registry
from norpm.specfile import specfile_expand_string


RHEL_LAST = 11
FEDORA_LAST = 45


def _buildroot(mock_root):
    return f'/var/lib/mock/{mock_root}/root'


def expand_non_parametric_macro_norpm(macro_name, old_db):
    """
    Expand %macro_name using norpm
    """
    db = copy.deepcopy(old_db)
    return specfile_expand_string('%' + macro_name, db)


def expand_non_parametric_macro_rpm(macro_name, root):
    """
    Call 'rpm --eval %macro_name'
    """

    cmd = ['mock', '-r', 'fedora-rawhide-x86_64',
           '--shell', 'rpm', '--eval', '%' + macro_name]
    output = subprocess.check_output(cmd).decode("utf-8")
    return output[:-1]


def _get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--macro-list", required=True)
    parser.add_argument("--root", required=True)
    return parser


def _load_list(filename):
    with open(filename, "r", encoding="utf-8") as fd:
        output = set(json.loads(fd.read()))
    output = {o for o in output if o not in [
        "with",
        "without",
    ]}

    for i in range(FEDORA_LAST - 5, FEDORA_LAST + 1):
        output.add(f"fc{i}")
    for i in range(RHEL_LAST - 5, RHEL_LAST + 1):
        output.add(f"el{i}")
    return list(output)

def _main():
    opts = _get_arg_parser().parse_args()
    macro_names = _load_list(opts.macro_list)
    db = system_macro_registry(prefix=_buildroot(opts.root))
    macro_defs = {}
    for name in macro_names:
        try:
            macro_def = db[name]
            if macro_def.parametric:
                macro_defs[name] = db[name].dump_def()
                continue
            value = expand_non_parametric_macro_norpm(name, db)
            if '%' in value:
                # Is there '%lua' inside?
                value = expand_non_parametric_macro_rpm(name, opts.root)
            # only one item in array, no over-definitions here.
            macro_defs[name] = [{'def': value, 'params': None}]
        except KeyError:
            macro_defs[name] = None
    print(yaml.dump(macro_defs, indent=2, default_flow_style=False))


if __name__ == "__main__":
    _main()
