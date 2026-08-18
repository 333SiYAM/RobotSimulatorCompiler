%{
/*
 * ============================================================
 *  robot_parser.y  --  Bison Parser
 *  Robot Command Language (RCL)
 *
 *  Purpose:
 *    Define the grammar of RCL and, for each recognized command,
 *    output a JSON object to stdout.  The Python frontend reads
 *    this JSON to drive the robot animation.
 *
 *  Grammar (EBNF summary):
 *
 *    program      -->  command+
 *
 *    command      -->  move_cmd
 *                   | turn_cmd
 *                   | speed_cmd
 *                   | stop_cmd
 *                   | ability_cmd
 *
 *    move_cmd     -->  MOVE  direction  NUMBER  [STEPS]
 *    turn_cmd     -->  TURN  direction  NUMBER  [DEGREES]
 *    speed_cmd    -->  SPEED  NUMBER
 *    stop_cmd     -->  STOP
 *    ability_cmd  -->  ABILITY  STRING
 *
 *    direction    -->  FORWARD | BACKWARD | LEFT | RIGHT
 *
 *  Output format (one object per command):
 *    [
 *      { "type":"move", "direction":"forward", "value":5.00,
 *        "unit":"steps", "extra":"" },
 *      { "type":"turn", "direction":"left",    "value":90.00,
 *        "unit":"degrees", "extra":"" },
 *      { "type":"speed", "value":7.00,         "unit":"", "extra":"" },
 *      { "type":"stop",  "value":-1,            "unit":"", "extra":"" },
 *      { "type":"ability","value":-1,           "unit":"", "extra":"shield" }
 *    ]
 *
 *  How to build:
 *    bison -d robot_parser.y    (produces robot_parser.tab.c + .h)
 *    See Makefile for full build.
 * ============================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ── External symbols provided by robot_lexer.l ── */
extern int  yylex(void);
extern int  line_num;

/* ── Error handler (defined at bottom of this file) ── */
void yyerror(const char *msg);

/* ── JSON output state ────────────────────────────────────────────────────── */
int cmd_count = 0;   /* how many commands have been emitted so far */

/*
 * emit_command()
 *   Prints one JSON object for a parsed command.
 *   Parameters:
 *     type      - command type: "move", "turn", "speed", "stop", "ability"
 *     direction - direction string, or "" if not applicable
 *     value     - numeric argument, or -1.0 if not applicable
 *     unit      - unit string ("steps", "degrees"), or ""
 *     extra     - ability name string, or ""
 */
static void emit_command(
        const char *type,
        const char *direction,
        double      value,
        const char *unit,
        const char *extra)
{
    /* Separate JSON objects with a comma */
    if (cmd_count > 0)
        printf(",\n");

    printf("  {\n");
    printf("    \"type\"      : \"%s\"",    type);

    if (direction && direction[0])
        printf(",\n    \"direction\" : \"%s\"", direction);

    if (value >= 0)
        printf(",\n    \"value\"     : %.2f",   value);

    if (unit && unit[0])
        printf(",\n    \"unit\"      : \"%s\"", unit);

    if (extra && extra[0])
        printf(",\n    \"extra\"     : \"%s\"", extra);

    printf("\n  }");
    fflush(stdout);
    cmd_count++;
}
%}

/* ════════════════════════════════════════════════════════════
   Semantic value union
   Each token or non-terminal can carry one of these values.
   ════════════════════════════════════════════════════════════ */
%union {
    double  fval;   /* value for NUMBER tokens                 */
    char   *sval;   /* value for STRING tokens (heap-allocated)*/
}

/* ════════════════════════════════════════════════════════════
   Token declarations
   (Must match what robot_lexer.l returns via return <TOKEN>)
   ════════════════════════════════════════════════════════════ */
%token  MOVE FORWARD BACKWARD LEFT RIGHT    /* movement keywords  */
%token  TURN                                /* rotation keyword   */
%token  STOP                                /* stop keyword       */
%token  ABILITY                             /* ability keyword    */
%token  SPEED                               /* speed keyword      */
%token  STEPS DEGREES                       /* unit keywords      */

%token  <fval>  NUMBER   /* carries the numeric value   */
%token  <sval>  STRING   /* carries the string content  */

/* ════════════════════════════════════════════════════════════
   Non-terminal type declarations
   ════════════════════════════════════════════════════════════ */
%type   <sval>  direction   /* will hold "forward","backward",etc. */

/* ════════════════════════════════════════════════════════════
   Grammar Rules
   ════════════════════════════════════════════════════════════ */
%%

/* ─── Top-level: the whole program is one or more commands ── */
program
    : command_list
    ;

/*
 *  command_list is left-recursive so the parser builds it bottom-up
 *  without consuming extra stack space.
 */
command_list
    : command_list  command     /* append another command */
    | command                   /* first (only) command   */
    ;

/* ─── Dispatch to individual command rules ─────────────────── */
command
    : move_cmd
    | turn_cmd
    | speed_cmd
    | stop_cmd
    | ability_cmd
    | error                 /* graceful error recovery  */
        {
            fprintf(stderr, "Skipping bad command and continuing...\n");
            yyerrok;        /* reset error flag          */
        }
    ;

/* ─────────────────────────────────────────────────────────────
   MOVE  direction  NUMBER  [STEPS]
   Examples:
     move forward 5 steps
     go backward 3
     move left 2
   ───────────────────────────────────────────────────────────── */
move_cmd
    : MOVE direction NUMBER STEPS
        {
            emit_command("move", $2, $3, "steps", "");
            free($2);           /* free heap string from direction rule */
        }
    | MOVE direction NUMBER
        {
            emit_command("move", $2, $3, "steps", "");
            free($2);
        }
    ;

/* ─────────────────────────────────────────────────────────────
   TURN  direction  NUMBER  [DEGREES]
   Examples:
     turn left 90 degrees
     rotate right 45
     turn left 180 deg
   ───────────────────────────────────────────────────────────── */
turn_cmd
    : TURN direction NUMBER DEGREES
        {
            emit_command("turn", $2, $3, "degrees", "");
            free($2);
        }
    | TURN direction NUMBER
        {
            emit_command("turn", $2, $3, "degrees", "");
            free($2);
        }
    ;

/* ─────────────────────────────────────────────────────────────
   SPEED  NUMBER   (1 = slowest, 10 = fastest)
   Example:
     speed 7
   ───────────────────────────────────────────────────────────── */
speed_cmd
    : SPEED NUMBER
        {
            emit_command("speed", "", $2, "", "");
        }
    ;

/* ─────────────────────────────────────────────────────────────
   STOP  (no arguments)
   Example:
     stop
     halt
   ───────────────────────────────────────────────────────────── */
stop_cmd
    : STOP
        {
            emit_command("stop", "", -1.0, "", "");
        }
    ;

/* ─────────────────────────────────────────────────────────────
   ABILITY  STRING
   Examples:
     ability "shield"
     ability "laser"
     skill "boost"
   ───────────────────────────────────────────────────────────── */
ability_cmd
    : ABILITY STRING
        {
            emit_command("ability", "", -1.0, "", $2);
            free($2);           /* free heap string from lexer */
        }
    ;

/* ─────────────────────────────────────────────────────────────
   direction  -->  FORWARD | BACKWARD | LEFT | RIGHT
   Returns a heap-allocated string; caller must free().
   ───────────────────────────────────────────────────────────── */
direction
    : FORWARD   { $$ = strdup("forward");  }
    | BACKWARD  { $$ = strdup("backward"); }
    | LEFT      { $$ = strdup("left");     }
    | RIGHT     { $$ = strdup("right");    }
    ;

%%

/* ─────────────────────────────────────────────────────────────
   yyerror()
   Called by the parser whenever a syntax error is detected.
   Prints the line number and error message to stderr.
   ───────────────────────────────────────────────────────────── */
void yyerror(const char *msg) {
    fprintf(stderr, "Parse Error (line %d): %s\n", line_num, msg);
}
