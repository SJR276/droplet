SHELL = /bin/sh
CC = gcc
CFLAGS = -fPIC -Wall -Wextra -O3
LIBS = -lm
LDFLAGS = -shared

TARGET  = ../droplet/libdroplet.so
SOURCES = $(shell echo *.c)
HEADERS = $(shell echo *.h)
OBJECTS = $(SOURCES:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $(TARGET) $(LDFLAGS) $(OBJECTS) $(LIBS)
