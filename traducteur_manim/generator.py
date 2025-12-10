"""
Traducteur DSL -> code Manim.

On prend un Program (AST) et on génère une classe Manim
avec une scène simple.
"""

from parser_manim.ast_nodes import (
    Program,
    CreateInstruction,
    MoveInstruction,
    RotateInstruction,
)
from parser_manim.parser_engine import parse_string


def generate_manim_scene(program: Program, class_name: str = "GeneratedScene") -> str:
    lines: list[str] = []

    lines.append("from manim import *")
    lines.append("")
    lines.append(f"class {class_name}(Scene):")
    lines.append("    def construct(self):")
    lines.append("        objects = {}  # id -> mobject")
    lines.append("")

    # Génération des créations d'objets
    for instr in program.instructions:
        if isinstance(instr, CreateInstruction):
            _emit_create(lines, instr)

    # Génération des animations (MOVE / ROTATE)
    for instr in program.instructions:
        if isinstance(instr, MoveInstruction):
            _emit_move(lines, instr)
        elif isinstance(instr, RotateInstruction):
            _emit_rotate(lines, instr)

    return "\n".join(lines)


def _emit_create(lines: list[str], instr: CreateInstruction) -> None:
    obj_id = instr.id
    if not obj_id:
        return  # on ignore les objets sans id

    x = instr.x or 0.0
    y = instr.y or 0.0

    if instr.shape == "circle":
        radius = instr.radius or 1.0
        ctor = f"Circle(radius={radius})"
    elif instr.shape == "square":
        size = instr.size or 1.0
        ctor = f"Square(side_length={size})"
    elif instr.shape == "rectangle":
        width = instr.width or 2.0
        height = instr.height or 1.0
        ctor = f"Rectangle(width={width}, height={height})"
    elif instr.shape == "line":
        if instr.start and instr.end:
            (x1, y1) = instr.start
            (x2, y2) = instr.end
            ctor = f"Line(start=[{x1}, {y1}, 0], end=[{x2}, {y2}, 0])"
        else:
            ctor = "Line()"
    elif instr.shape == "text":
        content = instr.content or ""
        ctor = f'Text("{content}")'
    else:
        ctor = "Dot()"

    lines.append(f"        obj_{obj_id} = {ctor}.move_to([{x}, {y}, 0])")
    lines.append(f"        objects['{obj_id}'] = obj_{obj_id}")
    lines.append("        self.add(obj_{})".format(obj_id))
    lines.append("")


def _emit_move(lines: list[str], instr: MoveInstruction) -> None:
    dx = instr.dx or 0.0
    dy = instr.dy or 0.0
    duration = instr.duration or 1.0

    lines.append(
        f"        self.play(objects['{instr.target_id}'].animate.shift(RIGHT*{dx} + UP*{dy}), "
        f"run_time={duration})"
    )


def _emit_rotate(lines: list[str], instr: RotateInstruction) -> None:
    angle = instr.angle or 0.0
    duration = instr.duration or 1.0

    lines.append(
        f"        self.play(objects['{instr.target_id}'].animate.rotate({angle}*DEGREES), "
        f"run_time={duration})"
    )


def generate_manim_from_source(src: str, class_name: str = "GeneratedScene") -> str:
    """
    Helper pratique : prend directement du DSL en entrée,
    parse -> AST -> code Manim.
    """
    program = parse_string(src)
    return generate_manim_scene(program, class_name)
