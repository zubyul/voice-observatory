CC      ?= clang
CFLAGS  ?= -O2 -fobjc-arc -Wall
LDFLAGS ?= -framework Foundation

voicedl: voicedl.m
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

.PHONY: clean
clean:
	rm -f voicedl
