from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

RAW_RESULTS_PATH = RESULTS_DIR / "raw_results.csv"
COMPARISON_PATH = RESULTS_DIR / "comparison_results.csv"

def analyze_algorithm_differences() -> pd.DataFrame:
    raw_df = pd.read_csv(RAW_RESULTS_PATH)

    naive_df = raw_df[raw_df["algorithm"] == "naive"].copy()
    suurballe_df = raw_df[raw_df["algorithm"] == "suurballe"].copy()

    naive_df = naive_df.set_index(["source", "target"])
    suurballe_df = suurballe_df.set_index(["source", "target"])

    comparison_df = naive_df[
        [
            "status",
            "primary_path",
            "backup_path",
            "primary_length",
            "backup_length",
            "total_length",
        ]
    ].join(
        suurballe_df[
            [
                "status",
                "primary_path",
                "backup_path",
                "primary_length",
                "backup_length",
                "total_length",
            ]
        ],
        lsuffix="_naive",
        rsuffix="_suurballe",
    )

    comparison_df["total_length_difference"] = (
        comparison_df["total_length_naive"] 
        - comparison_df["total_length_suurballe"]
    )

    comparison_df["backup_length_difference"] = (
        comparison_df["backup_length_naive"] 
        - comparison_df["backup_length_suurballe"]
    )

    comparison_df = comparison_df.reset_index()

    return comparison_df

def main() -> None:
    comparison_df = analyze_algorithm_differences()

    comparison_df.to_csv(COMPARISON_PATH, index=False)

    different_results = comparison_df[
        comparison_df["total_length_difference"] != 0
    ]

    suurballe_better = comparison_df[
        comparison_df["total_length_difference"] > 0
    ]

    naive_better = comparison_df[
        comparison_df["total_length_difference"] < 0
    ]

    print("Comparison completed.")
    print()
    print(f"Total compared pairs: {len(comparison_df)}")
    print(f"Different total length results: {len(different_results)}")
    print(f"Suurballe better cases: {len(suurballe_better)}")
    print(f"Naive better cases: {len(naive_better)}")
    print()
    print("Cases where Suurballe is better:")
    print(
        suurballe_better[
            [
                "source",
                "target", 
                "primary_length_naive",
                "backup_length_naive",
                "total_length_naive",
                "primary_length_suurballe",
                "backup_length_suurballe",
                "total_length_suurballe",
                "total_length_difference",
            ]
        ].to_string(index=False)
    )
    print()
    print(f"Comparison results saved to: {COMPARISON_PATH}")

if __name__ == "__main__":
    main()