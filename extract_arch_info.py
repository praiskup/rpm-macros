#! /bin/python3

import argparse
import copy
import os

import yaml

from norpm.macrofile import system_macro_registry
from norpm.specfile import ParserHooks, specfile_expand


class Hooks(ParserHooks):
    """ Gather access to spec tags """
    def __init__(self):
        self.tags = {}
    def tag_found(self, name, value, _tag_raw):
        """ Gather EclusiveArch, ExcludeArch, BuildArch... """
        if name.lower() in ["exclusivearch", "excludearch", "buildarch"]:
            self.tags[name] = value


def _get_override_db():
    dirname = os.path.dirname(os.path.realpath(__file__))
    file = os.path.join(dirname, "data-builder-architecture.yaml")
    with open(file, 'r', encoding="utf8") as f:
        file_data = yaml.safe_load(f)
    return file_data


def _get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--specfile", required=True)
    excl = parser.add_mutually_exclusive_group()
    excl.add_argument("--target")
    excl.add_argument("--targets", action="append")
    return parser


def handle_target(origdb, overrides, specfile, target):
    """
    Using the system database ORIGDB, and OVERRIDES, expand SPECFILE
    for Mock TARGET.
    """
    db = copy.deepcopy(origdb)
    distro, _ = target.rsplit("-", 1)
    for key in overrides.keys():
        # No matter if defined for given TARGET, we undefine the macro.
        # Think of `%fc43` for F44 TARGET on F43 host.
        db.undefine(key)
        for data in overrides[key]:
            if distro in data["tags"]:
                if data["value"] is None:
                    continue
                value = data["value"][-1]
                if value["params"] is None:
                    db.define(key, value["def"])
                else:
                    db.define(key, (value["def"], value["params"]))

    hooks = Hooks()
    with open(specfile, "r", encoding="utf8") as fd:
        specfile_expand(fd.read(), db, hooks)
    return hooks.tags


def _main():
    opts = _get_arg_parser().parse_args()
    db = system_macro_registry()
    db["dist"] = ""
    db.known_norpm_hacks()
    overrides = _get_override_db()

    if opts.target:
        result = handle_target(db, overrides, opts.specfile, opts.target)
    else:
        result = {}
        for target in opts.targets:
            result[target] = handle_target(db, overrides, opts.specfile, target)

    print(yaml.dump(result, sort_keys=True))

if __name__ == "__main__":
    _main()
