"""
Grammaire Lark pour le DSL Manim.

Ce fichier définit uniquement :
- le texte de la grammaire (DSL_GRAMMAR)
- une petite fonction make_parser() pour construire un parseur Lark

L’AST et la logique de transformation seront gérés dans parser_engine.py / ast_nodes.py.
"""

from lark import Lark

DSL_GRAMMAR = r"""
// --------- Règle de départ ---------

?start: programme

programme: instruction+


// --------- Instructions ---------

instruction: instr_create
           | instr_move
           | instr_rotate


// --------- CREATE ---------

instr_create: "CREATE" shape "(" create_param_list? ")"

shape: SHAPE

SHAPE: "circle"
     | "square"
     | "triangle"
     | "rectangle"
     | "line"
     | "text"


create_param_list: create_param ("," create_param)*

create_param: param_id
            | param_radius
            | param_size
            | param_width
            | param_height
            | param_x
            | param_y
            | param_start
            | param_end
            | param_content

param_id: "id" "=" IDENT
param_radius: "radius" "=" NUM
param_size: "size" "=" NUM
param_width: "width" "=" NUM
param_height: "height" "=" NUM
param_x: "x" "=" NUM
param_y: "y" "=" NUM
param_start: "start" "=" "(" NUM "," NUM ")"
param_end: "end" "=" "(" NUM "," NUM ")"
param_content: "content" "=" STRING



// --------- MOVE ---------

instr_move: "MOVE" "(" "id" "=" IDENT ("," move_param_list)? ")"

move_param_list: move_param ("," move_param)*

move_param: param_dx
          | param_dy
          | param_duration

param_dx: "dx" "=" NUM
param_dy: "dy" "=" NUM
param_duration: "duration" "=" NUM

// --------- ROTATE ---------

// angle obligatoire, duration optionnelle
instr_rotate: "ROTATE" "(" "id" "=" IDENT "," "angle" "=" NUM ("," "duration" "=" NUM)? ")"


// --------- Terminaux (tokens) ---------

IDENT: /[a-zA-Z_][a-zA-Z0-9_]*/
NUM: SIGNED_NUMBER
STRING: ESCAPED_STRING

%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%import common.WS

%ignore WS
"""


def make_parser() -> Lark:
    """
    Construit et renvoie un parseur Lark pour le DSL Manim.
    (On utilisera cette fonction dans parser_engine.py)
    """
    return Lark(DSL_GRAMMAR, start="programme", parser="lalr")
