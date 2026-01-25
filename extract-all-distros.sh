#! /bin/bash -ex

arch=x86_64
input=data-builder-architecture-macros.json
distros=(
    alma+epel-10
    alma+epel-9
    alma-kitten+epel-10
    almalinux-10
    almalinux-9
    almalinux-kitten-10
    amazonlinux-2023
    centos-stream-10
    centos-stream-8
    centos-stream-9
    centos-stream+epel-next-8
    centos-stream+epel-next-9
    centos+epel-7
    fedora-42
    fedora-43
    fedora-eln
    fedora-rawhide
    mageia-8
    mageia-9
    mageia-cauldron
    openeuler-20.03
    openeuler-22.03
    openeuler-24.03
    opensuse-leap-15.6
    opensuse-tumbleweed
    rhel-10
    rhel-7
    rhel-8
    rhel-9
    rhel+epel-10
)

# EPEL-8+ is RHEL+EPEL-8

for distro in "${distros[@]}"; do
    mock_opt=$distro-$arch
    case $distro in
    centos+epel-7)
        mock_opt=eol/$mock_opt
        ;;
    esac
    mock -r "$mock_opt" --init
    ./extract_macro_definitions.py --macro-list "$input" --root "$mock_opt" > "data/$distro.yaml"
done
