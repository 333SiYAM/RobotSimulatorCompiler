/*
 * ============================================================
 *  main.c  --  Robot Command Compiler Entry Point
 *
 *  Purpose:
 *    Glue the Flex-generated lexer (lex.yy.c) and the
 *    Bison-generated parser (robot_parser.tab.c) together
 *    into a single executable.
 *
 *    Reads Robot Command Language (RCL) from stdin,
 *    runs the lexer+parser pipeline, and outputs a JSON
 *    array of parsed commands to stdout.
 *    Error messages go to stderr.
 *
 *  Usage:
 *    echo "move forward 5 steps"  | robot_compiler.exe
 *    robot_compiler.exe < my_commands.rcl
 *    robot_compiler.exe < my_commands.rcl > output.json
 *
 *  Example output:
 *    [
 *      {
 *        "type"      : "move",
 *        "direction" : "forward",
 *        "value"     : 5.00,
 *        "unit"      : "steps",
 *        "extra"     : ""
 *      }
 *    ]
 *
 *  Exit codes:
 *    0 = success
 *    1 = parse error(s) encountered
 * ============================================================
 */

#include <stdio.h>
#include <stdlib.h>

/* ── Declarations from robot_parser.tab.c ────────────────────────────────── */
extern int yyparse(void);   /* main parser function (calls yylex internally) */

/* ── Declarations from robot_parser.y ───────────────────────────────────── */
extern int cmd_count;       /* number of commands successfully parsed        */

int main(int argc, char *argv[]) {

    /* ── Print opening bracket of the JSON array ── */
    printf("[\n");

    /* ── Run the parser (drives the lexer via yylex()) ── */
    int parse_result = yyparse();

    /* ── Print closing bracket ── */
    printf("\n]\n");

    /* ── Report result ── */
    if (parse_result != 0) {
        fprintf(stderr, "Compilation FAILED.\n");
        return EXIT_FAILURE;
    }

    fprintf(stderr,
        "Compilation OK  --  %d command(s) parsed.\n",
        cmd_count);

    return EXIT_SUCCESS;
}
