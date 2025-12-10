from parser_engine import parse_string

src = """
CREATE circle(id=c1, radius=1, x=0, y=0)
CREATE square(id=s1, size=2, x=1, y=1)
MOVE(id=c1, dx=1, dy=0, duration=2)
ROTATE(id=s1, angle=45, duration=1)
"""

def main():
    program = parse_string(src)
    print("=== Program ===")
    print(program)
    print("\n=== Instructions ===")
    for instr in program.instructions:
        print(instr)

if __name__ == "__main__":
    main()



