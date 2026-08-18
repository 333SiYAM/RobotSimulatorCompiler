# ============================================================
#  Makefile  --  Build the Robot Command Compiler
#
#  Prerequisites:
#    - flex  (GNU Flex lexer generator)
#    - bison (GNU Bison parser generator)
#    - gcc   (MinGW on Windows, or GCC on Linux/macOS)
#
#  On Windows with MinGW, install via:
#    winget install GnuWin.Flex
#    winget install GnuWin.Bison
#    winget install MinGW
#
#  Targets:
#    make          ->  build robot_compiler.exe
#    make test     ->  quick smoke test
#    make clean    ->  remove all generated files
# ============================================================

CC      = gcc
CFLAGS  = -Wall -Wextra -g
TARGET  = robot_compiler.exe

# ── Generated source files (created by flex and bison) ──────
LEX_SRC  = lex.yy.c
PAR_SRC  = robot_parser.tab.c
PAR_HDR  = robot_parser.tab.h

# ════════════════════════════════════════════════════════════
#  Default target: build the compiler executable
# ════════════════════════════════════════════════════════════
all: $(TARGET)
	@echo ""
	@echo "  Build complete!  Run: echo 'move forward 5 steps' | ./$(TARGET)"
	@echo ""

# ── Step 1: Bison generates the parser source + header ──────
#   -d  also produces the .h file that the lexer #includes
$(PAR_SRC) $(PAR_HDR): robot_parser.y
	@echo "[Bison] Compiling robot_parser.y  ->  $(PAR_SRC) + $(PAR_HDR)"
	bison -d robot_parser.y

# ── Step 2: Flex generates the lexer source ─────────────────
#   Must depend on PAR_HDR because lex.yy.c #includes it
$(LEX_SRC): robot_lexer.l $(PAR_HDR)
	@echo "[Flex ] Scanning robot_lexer.l  ->  $(LEX_SRC)"
	flex robot_lexer.l

# ── Step 3: Compile all C sources into one binary ───────────
$(TARGET): main.c $(PAR_SRC) $(LEX_SRC)
	@echo "[GCC  ] Linking  ->  $(TARGET)"
	$(CC) $(CFLAGS) -o $(TARGET) main.c $(PAR_SRC) $(LEX_SRC) -lfl
	@echo "[OK   ] $(TARGET) is ready."

# ════════════════════════════════════════════════════════════
#  Smoke test: parse a few commands and print JSON
# ════════════════════════════════════════════════════════════
test: $(TARGET)
	@echo ""
	@echo "═══ Test 1: move forward 5 steps ═══"
	@echo "move forward 5 steps" | ./$(TARGET)
	@echo ""
	@echo "═══ Test 2: multiple commands ═══"
	@printf "speed 8\nmove forward 3 steps\nturn left 90 degrees\nstop\n" | ./$(TARGET)
	@echo ""
	@echo "═══ Test 3: ability ═══"
	@echo 'ability "shield"' | ./$(TARGET)
	@echo ""

# ════════════════════════════════════════════════════════════
#  Clean generated files
# ════════════════════════════════════════════════════════════
clean:
	@echo "[Clean] Removing generated files..."
	-del /Q $(LEX_SRC) $(PAR_SRC) $(PAR_HDR) $(TARGET) 2>NUL
	@echo "[Clean] Done."

.PHONY: all test clean
