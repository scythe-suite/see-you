SHELL = bash

CSOURCES = $(wildcard *.c)
BSOURCES = $(wildcard *.sh)
JSOURCES = $(wildcard *.java)

ifneq ($(strip $(JSOURCES)),)
	jcode = 1
	SOURCES = $(JSOURCES)
	OBJECTS = $(SOURCES:.java=.class)
	JAVAC = javac
	compile = $(JAVAC) -encoding utf8 $<
else ifneq ($(strip $(CSOURCES)),)
	ccode = 1
	SOURCES = $(CSOURCES)
	OBJECTS = $(SOURCES:.c=.o)
	CFLAGS = -Wall -pedantic -ansi
	CC = gcc
	compile = $(CC) $(CFLAGS) -c -o $@ $<
	link = $(CC) $^ -o $@
else ifneq ($(strip $(BSOURCES)),)
	bcode = 1
	SOURCES = $(BSOURCES)
	OBJECTS = $(BSOURCES)
	compile =
	link =
endif

INPUTS = $(wildcard input-*.txt)
DIFFS = $(INPUTS:input-%.txt=diffs-%.txt)
TARGET = soluzione
test = ./soluzione $$\(cat args-$*.txt\) \< $< \> $@

max_output = $$((1024*1024))

exit_on_fail = true

red := bash -c 'echo -ne "\033[31m"'
blue := bash -c 'echo -ne "\033[34m"'
reset := bash -c 'echo -ne "\033[0m"'

.PHONY: aiuto compila test pulisci consegna termina

aiuto:
	@echo "      aiuto: mostra questo aiuto"
	@echo "    compila: compila i file sorgenti"
	@echo "       test: esegue i test"
	@echo "    pulisci: elimina i file generati dai test ed i backup dell'editor"
	@echo "   consegna: esegue il comando 'consegna'"
	@echo "    termina: termina tutti gli xterm in esecuzione (ed i processi lanciati da essi)"

consegna:
	consegna

termina:
	@bash -c 'read -p "Sei sicuro? " -rsn 1; if [[ $$REPLY =~ ^[Ss]$$ ]]; then killall xterm >/dev/null 2>&1; fi; echo'

compila: $(TARGET) ;

test: $(DIFFS) ;

pulisci:
	@rm -f *.o .compile-* .link-* .errors-* actual-*.txt diffs-*.txt $(TARGET) .main-* *.class \~*

%.o: %.c
	@rm -f .compile-$*
	@echo $(compile)
	@if ! $(compile) -fmessage-length=0 2> .compile-$*; then\
		echo "make: error: compiler exit status: $$?" >> .compile-$*;\
	fi
	@if grep -q warning: .compile-$*; then\
		$(red);\
		grep ': warning:' .compile-$*;\
		$(reset);\
	fi
	@if grep -q error: .compile-$*; then\
		$(blue);\
		grep ': error:' .compile-$* 1>&2;\
		$(reset);\
		exit 1;\
	fi

%.class: %.java
	@rm -f .compile-$*
	@echo $(compile)
	@if ! $(compile) 2> .compile-$*; then\
		echo "make: error: compiler exit status: $$?" >> .compile-$*;\
	fi
	@if grep -q warning: .compile-$*; then\
		$(red);\
		grep ': warning:' .compile-$*;\
		$(reset);\
	fi
	@if grep -q error: .compile-$*; then\
		$(blue);\
		grep ': error:' .compile-$* 1>&2;\
		$(reset);\
		exit 1;\
	fi

$(TARGET): $(OBJECTS)
ifdef ccode
	@rm -f .link-$@
	@echo $(link)
	@$(link) -fmessage-length=0 2> .link-$@ || true
	@if [ -s .link-$@ ]; then\
		$(blue);\
		cat .link-$@ 1>&2;\
		$(reset);\
		exit 1;\
	fi
else ifdef jcode
	@rm -f .main-$@ $@
	@grep -HE 'public\s+static\s+void\s+main' *.java | cut -d : -f 1 | cut -d . -f 1 > .main-$@
	@if [ $$(wc -l < .main-$@) -eq 0 ]; then\
		$(blue);\
		echo error: no main method found 1>&2;\
		$(reset);\
		exit 1;\
	fi
	@if [ $$(wc -l < .main-$@) -gt 1 ]; then\
		$(blue);\
		echo error: more than one main method found 1>&2;\
		$(reset);\
		exit 1;\
	fi
	@bash -c "echo -e '#!/bin/sh\nexec java $$(cat .main-$@) \"\$$@\"' > $@"
	@chmod u+x $@
else ifdef bcode
	@rm -f .main-$@ $@
	@ls | grep .sh > .main-$@
	@if [ $$(wc -l < .main-$@) -eq 0 ]; then\
		$(blue);\
		echo error: no .sh file found 1>&2;\
		$(reset);\
		exit 1;\
	fi
	@if [ $$(wc -l < .main-$@) -gt 1 ]; then\
		$(blue);\
		echo error: more than one .sh file found 1>&2;\
		$(reset);\
		exit 1;\
	fi
	@bash -c "echo -e '#!/bin/sh\nexec bash $$(cat .main-$@) \"\$$@\"' > $@"
	@chmod u+x $@
else
	@$(blue);\
	echo error: no .c, .java, or .sh file found 1>&2;\
	$(reset);\
	exit 1
endif

.PRECIOUS: actual-%.txt

actual-%.txt: input-%.txt args-%.txt $(TARGET)
	@rm -f .errors-$* $@
	@echo $(test)
	@if ! bash -c '( cmdpid=$$BASHPID; (sleep 2; kill $$cmdpid 2>/dev/null && echo bash: line 1: Terminated 1>&2) & exec ./$(TARGET) $$(cat args-$*.txt) < $< > .$@ )' 2>.errors-$*; then\
		if grep -Eqi 'bash: line 1: .*Segmentation fault' .errors-$*; then\
			$(red);\
			echo segmentation fault 1>&2;\
			$(reset);\
			rm -f .$@;\
		elif grep -Eqi 'bash: line 1: .*Terminated' .errors-$*; then\
			$(blue);\
			echo execution timeout 1>&2;\
			$(reset);\
			rm -f .$@;\
		else\
			$(red);\
			echo non-zero return value 1>&2;\
			$(reset);\
			head -c $(max_output) < .$@ > $@;\
			rm -f .$@;\
		fi;\
		if $(exit_on_fail); then exit 1; fi;\
	else\
		if grep -q -e '[[:cntrl:]]' .$@; then\
			$(red);\
			echo file contains control chars 1>&2;\
			$(reset);\
			rm -f .$@;\
			if $(exit_on_fail); then exit 1; fi;\
		else\
			head -c $(max_output) < .$@ > $@;\
			rm -f .$@;\
			> .errors-$*;\
		fi;\
	fi

diffs-%.txt: output-%.txt actual-%.txt
	@echo diff -Bab $^ \> $@
	@bash -c "diff -Bab actual-$*.txt output-$*.txt > $@" 2> /dev/null || true
	@if [ -s $@ ]; then\
	 	$(red);\
	 	cat $@;\
		$(reset);\
		if $(exit_on_fail); then exit 1; fi;\
	fi
