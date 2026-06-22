from itertools import combinations
from pathlib import Path

import pandas as pd

from topology import load_c4_topology
from naive import find_naive_disjoint_paths
from suurballe import find_suurballe_disjoint_paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

RAW_RESULTS_PATH = RESULTS_DIR / "raw_results.csv"
SUMMARY_RESULTS_PATH = RESULTS_DIR / "summary_results.csv"

def path_to_string(path: list[int] | None) -> str:
    if path is None:
        return ""
    
    return "-".join(str(node) for node in path)

def run_algorithm_for_all_pairs(
    algorithm_name: str,
    algorithm_function,
) -> list[dict]:
    graph = load_c4_topology()
    nodes = sorted(graph.nodes())

    results = []

    for source, target in combinations(nodes, 2):
        result = algorithm_function(graph, source, target)
        
        primary_length = result["primary_length"]
        backup_length = result["backup_length"]

        if result["status"] == "accepted":
            total_length = primary_length + backup_length
        else:
            total_length = None

        results.append(
            {
                "algorithm": algorithm_name,
                "source": source,
                "target": target,
                "status": result["status"],
                "primary_path": path_to_string(result["primary_path"]),
                "backup_path": path_to_string(result["backup_path"]),
                "primary_length": primary_length,
                "backup_length": backup_length,
                "total_length": total_length,
                "edge_disjoint": result.get("edge_disjoint", False),
                "reason": result["reason"],
            }
        )
        
    return results

def run_all_experiments() -> list[dict]:
    results = []

    results.extend(
        run_algorithm_for_all_pairs(
            algorithm_name="naive",
            algorithm_function=find_naive_disjoint_paths,
        )
    )

    results.extend(run_algorithm_for_all_pairs(
        algorithm_name="suurballe",
        algorithm_function=find_suurballe_disjoint_paths,
        )
    )

    return results

def calculate_summary(results: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(results)

    summary_rows = []

    for algorithm, group in df.groupby("algorithm"):
        total_requests = len(group)
        accepted_requests = len(group[group["status"] == "accepted"])
        rejected_requests = len(group[group["status"] == "rejected"])

        rejection_ratio = rejected_requests / total_requests if total_requests > 0 else 0

        accepted_group = group[group["status"] == "accepted"]

        summary_rows.append(
            {
                "algorithm": algorithm,
                "total_requests": total_requests,
                "accepted_requests": accepted_requests,
                "rejected_requests": rejected_requests,
                "rejection_ratio": rejection_ratio,
                "average_primary_length": accepted_group["primary_length"].mean(),
                "average_backup_length": accepted_group["backup_length"].mean(),
                "average_total_length": accepted_group["total_length"].mean(),
            }
        )

    return pd.DataFrame(summary_rows)

def save_results(results: list[dict], summary_df: pd.DataFrame) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = pd.DataFrame(results)

    raw_df.to_csv(RAW_RESULTS_PATH, index=False)
    summary_df.to_csv(SUMMARY_RESULTS_PATH, index=False)

def main() -> None:
    results = run_all_experiments()
    summary_df = calculate_summary(results)

    save_results(results, summary_df)

    print("Experiments completed.")
    print()
    print("Summary:")
    print(summary_df.to_string(index=False))
    print()
    print(f"Raw results saved to: {RAW_RESULTS_PATH}")
    print(f"Summary results saved to: {SUMMARY_RESULTS_PATH}")

if __name__ == "__main__":
    main()