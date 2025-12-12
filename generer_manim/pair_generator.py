"""
Générateur de paires (dsl, code_manim).

generate_pairs(n, seed) renvoie une liste de dicts :
    {"dsl": "<programme DSL>", "code": "<code manim généré>"}
Pas d'écriture de fichier.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence

from traducteur_manim.generator import generate_manim_from_source


# --- Modèles de génération ---

SHAPES = ("circle", "square", "rectangle", "line", "text")


@dataclass
class ObjectSpec:
    obj_id: str
    shape: str


def generate_pairs(n: int = 10, seed: int | None = None) -> List[Dict[str, str]]:
    """
    Génère n paires (dsl, code_manim) et les retourne sous forme de liste.
    - seed permet de rendre la génération déterministe.
    """
    if seed is not None:
        random.seed(seed)

    pairs: List[Dict[str, str]] = []
    for _ in range(max(0, n)):
        dsl_program = _build_program()
        code = generate_manim_from_source(dsl_program)
        pairs.append({"dsl": dsl_program, "code": code})
    return pairs


# --- Construction d'un petit programme DSL ---

def _build_program() -> str:
    obj_specs = _create_objects()
    instructions: List[str] = []

    # Créations
    for spec in obj_specs:
        instructions.append(_emit_create(spec))

    # Animations (move/rotate) choisies parmi les objets créés
    anims = _build_animations(obj_specs, max_instr=3)
    instructions.extend(anims)

    return "\n".join(instructions)


def _create_objects() -> List[ObjectSpec]:
    count = random.randint(1, 3)
    specs: List[ObjectSpec] = []
    for idx in range(count):
        shape = random.choice(SHAPES)
        specs.append(ObjectSpec(obj_id=f"obj{idx+1}", shape=shape))
    return specs


def _emit_create(spec: ObjectSpec) -> str:
    base = f"CREATE {spec.shape}(id={spec.obj_id}"
    if spec.shape == "circle":
        radius = round(random.uniform(0.5, 2.0), 2)
        base += f", radius={radius}"
    elif spec.shape == "square":
        size = round(random.uniform(0.5, 2.0), 2)
        base += f", size={size}"
    elif spec.shape == "rectangle":
        width = round(random.uniform(1.0, 3.0), 2)
        height = round(random.uniform(0.5, 2.0), 2)
        base += f", width={width}, height={height}"
    elif spec.shape == "line":
        x1, y1, x2, y2 = [_rand_coord() for _ in range(4)]
        base += f", start=({x1},{y1}), end=({x2},{y2})"
    elif spec.shape == "text":
        content = random.choice(("Hello", "Manim", "DSL", "Demo"))
        base += f', content="{content}"'

    x, y = _rand_coord(), _rand_coord()
    base += f", x={x}, y={y}"
    base += ")"
    return base


def _build_animations(specs: Sequence[ObjectSpec], max_instr: int) -> List[str]:
    anims: List[str] = []
    if not specs:
        return anims
    instr_count = random.randint(0, max_instr)
    for _ in range(instr_count):
        target = random.choice(specs)
        if random.random() < 0.6:
            dx, dy = _rand_delta(), _rand_delta()
            dur = _rand_duration()
            anims.append(f"MOVE(id={target.obj_id}, dx={dx}, dy={dy}, duration={dur})")
        else:
            angle = round(random.uniform(15, 180), 1)
            dur = _rand_duration()
            anims.append(f"ROTATE(id={target.obj_id}, angle={angle}, duration={dur})")
    return anims


def _rand_coord() -> float:
    return round(random.uniform(-3.0, 3.0), 2)


def _rand_delta() -> float:
    return round(random.uniform(-2.0, 2.0), 2)


def _rand_duration() -> float:
    return round(random.uniform(0.5, 3.0), 2)


__all__ = ["generate_pairs"]
