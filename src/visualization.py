from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

SUMMARY_RESULTS_PATH = RESULTS_DIR / "summary_results.csv"  
COMPARISON_RESULTS_PATH = RESULTS_DIR / "comparison_results.csv"

def save_average_lengths_chart(summary_df: pd.DataFrame) -> None:
    metrics = [
        "average_primary_length",
        "average_backup_length",
        "average_total_length",
    ]

    chart_df = summary_df.set_index("algorithm")[metrics]

    plt.figure(figsize=(8, 6))
    chart_df.plot(kind="bar")

    plt.title("Average path lengths ")
    plt.xlabel("Algorithm")
    plt.ylabel("Average number of links")
    plt.xticks(rotation=0)
    plt.legend(
        [
            "Primary path",
            "Backup path",
            "Total length",
        ]
    )
    plt.tight_layout()

    output_path = FIGURES_DIR / "average_lengths.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")

def save_rejection_ratio_chart(summary_df: pd.DataFrame) -> None:
    plt.figure(figsize=(7, 5))

    plt.bar(
        summary_df["algorithm"],
        summary_df["rejection_ratio"]
    )

    plt.title("Request rejection ratio")
    plt.xlabel("Algorithm")
    plt.ylabel("Rejection ratio")
    plt.ylim(0, 1)
    plt.tight_layout()

    output_path = FIGURES_DIR / "rejection_ratio.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")

def save_suurballe_better_cases_chart(comparison_df: pd.DataFrame) -> None:
    suurballe_better = comparison_df[
        comparison_df["total_length_difference"] > 0
    ].copy()

    if suurballe_better.empty:
        print("No cases where Suurballe is better. Chart skipped.")
        return

    suurballe_better["pair"] = (
        suurballe_better["source"].astype(str)
        + "-" 
        + suurballe_better["target"].astype(str)
    )

    chart_df = suurballe_better[
        [
            "pair",
            "total_length_naive",
            "total_length_suurballe",
            ]
        ].set_index("pair")

    plt.figure(figsize=(8, 5))
    chart_df.plot(kind="bar")

    plt.title("Cases where Suurballe gives shorter paths")
    plt.xlabel("Node pair")
    plt.ylabel("Total number of links")
    plt.xticks(rotation=0)
    plt.legend(["Naive", "Suurballe"])
    plt.tight_layout()

    output_path = FIGURES_DIR / "suurballe_better_cases.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")

def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    summary_df = pd.read_csv(SUMMARY_RESULTS_PATH)
    comparison_df = pd.read_csv(COMPARISON_RESULTS_PATH)

    save_average_lengths_chart(summary_df)
    save_rejection_ratio_chart(summary_df)
    save_suurballe_better_cases_chart(comparison_df)

    print()
    print("Visualization completed.")

if __name__ == "__main__":
    main()