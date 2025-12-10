"""
Définition de l'AST (Abstract Syntax Tree) pour le DSL Manim.
On définit ici des classes Python simples qui représentent
les instructions de notre langage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


# ---------- Types de base ----------

Point = Tuple[float, float]


# ---------- Instructions ----------

@dataclass
class CreateInstruction:
    """
    Représente une instruction de type :
        CREATE <shape>(id=..., ...)
    """
    shape: str                      # "circle", "square", ...
    id: Optional[str] = None        # identifiant de l'objet (obligatoire en pratique)
    radius: Optional[float] = None  # pour circle
    size: Optional[float] = None    # pour square / triangle
    width: Optional[float] = None   # pour rectangle / line
    height: Optional[float] = None  # pour rectangle
    x: Optional[float] = None       # position initiale (x, y)
    y: Optional[float] = None
    start: Optional[Point] = None   # début de segment (pour line)
    end: Optional[Point] = None     # fin de segment (pour line)
    content: Optional[str] = None   # texte (pour text)


@dataclass
class MoveInstruction:
    """
    Représente une instruction de type :
        MOVE(id=..., dx=..., dy=..., duration=...)
    """
    target_id: str
    dx: float = 0.0
    dy: float = 0.0
    duration: Optional[float] = None


@dataclass
class RotateInstruction:
    """
    Représente une instruction de type :
        ROTATE(id=..., angle=..., duration=...)
    """
    target_id: str
    angle: float
    duration: Optional[float] = None


# Union pratique pour typer les listes d'instructions
Instruction = Union[CreateInstruction, MoveInstruction, RotateInstruction]


@dataclass
class Program:
    """
    Représente un programme complet :
        une suite d'instructions (CREATE / MOVE / ROTATE).
    """
    instructions: List[Instruction]
