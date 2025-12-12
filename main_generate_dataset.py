"""
Script principal pour générer un dataset DSL -> Manim
et l'enregistrer au format Pickle (.pkl).
"""

import pickle
from generer_manim.pair_generator import generate_pairs


def main() -> None:
    # Paramètres du dataset
    N_PAIRS = 10_000
    SEED = 42
    OUTPUT_FILE = "dataset_dsl_manim.pkl"

    print("Génération du dataset...")
    pairs = generate_pairs(n=N_PAIRS, seed=SEED)

    print(f"Nombre de paires générées : {len(pairs)}")

    # Sauvegarde en Pickle
    print(f"Sauvegarde dans {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump(pairs, f)

    print("Dataset sauvegardé avec succès ✅")


if __name__ == "__main__":
    main()
