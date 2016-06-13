# Coole makefile
# Copyrights to Niek
default: test.pdf rm

test.tex: tex.py syntax semantics document
	python3 tex.py

test.pdf: test.tex
	pdflatex --shell-escape test.tex
	pdflatex --shell-escape test.tex

lua.pdf: lua.tex
	pdflatex --shell-escape lua.tex
	pdflatex --shell-escape lua.tex

rm:
	- rm -r logs/
	mkdir -p logs/
	- mv test.tex logs/
	- mv *.aux logs/
	- mv *.log logs/
	- mv *.toc logs/
	- mv *.dot logs/
	- mv *.out logs/
	- mv *-dot2tex-*.tex logs/
