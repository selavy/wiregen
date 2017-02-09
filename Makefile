CC=g++
CFLAGS=-Wall -Werror -std=c++11
TARGET=a.out

$(TARGET): main.cpp mktdata_itch.h
	$(CC) -o $@ $(CFLAGS) $<

.PHONY: clean
clean:
	rm -rf $(TARGET)
