%{
/*
 * ============================================================
 *  robot_lexer.l  --  Flex Lexical Analyser
 *  Robot Command Language (RCL)
 *
 *  Purpose:
 *    Scan the source text character-by-character and break it
 *    into a stream of tokens for the Bison parser.
 *
 *  Tokens produced:
 *    MOVE, FORWARD, BACKWARD, LEFT, RIGHT, TURN,
 *    STOP, ABILITY, SPEED, STEPS, DEGREES,
 *    NUMBER  (integer or float),
 *    STRING  (double-quoted text)
 *
 *  Ignored:
 *    Whitespace, newlines, single-line comments ( # ... )
 *
 *  Aliases supported (case-insensitive):
 *    go     -> MOVE     |  rotate -> TURN
 *    back   -> BACKWARD |  halt   -> STOP
 *    skill  -> ABILITY  |  deg    -> DEGREES
 *    step   -> STEPS    |  degree -> DEGREES
 *
 *  How to build:
 *    flex robot_lexer.l          (produces lex.yy.c)
 *    See Makefile for full build.
 * ============================================================
 */

#include "robot_parser.tab.h"   /* token constants from Bison */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int line_num = 1;               /* current source line (for error messages) */
%}

/* ── Flex Options ─────────────────────────────────────────────────────────── */
%option noyywrap          /* no yywrap() needed for single-file input     */
%option yylineno          /* let Flex maintain yylineno automatically      */
%option case-insensitive  /* keywords match regardless of letter case      */

/* ── Named Regular-Expression Patterns ───────────────────────────────────── */
DIGIT       [0-9]
INTEGER     {DIGIT}+
FLOAT       {DIGIT}+"."{DIGIT}+
NUMBER      {FLOAT}|{INTEGER}        /* float before integer (greedy)       */
WHITESPACE  [ \t\r]+
NEWLINE     \n
STRING      \"[^\"]*\"               /* anything between double quotes       */
COMMENT     #[^\n]*                  /* hash to end-of-line                  */

%%

/* ── KEYWORD TOKENS ─────────────────────────────────────────────────────── */
/*    Listed longest/most-specific first to avoid prefix conflicts           */

"move"          { return MOVE;     }   /* begin a movement command           */
"go"            { return MOVE;     }   /* alias: 'go forward 3'             */

"forward"       { return FORWARD;  }   /* direction: straight ahead          */
"backward"      { return BACKWARD; }   /* direction: reverse                 */
"back"          { return BACKWARD; }   /* alias: 'move back 2'              */

"left"          { return LEFT;     }   /* direction: rotate/strafe left      */
"right"         { return RIGHT;    }   /* direction: rotate/strafe right     */

"turn"          { return TURN;     }   /* rotation command                   */
"rotate"        { return TURN;     }   /* alias: 'rotate left 90'           */

"stop"          { return STOP;     }   /* halt all movement                  */
"halt"          { return STOP;     }   /* alias: 'halt'                     */

"ability"       { return ABILITY;  }   /* activate a special ability         */
"skill"         { return ABILITY;  }   /* alias: 'skill "shield"'           */

"speed"         { return SPEED;    }   /* set movement speed                 */

/* ── UNIT TOKENS ────────────────────────────────────────────────────────── */
"steps"         { return STEPS;   }    /* distance unit (plural)             */
"step"          { return STEPS;   }    /* distance unit (singular)           */
"degrees"       { return DEGREES; }    /* angle unit (plural)                */
"degree"        { return DEGREES; }    /* angle unit (singular)              */
"deg"           { return DEGREES; }    /* short form                         */

/* ── LITERAL TOKENS ─────────────────────────────────────────────────────── */
{NUMBER}        {
                    /*  Convert matched text to a double and store it in
                     *  yylval so the parser can read the numeric value.    */
                    yylval.fval = atof(yytext);
                    return NUMBER;
                }

{STRING}        {
                    /*  Strip the surrounding double-quotes before storing. */
                    char *s = strdup(yytext + 1);   /* skip opening quote   */
                    s[strlen(s) - 1] = '\0';         /* remove closing quote */
                    yylval.sval = s;
                    return STRING;
                }

/* ── IGNORED TOKENS ─────────────────────────────────────────────────────── */
{COMMENT}       { /* skip single-line comments                */            }
{WHITESPACE}    { /* skip spaces, tabs, carriage returns       */            }
{NEWLINE}       { line_num++;  /* count lines for error messages */          }

/* ── UNKNOWN CHARACTER ──────────────────────────────────────────────────── */
.               {
                    /*  Any character not matched above is an error.
                     *  We print a message and continue scanning.           */
                    fprintf(stderr,
                        "Lexer Error (line %d): unknown character '%s'\n",
                        line_num, yytext);
                }

%%
/*
 *  End of robot_lexer.l
 *
 *  No user code section is needed here.
 *  The parser calls yylex() which is auto-generated from the rules above.
 */
