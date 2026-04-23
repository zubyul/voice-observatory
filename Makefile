voicedl: voicedl.m
	clang -O2 -fobjc-arc -Wall -framework Foundation -o voicedl voicedl.m

.PHONY: clean
clean:
	rm -f voicedl
