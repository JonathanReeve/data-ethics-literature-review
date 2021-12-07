#! /usr/bin/env nix-shell
#! nix-shell -i bash -p pandoc haskellPackages.pandoc-crossref

# This script can be run with the command ./build.sh, and requires the Nix package manager.
# Alternatively, install pandoc, pandoc-crossref, and run the command below.

pandoc -o jices-paper.pdf jices-paper.md --bibliography=../bibliography.bib --filter=pandoc-crossref --citeproc -Vurlcolor=blue
