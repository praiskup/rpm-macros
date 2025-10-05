#! /bin/bash -ex

arch=x86_64
input=data-builder-architecture-macros.json
distros=(
    rhel-7
    rhel-8
    rhel-9
    rhel-10
    fedora-rawhide
    fedora-43
    fedora-42
    fedora-41
    opensuse-tumbleweed
)

for distro in "${distros[@]}"; do
    mock_root=$distro-$arch
    mock -r "$mock_root" "$distro-$arch" --init
    ./extract_macro_definitions.py --macro-list "$input" --root "$mock_root" > "data/$distro.yaml"
done
