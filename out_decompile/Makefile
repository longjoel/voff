# VOFF Winelib Build
WINE = winegcc
WINE_FLAGS = -Wall -Wno-unused-variable -Wno-int-conversion -Wno-incompatible-pointer-types -I.
WINE_LIBS = -lgdi32 -lcomctl32 -lwinmm -lddraw

# VOFF SDL2 Build (native Linux, no Wine)
CC = gcc
SDL_FLAGS = -Wall -O2
SDL_LIBS = -lSDL2 -lGL -lm

TARGET = voff.exe
TARGET_SDL = voff_sdl

# Core sources
CORE_SRCS = voff_data.c voff_game.c
CORE_OBJS = $(CORE_SRCS:.c=.o) data_init.o rdata_init.o

# Game function sources (compiled from decompiled code)
GAME_SRCS = $(wildcard game/*.c)
GAME_OBJS = $(GAME_SRCS:.c=.o)
GAME_OBJS := $(filter-out game/stub_funcs.o,$(GAME_OBJS))

SDL_SRCS = voff_sdl.c
SDL_OBJS = $(SDL_SRCS:.c=.o) data_init.o rdata_init.o

.PHONY: all clean data sdl gen

all: data_init.o rdata_init.o $(TARGET)

sdl: data_init.o rdata_init.o $(TARGET_SDL)

gen:
	python3 gen_game.py game/

data_init.o: .data.bin
	dd if=.data.bin of=data_init.bin bs=1 count=3947520 2>/dev/null
	objcopy -I binary -O elf64-x86-64 -B i386:x86-64 --rename-section .data=.voff_data data_init.bin $@

rdata_init.o: .rdata.bin
	objcopy -I binary -O elf64-x86-64 -B i386:x86-64 --rename-section .data=.voff_rdata .rdata.bin $@

$(TARGET): $(CORE_OBJS) $(GAME_OBJS) game/stub_funcs.o
	$(WINE) $(WINE_FLAGS) -o $@ $^ $(WINE_LIBS)

$(TARGET_SDL): $(SDL_OBJS)
	$(CC) $(SDL_FLAGS) -o $@ $^ $(SDL_LIBS)

%.o: %.c voff_bridge.h
	$(WINE) $(WINE_FLAGS) -c -o $@ $<

game/%.o: game/%.c game/game.h
	$(WINE) $(WINE_FLAGS) -c -o $@ $<

voff_sdl.o: voff_sdl.c
	$(CC) $(SDL_FLAGS) -c -o $@ $<

clean:
	rm -f $(TARGET) $(TARGET).so $(CORE_OBJS) game/*.o $(TARGET_SDL) data_init.bin voff_sdl.o
