#!/bin/zsh
# Run build_manifest.py and stage manifest.json if changed
python tie/build_manifest.py
if [[ $? -ne 0 ]]; then
  echo "Error running build_manifest.py"
  exit 1
fi
if [[ -n $(git status --porcelain tie/tcv/manifest.json) ]]; then
  git add tie/tcv/manifest.json
  echo "Staged updated tie/tcv/manifest.json"
else
  echo "No changes to tie/tcv/manifest.json"
fi
exit 0
