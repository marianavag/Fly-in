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
make fclean      # Run clean and also remove the .venv virtual environment
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
- **Custom Cost Function**: Replaces standard unit distances with turn delays (1 turn for `normal`/`priority`, 2 turns for `restricted`, and infinite cost for `blocked` zones).
- **Tie-Breaking Preference**: Prefers paths passing through `priority` zones when two routes have identical total turn costs.
- **Multi-Path Extraction**: Runs iterative pathfinding to find secondary paths (`max_paths=2`), distributing drone traffic across alternate routes to avoid bottleneck congestion.

### Simulation Engine

* Tracks capacity limits (`max_drones` and `max_link_capacity`).
* Allows dynamic vacating: a drone leaving a hub vacates space during the same turn, permitting entry to another drone.
* A drone travelling to a restricted zone occupies the connection for both turns.
* Deadlocks are avoided by design (paths do not share capacity 1 zones or links) and detected at runtime: a turn without any movement stops the program with a clear error.
* Omits stationary waiting drones from turn logs as per project evaluation requirements.

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