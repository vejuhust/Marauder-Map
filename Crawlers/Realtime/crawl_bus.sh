#!/bin/bash

TZ='Asia/Shanghai'; export TZ

lines=(
    "3e37f7b5-db71-4dfa-9dc1-30f5d29f43f5 110a"
    "792365ed-82b2-423f-bbdc-5376d1507d21 110b"
    "edc1ecd6-2bf8-4b08-8727-385bb8943b9d 115a"
    "e31d7bb3-ba4c-4e24-85e8-95e9d0f4d49e 115b"
    "e0855aea-89f2-4881-a582-4950272fbdb0 177a"
    "12d2ac2a-28fb-4d06-adb8-af1d2011d580 177b"
    "7d984315-a7f0-4d68-a797-95417d4d0045 180a"
    "fc985516-bbdb-4640-a575-9087aa87460a 180b"
)

cd "$( dirname "${BASH_SOURCE[0]}" )"
command="python get_bus.py"

for target in "${lines[@]}"
do
    ${command} ${target}
    echo "$(date '+%Y-%m-%dT%H:%M:%SZ')" "${target}"
done
