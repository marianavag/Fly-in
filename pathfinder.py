import heapq
from models import Graph


class PathNotFoundError(Exception):
    """Raised when no valid route exists between two zones."""
    pass


class PathFinder:
    """Computes cost-aware routes through the graph."""

    @classmethod
    def zone_turn_cost(cls, graph: Graph, zone_name: str) -> int:
        """Turn cost of entering a zone, based on its zone_type."""
        if zone_name not in graph.zones:
            raise KeyError(f"Zone '{zone_name}' not defined.")
        zone = graph.zones[zone_name]
        if zone.zone_type in ("normal", "priority"):
            return 1
        elif zone.zone_type == "restricted":
            return 2
        elif zone.zone_type == "blocked":
            raise ValueError("Zone type is not accessible.")
        raise ValueError("Zone type not valid.")

    @classmethod
    def zone_preference_weight(cls, graph: Graph, zone_name: str) -> int:
        """Returns a weight to prioritize 'priority' zones."""
        zone = graph.zones[zone_name]
        if zone.zone_type == "priority":
            return 0
        return 1

    @classmethod
    def find_path(cls, graph: Graph, start: str, end: str,
                  blocked_nodes: set[str] | None = None,
                  blocked_connections: set[frozenset[str]] | None = None
                  ) -> list[str]:
        """Finds the lowest-cost route from start to end using Dijkstra."""
        blocked_nodes = blocked_nodes or set()
        blocked_connections = blocked_connections or set()
        if start not in graph.zones or end not in graph.zones:
            raise PathNotFoundError("Start or end zone does not exist.")
        if (
            start in blocked_nodes
            or end in blocked_nodes
            or graph.zones[start].zone_type == "blocked"
            or graph.zones[end].zone_type == "blocked"
        ):
            raise PathNotFoundError("Start or end zone is inaccessible.")
        heap: list[tuple[int, int, str]] = [(0, 0, start)]
        best_cost: dict[str, tuple[int, int]] = {start: (0, 0)}
        came_from: dict[str, str] = {}
        visited: set[str] = set()
        while heap:
            turns, pref, current_zone = heapq.heappop(heap)
            if current_zone in visited:
                continue
            if (turns, pref) != best_cost[current_zone]:
                continue
            visited.add(current_zone)
            if current_zone == end:
                break
            for neighbour in graph.adjacency[current_zone]:
                if neighbour in blocked_nodes:
                    continue
                if graph.zones[neighbour].zone_type == "blocked":
                    continue
                if neighbour in visited:
                    continue
                connection = frozenset((current_zone, neighbour))
                if connection in blocked_connections:
                    continue
                new_turns = turns + cls.zone_turn_cost(graph, neighbour)
                new_pref = pref + cls.zone_preference_weight(graph, neighbour)
                new_cost = (new_turns, new_pref)
                if (neighbour not in best_cost
                        or new_cost < best_cost[neighbour]):
                    best_cost[neighbour] = new_cost
                    came_from[neighbour] = current_zone
                    heapq.heappush(heap, (new_turns, new_pref, neighbour))
        if end not in best_cost:
            raise PathNotFoundError(
                f"No path found between '{start}' and '{end}'.")
        path = []
        current = end
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path

    @classmethod
    def find_multiple_paths(cls, graph: Graph, start: str,
                            end: str, max_paths: int = 2) -> list[list[str]]:
        """Calculates multiple alternative paths."""
        paths = []
        blocked_nodes: set[str] = set()
        blocked_connections: set[frozenset[str]] = set()
        for _ in range(max_paths):
            try:
                path = cls.find_path(graph, start, end, blocked_nodes,
                                     blocked_connections)
                paths.append(path)
                if len(path) > 1:
                    blocked_connections.add(frozenset((path[0], path[1])))
            except PathNotFoundError:
                break
        if not paths:
            paths.append(cls.find_path(graph, start, end))
        return paths
