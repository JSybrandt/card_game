#!/bin/bash

# Make sure to install imagemagik

if [[ ! -d img ]]; then
  echo "Can't find image dir."
  exit 1
fi

mkdir -p card_sheets

montage -tile 3x3 -mode concatenate img/*.png card_sheets/%d.png


