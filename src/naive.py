import networkx as nx

from topology import load_c4_topology

def path_to_edges(path: list[int]) -> list[tuple[int, int]]:
    return list(zip(path[:-1], path[1:]))

def normalize_edge(edge: tuple[int, int]) -> tuple[int, int]:
    u, v = edge
    return tuple(sorted((u,v)))

def are_edges_disjoint(path_1: list[int], path_2: list[int]) -> bool:
    edges_1 = {normalize_edge(edge) for edge in path_to_edges(path_1)}
    edges_2 = {normalize_edge(edge) for edge in path_to_edges(path_2)}
    return edges_1.isdisjoint(edges_2)

def path_length(path: list[int]) -> int:
    return len(path) - 1

def find_naive_disjoint_paths(
        graph: nx.Graph,
        source: int,
        target: int,
) -> dict:
    try:
        primary_path = nx.dijkstra_path(
            graph, 
            source=source,
            target=target,
            weight="weight",
        )
    except nx.NetworkXNoPath:
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
    
    modified_graph = graph.copy()
    primary_edges = path_to_edges(primary_path)
    modified_graph.remove_edges_from(primary_edges)

    try:
        backup_path = nx.dijkstra_path(
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
            "primary_path": primary_path,
            "backup_path": None,
            "primary_length": path_length(primary_path),
            "backup_length": None,
            "reason": "backup_path_not_found",
        }
    
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
        result = find_naive_disjoint_paths(G, source, target)

        print(f"\nPair: {source} -> {target}")
        print(f"Status: {result['status']}")
        print(f"Primary Path: {result['primary_path']}")
        print(f"Backup Path: {result['backup_path']}")
        print(f"Primary Length: {result['primary_length']}")
        print(f"Backup Length: {result['backup_length']}")

        if result['status'] == 'accepted':
            print(f"Edge Disjoint: {result['edge_disjoint']}")
        else:
            print(f"Reason: {result['reason']}")