#!/bin/bash


# Checking that everything is in its right place:

error(){
  # Reports and error and exits.
  MSG=$1
  echo "Presubmit failed. $MSG"
  exit 1
}

phase(){
  # Delineates between presubmit phases.
  NAME=$1
  echo
  echo
  echo "--- $NAME ---"
}

PACKAGE_DIR="./card_game"

if [[ ! -d "$PACKAGE_DIR" ]]; then
  error "Must run in project root."
fi

if ! which pylint; then
  error "Failed to find pylint."
fi

if ! which yapf; then
  error "Failed to find yapf."
fi


phase "formatting"
# Reorder imports
isort "$PACKAGE_DIR"
yapf --verbose --in-place --parallel --recursive \
  --style='{based_on_style: google indent_width: 2}' \
  "$PACKAGE_DIR"
if [[ $? -ne 0 ]]; then
  error "Formatter error."
fi

phase "linting"
# Exits nonzero if code quality score is less than `fail-under`.
pylint --jobs=0 --fail-under=10 --indent-string="  " \
  --max-line-length=80 \
  --good-names="i,j,id,x,y,im,bb,c,x1,x2,y1,y2,t,v,db,f,e" \
  --disable=missing-docstring,broad-except\
  --load-plugins="pylint.extensions.docparams" $PACKAGE_DIR
if [[ $? -ne 0 ]]; then
  error "Linter errors."
fi

phase "Success!"
