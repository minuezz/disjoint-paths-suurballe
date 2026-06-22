from pathlib import Path
import csv

import networkx as nx
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOPOLOGY_PATH = PROJECT_ROOT / "data" / "topology_c4_edges.csv"

C4_POSITIONS = {
    1: (8.0, 7.5),
    2: (4.6, 4.7),
    3: (9.8, 4.3),
    4: (6.3, 2.0),
    5: (7.2, 4.3),
    6: (3.0, 1.6),
    7: (6.7, 6.1),
    8: (5.9, 3.4),
    9: (1.7, 0.3),
    10: (2.0, 6.7),
    11: (4.2, 2.2),
    12: (4.0, 6.3),
    13: (0.5, 3.8),
    14: (7.0, 3.0),
    15: (7.4, 0.3),
    16: (8.4, 6.0),
}


def load_c4_topology(csv_path: Path = DEFAULT_TOPOLOGY_PATH) -> nx.Graph:
    graph = nx.Graph()

    graph.add_nodes_from(range(1, 17))

    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            source = int(row["source"])
            target = int(row["target"])
            graph.add_edge(source, target, weight=1)

    return graph


def print_topology_info(graph: nx.Graph) -> None:
    print("C4 topology information")
    print("-----------------------")
    print(f"Number of nodes: {graph.number_of_nodes()}")
    print(f"Number of edges: {graph.number_of_edges()}")
    print(f"Is connected: {nx.is_connected(graph)}")
    print()
    print("Edges:")
    for edge in sorted(graph.edges()):
        print(edge)


def draw_topology(
    graph: nx.Graph,
    output_path: Path | None = None,
    show: bool = True,
) -> None:
    plt.figure(figsize=(10, 8))

    nx.draw_networkx_nodes(
        graph,
        pos=C4_POSITIONS,
        node_size=1200,
    )

    nx.draw_networkx_labels(
        graph,
        pos=C4_POSITIONS,
        font_size=14,
    )

    nx.draw_networkx_edges(
        graph,
        pos=C4_POSITIONS,
        width=2,
    )

    plt.title("C4 network topology")
    plt.axis("off")

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, bbox_inches="tight")

    if show:
        plt.show()

    plt.close()


if __name__ == "__main__":
    G = load_c4_topology()

    print_topology_info(G)

    output_file = PROJECT_ROOT / "results" / "figures" / "topology_c4.png"
    draw_topology(G, output_path=output_file, show=True)

    print()
    print(f"Topology figure saved to: {output_file}")