Extracted RPM Macro data from multiple distributions
====================================================

We maintain these files:

- `data-builder-architecture-macros.json` - list of macros names that appears to
  affect builder architecture selection in Fedora/RHEL build systems.  Generated
  by `norpm-conditions-for-arch-statements` and all Rawhide spec-files.

- `data-builder-architecture.yaml` - the macro values for macros in
  `norpm-conditions-for-arch-statements` extracted from multiple distributions.


Howto
-----

```
$ norpm-conditions-for-arch-statements  --specfile-dir rpm-specs > used-macros.json
$ # combine used-macros.json into data-builder-architecture-macros.json
$ ./extract-all-distros.sh
$ ./combine-distros.py > data-builder-architecture.json
$ # commit changes
```

Implementation details
----------------------

If we talk about a parametric macro, that's an issue :-( We have to dump the
distro-specific definition (not the whole, indefinite set of possible outputs).
However, we want to avoid Turing-complete macros; for those, we need to find
safe workarounds manually.

**Non-parametric macros**

We attempt to expand using norpm. If that succeeds (meaning there are no %
characters remaining in the output), we use the expanded value as the
definition. If a macro remains (e.g., Lua), we then try to expand it with the
real RPM parser (via Mock)
