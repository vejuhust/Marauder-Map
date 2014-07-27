#!/bin/bash

TZ='Asia/Shanghai'; export TZ

lines=(
    "921f91ad-757e-49d6-86ae-8e5f205117be k1a"
    "af9b209b-f99d-4184-af7d-e6ac105d8e7f k1b"
    "1aa773c8-e865-4847-95a1-f4c956ae02ef k2a"
    "e0e5561a-32ea-432d-ac98-38eed8c4e448 k2b"
    "f5e34c0f-0276-44d6-9d6c-03aed352ed61 y1a"
    "528b5713-0177-4eb6-85be-c53dcf447e31 y1b"
    "20e54b5f-f140-41d3-90ae-d5a60a02957e y2a"
    "e128b409-921e-43db-9c99-c78b0f0c8fad y2b"
    "3e37f7b5-db71-4dfa-9dc1-30f5d29f43f5 110a"
    "792365ed-82b2-423f-bbdc-5376d1507d21 110b"
    "edc1ecd6-2bf8-4b08-8727-385bb8943b9d 115a"
    "e31d7bb3-ba4c-4e24-85e8-95e9d0f4d49e 115b"
    "7e5f894b-db9a-43da-b5eb-8c6a170db5b8 128a"
    "9f1f41ea-8939-492b-a969-028ef588857b 128b"
    "ab9fdefc-a31d-461f-bbdf-030ee15d41e7 146a"
    "96c177f0-0828-4a31-ba19-ddce9e9649e0 146b"
    "e0855aea-89f2-4881-a582-4950272fbdb0 177a"
    "12d2ac2a-28fb-4d06-adb8-af1d2011d580 177b"
    "7d984315-a7f0-4d68-a797-95417d4d0045 180a"
    "fc985516-bbdb-4640-a575-9087aa87460a 180b"
)

cd "$( dirname "${BASH_SOURCE[0]}" )"
command="python get_line_route.py"

for target in "${lines[@]}"
do
    ${command} ${target}
    echo "$(date '+%Y-%m-%dT%H:%M:%SZ')" "${target}"
    sleep 2
done
