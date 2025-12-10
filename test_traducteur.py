from traducteur_manim.generator import generate_manim_from_source

src = """
CREATE circle(id=c1, radius=1, x=0, y=0)
CREATE square(id=s1, size=2, x=2, y=0)
MOVE(id=c1, dx=1, dy=0, duration=2)
ROTATE(id=s1, angle=45, duration=1)
"""

code = generate_manim_from_source(src, class_name="MyGeneratedScene")
print(code)
