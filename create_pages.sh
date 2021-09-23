#!/bin/bash

# Make sure to install imagemagik

if [[ ! -d img ]]; then
  echo "Can't find image dir."
  exit 1
fi

rm -rf card_sheets
mkdir -p card_sheets

montage \
  -geometry +10+10 \
  -tile 3x3 \
  img/*.png card_sheets/%d.png


