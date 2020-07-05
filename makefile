name = PeterlitsNote
viewer = chrome.exe

.PHONY: run
run2:
	xelatex $(name).tex

.PHONY: clean
clean:
	-rm *.aux
	-rm *.log
	-rm *.toc
	-rm *.out

.PHONY: run2
run:
	xelatex $(name).tex
	xelatex $(name).tex

.PHONY: look
look:
	$(viewer) $(name).pdf

.PHONY: funk
fuck: run look

.PHONY: fuck2
fuck2: run2 look

.PHONY: git
git:
	git add .
	git commit
	git push

