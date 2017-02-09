CC=g++
CFLAGS=-Wall -Werror -std=c++11
TARGET=a.out
GENERATED=mktdata_itch.h

all: $(TARGET)

$(GENERATED): ./wiregen.py
	./wiregen.py > $@

$(TARGET): $(GENERATED) main.cpp
	$(CC) -o $@ $(CFLAGS) $<

.PHONY: clean
clean:
	rm -rf $(TARGET) $(GENERATED)
