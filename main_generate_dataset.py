from generer_manim.pair_generator import generate_pairs

def main() -> None:
    pairs = generate_pairs(n=10, seed=42)

    print(f"{len(pairs)=}\n")
    for i, p in enumerate(pairs, 1):
        print(f"--- Pair {i} ---")
        print("DSL:")
        print(p["dsl"])
        print("\nCODE (first 300 chars):")
        print(p["code"][:300])
        print()

if __name__ == "__main__":
    main()
