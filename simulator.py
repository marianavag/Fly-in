from models import Graph, Drone, Connection
from typing import Optional
from pathfinder import PathFinder
from visual import TerminalVisual


class SimulationEngine:
    """Manages the movements of the drones in the graph."""

    def __init__(self, graph: Graph) -> None:
        """Initialises the simulation and creates the drones."""
        self.graph = graph
        start_hub = self.graph.start_hub
        end_hub = self.graph.end_hub
        if not start_hub or not end_hub:
            raise ValueError("Graph must have a start_hub and an end_hub.")
        self.paths = PathFinder.find_multiple_paths(graph, start_hub,
                                                    end_hub, max_paths=2)
        self.current_turn: int = 0
        self.drones: list[Drone] = []
        self._init_drones()

    def _init_drones(self) -> None:
        """Creates drones from start_hub and marks initial position."""
        start_hub = self.graph.start_hub
        if start_hub is None:
            raise ValueError("Start hub is missing.")
        for drone_id in range(1, self.graph.nb_drones + 1):
            assigned_path = self.paths[(drone_id - 1) % len(self.paths)]
            drone = Drone(
                drone_id=drone_id,
                current_zone_name=start_hub,
                path=assigned_path,
                progress=0
            )
            start_zone = self.graph.zones[start_hub]
            start_zone.current_drones.add(drone.drone_id)
            self.drones.append(drone)

    def is_finished(self) -> bool:
        """True when all drones arrived at end_hub."""
        for drone in self.drones:
            if drone.current_zone_name != self.graph.end_hub:
                return False
        return True

    def _get_connection(self,
                        zone_a: str, zone_b: str) -> Optional[Connection]:
        """Search the connection between two zones."""
        for connection in self.graph.connections:
            if {connection.zone_a, connection.zone_b} == {zone_a, zone_b}:
                return connection
        return None

    def _incoming(self, zone_name: str) -> int:
        """Counts drones in flight (restricted link) heading to a zone."""
        return sum(
            1 for other in self.drones
            if other.in_transit_turns > 0
            and other.path[other.progress + 1] == zone_name
        )

    def _move_drone(self, drone: Drone, destination_name: str) -> None:
        """Updates the position of the drone in the zones."""
        current_zone = self.graph.zones[drone.current_zone_name]
        if drone.drone_id in current_zone.current_drones:
            current_zone.current_drones.remove(drone.drone_id)
        self.graph.zones[destination_name].current_drones.add(drone.drone_id)
        drone.current_zone_name = destination_name
        drone.progress += 1

    def _process_drone_move(self, drone: Drone) -> Optional[str]:
        """Checks if drone can move and executes move."""
        if drone.progress + 1 >= len(drone.path):
            return None
        next_zone_name = drone.path[drone.progress + 1]
        next_zone = self.graph.zones[next_zone_name]
        if next_zone_name != self.graph.end_hub:
            taken = len(next_zone.current_drones) + self._incoming(
                next_zone_name)
            if taken >= next_zone.max_drones:
                return None
        link = self._get_connection(drone.current_zone_name, next_zone_name)
        if not link or link.current_traversals >= link.max_link_capacity:
            return None
        link.current_traversals += 1
        if next_zone.zone_type == "restricted" and drone.in_transit_turns == 0:
            drone.in_transit_turns += 1
            current_zone = self.graph.zones[drone.current_zone_name]
            if drone.drone_id in current_zone.current_drones:
                current_zone.current_drones.remove(drone.drone_id)
            connection_name = f"{link.zone_a}-{link.zone_b}"
            return f"D{drone.drone_id}-{connection_name}"
        self._move_drone(drone, next_zone_name)
        formatted_zone = TerminalVisual.format_zone(next_zone_name,
                                                    next_zone.zone_type,
                                                    next_zone.color)
        return f"D{drone.drone_id}-{formatted_zone}"

    def step(self) -> list[str]:
        """Executes 1 turn of the simulation."""
        for connection in self.graph.connections:
            connection.current_traversals = 0
        moves: list[str] = []
        for drone in sorted(self.drones,
                            key=lambda drone: drone.progress, reverse=True):
            if drone.current_zone_name == self.graph.end_hub:
                continue
            if drone.in_transit_turns > 0:
                drone.in_transit_turns = 0
                next_zone_name = drone.path[drone.progress + 1]
                next_zone = self.graph.zones[next_zone_name]
                if next_zone_name != self.graph.end_hub:
                    taken = len(next_zone.current_drones) + self._incoming(
                        next_zone_name)
                    if taken >= next_zone.max_drones:
                        drone.in_transit_turns = 1
                        continue
                self._move_drone(drone, next_zone_name)
                zone_type = next_zone.zone_type
                zone_color = next_zone.color
                formatted_zone = TerminalVisual.format_zone(next_zone_name,
                                                            zone_type,
                                                            zone_color)
                moves.append(f"D{drone.drone_id}-{formatted_zone}")
                continue
            move_msg = self._process_drone_move(drone)
            if move_msg:
                moves.append(move_msg)
        return moves

    def run(self) -> list[str]:
        """Runs the simulation until all drones reach the end_hub."""
        history: list[str] = []
        max_safety_iterations = 1000
        iteration = 0
        while not self.is_finished() and iteration < max_safety_iterations:
            moves = self.step()
            if not moves:
                raise RuntimeError(
                    f"Deadlock detected at turn {self.current_turn + 1}.")
            line = " ".join(moves)
            history.append(line)
            self.current_turn += 1
            iteration += 1
        if not self.is_finished():
            raise RuntimeError("Simulation exceeded maximum turn limits"
                               "(possible infinite loop).")
        return history
