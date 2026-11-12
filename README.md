*This project has been created as part of the 42 curriculum by mgomes-v.*

# Fly-In

## Description

**Fly-In** is an algorithmic simulation engine in Python built to route a fleet of drones through an interconnected network of hubs. The engine reads map configurations, constructs an internal graph representation, evaluates multi-path routing, and simulates step-by-step drone movement while respecting zone capacities, connection limits, and zone traversal delays.

The application produces structured terminal output formatted with color-coded ANSI visual elements for monitoring network congestion and drone state transitions.

## Instructions

### Prerequisites

* Python 3.10 or higher
* `pip` package manager

### Environment Setup

Install necessary project dependencies:

```bash
make install
```

### Execution

Run the simulation by providing a path to a map configuration file:

```bash
make run ARGS="maps/easy/01_linear_path.txt"
# Alternatively, launch directly:
python3 main.py maps/easy/01_linear_path.txt
```

### Development Commands

```bash
make lint        # Run flake8 and mypy static code analyses
make lint-strict # Run strict typing compliance checks
make debug       # Execute under Python debugger (pdb)
make clean       # Remove bytecode and cache artifacts
```

## Map Format

Map files define total drones (`nb_drones`), start/end hubs, intermediate hubs, and connections. Metadata specified inside brackets defines attributes such as `max_drones`, `max_link_capacity`, `zone` type (`normal`, `priority`, `restricted`, `blocked`), and visual `color`.

### Example Input Map (`maps/easy/01_linear_path.txt`)

```text
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [zone=normal color=blue max_drones=1]
hub: waypoint2 2 0 [zone=normal color=cyan max_drones=1]
end_hub: goal 3 0 [color=yellow]

connection: start-waypoint1 [max_link_capacity=1]
connection: waypoint1-waypoint2 [max_link_capacity=1]
connection: waypoint2-goal [max_link_capacity=1]
```

## Architecture & Algorithm Explanation

### Parser & Data Model

* **Validation**: Ensures valid drone counts, unique start/end points, and link validity using Pydantic validation.
* **Graph Storage**: Hubs and links are held in adjacency structures for fast lookup.

### Pathfinding Strategy

The traditional **Dijkstra's algorithm** was modified to support custom graph rules:
- **Custom Cost Function:** Uses zone traversal costs instead of standard unit distances (1 turn for `normal` and `priority` zones, 2 turns for `restricted` zones, and infinite cost for `blocked` zones).
- **Tie-Breaking Preference:** When two paths have the same total turn cost, paths passing through `priority` zones are preferred.
- **Multi-Path Extraction:** Uses iterative pathfinding to identify alternative routes (`max_paths=2`).
- **Path Selection and Drone Distribution:** Calculates the total traversal cost and preference weight of each available path. Only paths with the lowest combined cost are selected. When multiple paths have the same cost, drones are distributed alternately between them to improve traffic distribution.

### Simulation Engine

- **Drone Management:** Initializes drones and assigns them to the selected paths.
- **Capacity Management:** Tracks zone occupancy (`max_drones`) and connection traversal limits (`max_link_capacity`).
- **Simultaneous Movement:** Processes drone movements turn by turn while respecting zone and connection capacity constraints.
- **Restricted Zone Handling:** A drone entering a restricted zone occupies the connection for two turns and must complete the transit on the following turn.
- **Movement Tracking:** Maintains each drone's current position and path progress throughout the simulation.
- **Deadlock Detection:** Detects situations where no drone can move and reports an error to prevent the simulation from continuing indefinitely.
- **Turn Output:** Stationary drones are omitted from the output, as required by the project specifications.

## Visual Representation

The output stream utilizes standard ANSI formatting (`visual.py`) to highlight zones and movement states:

* **Priority Zones**: Highlighted in blue tones.
* **Restricted Zones & Transits**: Highlighted in red tones.
* **Standard Zones**: Displayed using default color assignments or designated color metadata.
* Colors are only printed when the output goes to a terminal; redirected output stays plain text.

## Example Output

### Command

```bash
python3 main.py maps/easy/01_linear_path.txt
```

### Terminal Output

```text
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

## Resources

* [W3Schools Python Tutorial](https://www.w3schools.com/python/default.asp)
* [Python `heapq` Documentation](https://docs.python.org/3/library/heapq.html)
* [Dijkstra's Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
* [Pydantic Documentation](https://docs.pydantic.dev/)

### AI Usage Declaration

AI tools were used during development to:

* Assist in refining static typing checks (`mypy`).
* Verify graph edge-case scenarios and deadlock handling logic.
* Structure standardized documentation and code docstrings.