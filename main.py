import sys
from parser import Parser, ParseError
from pathfinder import PathNotFoundError
from simulator import SimulationEngine


class FlyIn:
    """Entry point: connects parser, pathfinder and simulator."""

    @classmethod
    def run(cls, argv: list[str]) -> int:
        """Runs the simulation until all drones reach the end_hub."""
        if len(argv) != 2:
            print("Usage: python main.py <map_file>", file=sys.stderr)
            return 1
        try:
            graph = Parser.parse_file(argv[1])
            engine = SimulationEngine(graph)
            history = engine.run()
        except (ParseError, PathNotFoundError, RuntimeError, OSError) as error:
            print(error, file=sys.stderr)
            return 1
        except Exception as error:
            print(f"ERROR: unexpected failure: {error}", file=sys.stderr)
            return 1
        for line in history:
            print(line)
        print(f"Total turns: {len(history)}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(FlyIn.run(sys.argv))
