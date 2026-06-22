import networkx as nx

from topology import load_c4_topology
from naive import (
    path_to_edges,
    path_length,
    are_edges_disjoint,
)

def build_directed_graph(graph: nx.Graph) -> nx.DiGraph:
    directed_graph = nx.DiGraph()

    for u, v, data in graph.edges(data=True):
        weight = data.get("weight", 1)

        directed_graph.add_edge(u, v, weight=weight)
        directed_graph.add_edge(v, u, weight=weight)

    return directed_graph

def reweight_graph(
    directed_graph: nx.DiGraph,
    distances: dict[int, float],
) -> nx.DiGraph:
    reweighted_graph = nx.DiGraph()

    for u, v, data in directed_graph.edges(data=True):
        original_weight = data["weight"]
        new_weight = original_weight + distances[u] - distances[v]

        reweighted_graph.add_edge(u, v, weight=new_weight)

    return reweighted_graph

def modify_graph_for_second_path(
    graph: nx.DiGraph,
    primary_path: list[int],
) -> nx.DiGraph:
    modified_graph = graph.copy()

    for u, v in path_to_edges(primary_path):
        if modified_graph.has_edge(u, v):
            modified_graph.remove_edge(u, v)

        modified_graph.add_edge(v, u, weight=0)

    return modified_graph

def cancel_opposite_edges(
    directed_edges: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    edge_counts: dict[tuple[int, int], int] = {}

    for u, v in directed_edges:
        opposite_edge = (v, u)

        if edge_counts.get(opposite_edge, 0) > 0:
            edge_counts[opposite_edge] -= 1
        else:
            edge_counts[(u, v)] = edge_counts.get((u, v), 0) + 1
    
    remaining_edges = []

    for edge, count in edge_counts.items():
        remaining_edges.extend([edge] * count)
    
    return remaining_edges

def decompose_into_two_paths(
    directed_edges: list[tuple[int, int]],
    source: int,
    target: int,
) -> tuple[list[int], list[int]]:
    residual_graph = nx.DiGraph()
    residual_graph.add_edges_from(directed_edges)

    paths = []

    for _ in range(2):
        try:
            path = nx.shortest_path(
                residual_graph,
                source=source,
                target=target,
            )
        except nx.NetworkXNoPath as exc:
            raise ValueError("Cannot decompose result into two paths") from exc
        
        paths.append(path)
        residual_graph.remove_edges_from(path_to_edges(path))

    return paths[0], paths[1]

def find_suurballe_disjoint_paths(
    graph: nx.Graph,
    source: int,
    target: int,
) -> dict:
    if source == target:
        return {
            "source": source,
            "target": target,
            "status": "rejected",
            "primary_path": None,
            "backup_path": None,
            "primary_length": None,
            "backup_length": None,
            "reason": "source_equals_target",
        }
    
    directed_graph = build_directed_graph(graph)

    distances, shortest_paths = nx.single_source_dijkstra(
        directed_graph,
        source=source,
        weight="weight",
    )

    if target not in shortest_paths:
        return {
            "source": source,
            "target": target,
            "status": "rejected",
            "primary_path": None,
            "backup_path": None,
            "primary_length": None,
            "backup_length": None,
            "reason": "primary_path_not_found",
        }
    
    first_shortest_path = shortest_paths[target]

    reweighted_graph = reweight_graph(directed_graph, distances)
    modified_graph = modify_graph_for_second_path(
        reweighted_graph,
        first_shortest_path,
    )

    try:
        second_path = nx.shortest_path(
            modified_graph,
            source=source,
            target=target,
            weight="weight",
        )
    except nx.NetworkXNoPath:
        return {
            "source": source,
            "target": target,
            "status": "rejected",
            "primary_path": first_shortest_path,
            "backup_path": None,
            "primary_length": path_length(first_shortest_path),
            "backup_length": None,
            "reason": "backup_path_not_found",
        }
    
    combined_edges = path_to_edges(first_shortest_path) + path_to_edges(second_path)
    remaining_edges = cancel_opposite_edges(combined_edges)

    try:
        path_1, path_2 = decompose_into_two_paths(
            remaining_edges,
            source,
            target,
        )
    except ValueError:
        return {
            "source": source,
            "target": target,
            "status": "rejected",
            "primary_path": first_shortest_path,
            "backup_path": None,
            "primary_length": path_length(first_shortest_path),
            "backup_length": None,
            "reason": "cannot_decompose_result",
        }
    
    if not are_edges_disjoint(path_1, path_2):
        return {
            "source": source,
            "target": target,
            "status": "rejected",
            "primary_path": path_1,
            "backup_path": path_2,
            "primary_length": path_length(path_1),
            "backup_length": path_length(path_2),
            "reason": "paths_not_edge_disjoint",
        }
    
    primary_path, backup_path = sorted(
        [path_1, path_2],
        key=lambda path: (path_length(path), path),
    )

    return {
        "source": source,
        "target": target,
        "status": "accepted",
        "primary_path": primary_path,
        "backup_path": backup_path,
        "primary_length": path_length(primary_path),
        "backup_length": path_length(backup_path),
        "edge_disjoint": are_edges_disjoint(primary_path, backup_path),
        "reason": None,
    }

if __name__ == "__main__":
    G = load_c4_topology()

    test_pairs = [
        (1, 15),
        (10, 4),
        (13, 16),
        (6, 3),
    ]

    for source, target in test_pairs:
        result = find_suurballe_disjoint_paths(G, source, target)

        print(f"\nPair: {source} -> {target}")
        print(f"Status: {result['status']}")
        print(f"Primary path: {result['primary_path']}")
        print(f"Backup path: {result['backup_path']}")
        print(f"Primary length: {result['primary_length']}")
        print(f"Backup length: {result['backup_length']}")

        if result["status"] == "accepted":
            print(f"Edge disjoint: {result['edge_disjoint']}")
        else:
            print(f"Reason: {result['reason']}")