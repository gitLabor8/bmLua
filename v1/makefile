# Coole makefile
# Copyrights to Niek
clean: tex rm open

tex:
		pdflatex --shell-escape lua.tex
		pdflatex --shell-escape lua.tex

rm:
		- mv *.aux logs
		- mv *.log logs
		- mv *.toc logs
		- mv *.dot logs
		- mv *-dot2tex-*.tex logs

open:
		okular lua.pdf &