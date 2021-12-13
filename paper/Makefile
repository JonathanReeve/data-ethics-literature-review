jices-paper.pdf: jices-paper.md
	nix-shell -p pandoc haskellPackages.pandoc-crossref --run "pandoc --bibliography=../bibliography.bib --filter=pandoc-crossref --citeproc -Vurlcolor=blue -o $@ $<"

jices-paper.tex: jices-paper.md
	nix-shell -p pandoc haskellPackages.pandoc-crossref --run "pandoc --standalone --bibliography=../bibliography.bib --filter=pandoc-crossref --citeproc -Vurlcolor=blue -o $@ $<"
