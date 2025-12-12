"""
Générateur de paires (dsl, code_manim).

generate_pairs(n, seed) renvoie une liste de dicts :
    {"dsl": "<programme DSL>", "code": "<code manim généré>"}

Pas d'écriture de fichier : juste une liste Python.
Dataset visé : diversité de structures (CREATE/MOVE/ROTATE dans n'importe quel ordre),
tout en restant SYNTAXIQUEMENT valide (pas forcément exécutable Manim).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence

from traducteur_manim.generator import generate_manim_from_source


# --- Modèles de génération ---

# On reste aligné avec ce que le traducteur sait générer proprement
SHAPES = ("circle", "square", "rectangle", "line", "text")
TEXT_CONTENTS = ("Hello", "Manim", "DSL", "Demo", "Test", "Circle", "Square")


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


# --- Construction d'un programme DSL varié ---

def _build_program() -> str:
    """
    Produit un programme DSL sous forme de texte multi-lignes.

    Stratégie :
    - on choisit un nombre total d'instructions (1..8)
    - chaque instruction est tirée au hasard parmi CREATE/MOVE/ROTATE
    - on peut utiliser des ids qui n'ont jamais été créés (dataset syntaxique)
    """
    instructions: List[str] = []

    total_instr = random.randint(1, 8)

    # pool d'ids potentiels (certains créés, certains non)
    # (ça permet d'avoir des MOVE/ROTATE sans CREATE préalable)
    id_pool = [f"obj{i}" for i in range(1, random.randint(2, 8) + 1)]

    # on garde quand même une chance de créer des objets,
    # sinon le code Manim généré sera souvent "vide"
    p_create = 0.55
    p_move = 0.30
    p_rotate = 0.15

    # possibilité de "forcer" au moins un CREATE une partie du temps
    force_one_create = random.random() < 0.7

    created_any = False
    for k in range(total_instr):
        kind = _choice_weighted(
            [("CREATE", p_create), ("MOVE", p_move), ("ROTATE", p_rotate)]
        )

        # Option : garantir au moins un CREATE dans le programme
        if force_one_create and (k == total_instr - 1) and (not created_any):
            kind = "CREATE"

        if kind == "CREATE":
            spec = _random_object_spec(id_pool=id_pool)
            instructions.append(_emit_create(spec))
            created_any = True
        elif kind == "MOVE":
            target_id = random.choice(id_pool)
            instructions.append(_emit_move(target_id))
        else:
            target_id = random.choice(id_pool)
            instructions.append(_emit_rotate(target_id))

    return "\n".join(instructions)


def _random_object_spec(id_pool: Sequence[str]) -> ObjectSpec:
    # On choisit un id au hasard (peut être "déjà utilisé" : syntaxiquement ok)
    obj_id = random.choice(id_pool)
    shape = random.choice(SHAPES)
    return ObjectSpec(obj_id=obj_id, shape=shape)


# --- Emission des instructions DSL ---

def _emit_create(spec: ObjectSpec) -> str:
    base = f"CREATE {spec.shape}(id={spec.obj_id}"

    if spec.shape == "circle":
        radius = _rand_in(0.5, 2.0, ndigits=2)
        base += f", radius={radius}"

    elif spec.shape == "square":
        size = _rand_in(0.5, 2.0, ndigits=2)
        base += f", size={size}"

    elif spec.shape == "rectangle":
        width = _rand_in(1.0, 3.0, ndigits=2)
        height = _rand_in(0.5, 2.0, ndigits=2)
        base += f", width={width}, height={height}"

    elif spec.shape == "line":
        x1, y1, x2, y2 = [_rand_coord() for _ in range(4)]
        base += f", start=({x1},{y1}), end=({x2},{y2})"

    elif spec.shape == "text":
        content = random.choice(TEXT_CONTENTS)
        base += f', content="{content}"'

    # x,y toujours présents (comme dans ton générateur initial)
    x, y = _rand_coord(), _rand_coord()
    base += f", x={x}, y={y})"
    return base


def _emit_move(target_id: str) -> str:
    dx, dy = _rand_delta(), _rand_delta()

    # duration optionnelle parfois (pour diversifier)
    if random.random() < 0.25:
        return f"MOVE(id={target_id}, dx={dx}, dy={dy})"

    dur = _rand_duration()
    return f"MOVE(id={target_id}, dx={dx}, dy={dy}, duration={dur})"


def _emit_rotate(target_id: str) -> str:
    angle = _rand_in(15.0, 180.0, ndigits=1)

    # duration optionnelle parfois
    if random.random() < 0.25:
        return f"ROTATE(id={target_id}, angle={angle})"

    dur = _rand_duration()
    return f"ROTATE(id={target_id}, angle={angle}, duration={dur})"


# --- Helpers aléatoires ---

def _rand_coord() -> float:
    return _rand_in(-3.0, 3.0, ndigits=2)


def _rand_delta() -> float:
    return _rand_in(-2.0, 2.0, ndigits=2)


def _rand_duration() -> float:
    return _rand_in(0.5, 3.0, ndigits=2)


def _rand_in(a: float, b: float, ndigits: int) -> float:
    return round(random.uniform(a, b), ndigits)


def _choice_weighted(items: Sequence[tuple[str, float]]) -> str:
    """
    Choisit un item selon des poids.
    items = [("CREATE", 0.5), ("MOVE", 0.3), ("ROTATE", 0.2)]
    """
    total = 0.0
    for _, w in items:
        total += max(0.0, w)

    r = random.uniform(0.0, total)
    upto = 0.0
    for name, w in items:
        w = max(0.0, w)
        upto += w
        if r <= upto:
            return name

    # fallback
    return items[-1][0]


__all__ = ["generate_pairs"]

