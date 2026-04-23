main.pdf: main.tex bibliography.bib fig1.pdf fig2.pdf fig3.pdf fig4.pdf fig5.pdf
	latexmk -pdf main -auxdir=aux

fig1.pdf: main.py
	python main.py fig1

fig2.pdf: main.py
	python main.py fig2

fig3.pdf: main.py
	python main.py fig3

fig4.pdf: main.py
	python main.py fig4

fig5.pdf: main.py
	python main.py fig5
