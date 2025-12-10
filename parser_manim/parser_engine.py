"""
Moteur de parsing pour le DSL Manim.

- utilise la grammaire Lark définie dans grammar.py
- transforme l'arbre de parse en AST défini dans ast_nodes.py
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from lark import Lark, Transformer, Token, Tree, UnexpectedInput

from .grammar import make_parser
from .ast_nodes import (
    Program,
    CreateInstruction,
    MoveInstruction,
    RotateInstruction,
    Instruction,
)
from .errors import DslParseError




class ASTBuilder(Transformer):
    """
    Transformer Lark -> AST Python.

    On part de l'arbre brut fourni par Lark et on construit :
    - Program
    - CreateInstruction
    - MoveInstruction
    - RotateInstruction
    """

    # ---------- Terminaux ----------

    def IDENT(self, token: Token) -> str:
        # Identifiants -> str
        return str(token)

    def NUM(self, token: Token) -> float:
        # Nombres -> float
        return float(token)

    def STRING(self, token: Token) -> str:
        # ESCAPED_STRING inclut les guillemets, on les enlève
        s = str(token)
        if len(s) >= 2 and s[0] == s[-1] == '"':
            return s[1:-1]
        return s

    # ---------- Règles de haut niveau ----------

    def programme(self, children: List[Instruction]) -> Program:
        # programme: instruction+
        return Program(instructions=children)

    def instruction(self, children: List[Instruction]) -> Instruction:
        # instruction: instr_create | instr_move | instr_rotate
        # Il n'y a qu'un seul enfant
        return children[0]

    # ---------- CREATE ----------

    def SHAPE(self, token: Token) -> str:
        # SHAPE: "circle" | "square" | ...
        return str(token)

    def shape(self, children: List[Any]) -> str:
        # shape: SHAPE
        # La règle shape ne contient qu'un enfant : le SHAPE déjà converti en str
        return children[0]

    def create_param_list(self, children: List[Tuple[str, Any]]) -> Dict[str, Any]:
        # Liste de (nom, valeur) -> dict
        params: Dict[str, Any] = {}
        for name, value in children:
            params[name] = value
        return params

    def create_param(self, children: List[Any]) -> Tuple[str, Any]:
        """
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

        Chaque enfant est déjà un tuple (nom, valeur) renvoyé
        par param_id / param_radius / etc. On renvoie donc cet enfant.
        """
        return children[0]

    # --- Sous-paramètres de CREATE ---

    def param_id(self, children: List[Any]) -> Tuple[str, Any]:
        # param_id: "id" "=" IDENT
        ident = children[0]  # déjà une str via IDENT()
        return "id", ident

    def param_radius(self, children: List[Any]) -> Tuple[str, Any]:
        # param_radius: "radius" "=" NUM
        value = children[0]  # déjà un float via NUM()
        return "radius", value

    def param_size(self, children: List[Any]) -> Tuple[str, Any]:
        # param_size: "size" "=" NUM
        value = children[0]
        return "size", value

    def param_width(self, children: List[Any]) -> Tuple[str, Any]:
        # param_width: "width" "=" NUM
        value = children[0]
        return "width", value

    def param_height(self, children: List[Any]) -> Tuple[str, Any]:
        # param_height: "height" "=" NUM
        value = children[0]
        return "height", value

    def param_x(self, children: List[Any]) -> Tuple[str, Any]:
        # param_x: "x" "=" NUM
        value = children[0]
        return "x", value

    def param_y(self, children: List[Any]) -> Tuple[str, Any]:
        # param_y: "y" "=" NUM
        value = children[0]
        return "y", value

    def param_start(self, children: List[Any]) -> Tuple[str, Any]:
        # param_start: "start" "=" "(" NUM "," NUM ")"
        x, y = children  # NUM -> déjà float
        return "start", (x, y)

    def param_end(self, children: List[Any]) -> Tuple[str, Any]:
        # param_end: "end" "=" "(" NUM "," NUM ")"
        x, y = children
        return "end", (x, y)

    def param_content(self, children: List[Any]) -> Tuple[str, Any]:
        # param_content: "content" "=" STRING
        text = children[0]  # déjà str via STRING()
        return "content", text

    def instr_create(self, children: List[Any]) -> CreateInstruction:
        """
        instr_create: "CREATE" shape "(" create_param_list? ")"
        children = [shape, params_dict?]
        """
        shape = children[0]
        params: Dict[str, Any] = children[1] if len(children) > 1 else {}

        return CreateInstruction(
            shape=shape,
            id=params.get("id"),
            radius=_maybe_float(params.get("radius")),
            size=_maybe_float(params.get("size")),
            width=_maybe_float(params.get("width")),
            height=_maybe_float(params.get("height")),
            x=_maybe_float(params.get("x")),
            y=_maybe_float(params.get("y")),
            start=params.get("start"),
            end=params.get("end"),
            content=params.get("content"),
        )

    # ---------- MOVE ----------

    def move_param_list(self, children: List[Tuple[str, Any]]) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        for name, value in children:
            params[name] = value
        return params

    def move_param(self, children: List[Any]) -> Tuple[str, Any]:
        """
        move_param: param_dx
                  | param_dy
                  | param_duration

        Chaque enfant est déjà un tuple (nom, valeur)
        renvoyé par param_dx / param_dy / param_duration.
        """
        return children[0]

    def param_dx(self, children: List[Any]) -> Tuple[str, Any]:
        # param_dx: "dx" "=" NUM
        value = children[0]  # NUM déjà converti en float
        return "dx", value

    def param_dy(self, children: List[Any]) -> Tuple[str, Any]:
        # param_dy: "dy" "=" NUM
        value = children[0]
        return "dy", value

    def param_duration(self, children: List[Any]) -> Tuple[str, Any]:
        # param_duration: "duration" "=" NUM
        value = children[0]
        return "duration", value

    def instr_move(self, children: List[Any]) -> MoveInstruction:
        """
        instr_move: "MOVE" "(" "id" "=" IDENT ("," move_param_list)? ")"
        children = [target_id, params_dict?]
        """
        target_id = children[0]
        params: Dict[str, Any] = children[1] if len(children) > 1 else {}

        dx = _maybe_float(params.get("dx"), default=0.0)
        dy = _maybe_float(params.get("dy"), default=0.0)
        duration = _maybe_float(params.get("duration"))

        return MoveInstruction(
            target_id=target_id,
            dx=dx,
            dy=dy,
            duration=duration,
        )

    # ---------- ROTATE ----------

    def instr_rotate(self, children: List[Any]) -> RotateInstruction:
        """
        instr_rotate: "ROTATE" "(" "id" "=" IDENT "," "angle" "=" NUM ("," "duration" "=" NUM)? ")"
        children = [target_id, angle, (duration)?]
        """
        target_id = children[0]
        angle = children[1]
        duration = children[2] if len(children) > 2 else None

        angle_f = _maybe_float(angle)
        if angle_f is None:
            raise DslParseError("ROTATE nécessite un paramètre angle=...")

        duration_f = _maybe_float(duration)

        return RotateInstruction(
            target_id=target_id,
            angle=angle_f,
            duration=duration_f,
        )


# ---------- Helpers ----------

def _maybe_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


# ---------- API publique ----------

_parser: Lark | None = None
_builder = ASTBuilder()


def _get_parser() -> Lark:
    global _parser
    if _parser is None:
        _parser = make_parser()
    return _parser


def parse_string(source: str) -> Program:
    """
    Parse une chaîne DSL et renvoie un objet Program (AST).
    Lève DslParseError en cas d'erreur de syntaxe.
    """
    parser = _get_parser()
    try:
        tree: Tree = parser.parse(source)
        result = _builder.transform(tree)
        if not isinstance(result, Program):
            raise DslParseError("Le parseur n'a pas retourné un Program.")
        return result
    except UnexpectedInput as e:
        raise DslParseError(f"Erreur de syntaxe dans le DSL : {e}") from e

