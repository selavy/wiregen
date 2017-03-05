CC=gcc
CFLAGS=-Wall -Werror
TARGET=a.out
GENERATED=mktdata_itch.h

all: $(TARGET)

$(GENERATED): ./wiregen.py
	./wiregen.py > $@

$(TARGET): main.c $(GENERATED)
	$(CC) -o $@ $(CFLAGS) $<

.PHONY: clean
clean:
	rm -rf $(TARGET) $(GENERATED)
