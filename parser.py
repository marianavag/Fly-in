from models import Graph, Zone, Connection
from typing import Literal


class ParseError(Exception):
    """Exception to indicate the line and reason of the error."""
    def __init__(self, line_num: int, message: str) -> None:
        """Initiates the exception with the line number and message."""
        self.line_num = line_num
        self.message = message
        super().__init__(f"ERROR: line {line_num}: {message}")


class Parser:
    """Reads, validates and converts the map files into an object Graph."""
    @classmethod
    def _parse_nb_drones(cls, line: str, line_num: int, graph: Graph) -> None:
        """Processes the initial line 'nb_drones: <positive_intenger>'."""
        if ":" not in line:
            raise ParseError(line_num, "Invalid nb_drones syntax.")
        prefix, value = line.split(":", 1)
        if prefix.strip() != "nb_drones":
            raise ParseError(line_num,
                             "Invalid prefix. Expected 'nb_drones'.")
        try:
            nb_drones = int(value.strip())
        except ValueError:
            raise ParseError(line_num,
                             "nb_drones must be a positive intenger.")
        if nb_drones <= 0:
            raise ParseError(line_num, "nb_drones must be greater than 0.")
        graph.nb_drones = nb_drones

    @classmethod
    def _parse_metadata(cls, text: str, line_num: int) -> dict[str, str]:
        """Processes any metadata block between [...]."""
        if text.count("[") != 1 or text.count("]") != 1:
            raise ParseError(line_num, "Invalid metadata brackets.")
        open_index = text.index("[")
        close_index = text.index("]")
        if close_index < open_index:
            raise ParseError(line_num, "Invalid metadata brackets.")
        if text[close_index + 1:].strip():
            raise ParseError(line_num, "Unexpected text after metadata.")
        clean_metadata = text[open_index + 1:close_index].strip()
        if not clean_metadata:
            return {}
        metadata_dict: dict[str, str] = {}
        for data in clean_metadata.split():
            if "=" not in data:
                raise ParseError(
                    line_num,
                    "Invalid metadata syntax. Expected 'key=value'.")
            data_key, data_value = data.split("=", 1)
            data_key = data_key.strip()
            data_value = data_value.strip()
            if not data_key or not data_value:
                raise ParseError(
                    line_num,
                    "Metadata key and value cannot be empty.")
            if data_key in metadata_dict:
                raise ParseError(
                    line_num,
                    f"Duplicate metadata key '{data_key}'.")
            metadata_dict[data_key] = data_value
        return metadata_dict

    @classmethod
    def _parse_hub(cls, line: str, line_num: int, graph: Graph) -> None:
        """Processes the zone/hub(start_hub, end_hub and hub)."""
        if ":" not in line:
            raise ParseError(line_num, "Invalid zone/hub syntax. Expected ':'")
        if "[" in line or "]" in line:
            hub_info = line.split("[", 1)[0].strip()
            metadata = cls._parse_metadata(line, line_num)
        else:
            hub_info = line
            metadata = {}
        valid_keys = {"zone", "color", "max_drones"}
        for key in metadata:
            if key not in valid_keys:
                raise ParseError(line_num, f"Unknown metadata '{key}'")
        hub_type, values = hub_info.split(":", 1)
        hub_type = hub_type.strip()
        if hub_type not in {"hub", "start_hub", "end_hub"}:
            raise ParseError(line_num, f"Invalid hub type '{hub_type}'.")
        parts = values.split()
        if len(parts) != 3:
            raise ParseError(line_num,
                             "Invalid number of elements for zone/hub.")
        name = parts[0]
        if "-" in name:
            raise ParseError(line_num, "Zone names cannot contain dashes.")
        if name in graph.zones:
            raise ParseError(line_num,
                             f"{name} already exists.")
        try:
            x, y = int(parts[1]), int(parts[2])
        except ValueError:
            raise ParseError(line_num, "Zone coordinates must be integers.")
        zone_type_raw = metadata.get("zone", "normal")
        zone_type: Literal["normal", "blocked", "restricted", "priority"]
        if zone_type_raw == "normal":
            zone_type = "normal"
        elif zone_type_raw == "blocked":
            zone_type = "blocked"
        elif zone_type_raw == "restricted":
            zone_type = "restricted"
        elif zone_type_raw == "priority":
            zone_type = "priority"
        else:
            raise ParseError(line_num, f"Invalid zone type: '{zone_type_raw}'")
        max_drones = 1
        if hub_type == "hub":
            try:
                max_drones = int(metadata.get("max_drones", 1))
            except ValueError:
                raise ParseError(line_num,
                                 "max_drones value must be an integer.")
            if max_drones <= 0:
                raise ParseError(line_num,
                                 "max_drones must be greater than 0.")
        zone = Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=metadata.get("color"),
            max_drones=max_drones
        )
        if hub_type == "start_hub":
            if graph.start_hub is not None:
                raise ParseError(line_num, "Only one start_hub is allowed.")
            graph.start_hub = zone.name
        elif hub_type == "end_hub":
            if graph.end_hub is not None:
                raise ParseError(line_num, "Only one end_hub is allowed.")
            graph.end_hub = zone.name
        graph.add_zone(zone)

    @classmethod
    def _parse_connection(cls, line: str, line_num: int, graph: Graph) -> None:
        """Processes the connections between zones/hubs."""
        if ":" not in line:
            raise ParseError(line_num, "Invalid connection syntax.")
        if "[" in line or "]" in line:
            connect_info = line.split("[", 1)[0].strip()
            metadata = cls._parse_metadata(line, line_num)
        else:
            connect_info = line
            metadata = {}
        valid_keys = {"max_link_capacity"}
        for key in metadata:
            if key not in valid_keys:
                raise ParseError(line_num, f"Unknown metadata '{key}'")
        prefix, values = connect_info.split(":", 1)
        if prefix.strip() != "connection":
            raise ParseError(line_num, "Invalid prefix. "
                             "Expected 'connection'.")
        connect_zones = values.strip()
        if "-" not in connect_zones:
            raise ParseError(line_num, "Invalid syntax. "
                             "Expected 'zoneA-zoneB'.")
        parts = connect_zones.split("-", 1)
        zone_a, zone_b = parts[0].strip(), parts[1].strip()
        if not zone_a or not zone_b:
            raise ParseError(line_num,
                             "Both zones must be specified in the connection.")
        if zone_a == zone_b:
            raise ParseError(line_num,
                             f"Zone '{zone_a}' cannot connect to itself.")
        if zone_a not in graph.zones:
            raise ParseError(line_num, f"{zone_a} not part of zones/hubs.")
        if zone_b not in graph.zones:
            raise ParseError(line_num, f"{zone_b} not part of zones/hubs.")
        for existing_connection in graph.connections:
            if (
                (existing_connection.zone_a == zone_a and
                 existing_connection.zone_b == zone_b)
                or (existing_connection.zone_a == zone_b and
                    existing_connection.zone_b == zone_a)
            ):
                raise ParseError(line_num, f"Connection between {zone_a} "
                                 f"and {zone_b} already exists.")
        try:
            max_link_capacity = int(metadata.get("max_link_capacity", 1))
        except ValueError:
            raise ParseError(line_num,
                             "max_link_capacity must be an integer.")
        if max_link_capacity <= 0:
            raise ParseError(line_num,
                             "max_link_capacity must be greater than 0.")
        connection = Connection(
            zone_a=zone_a,
            zone_b=zone_b,
            max_link_capacity=max_link_capacity
        )
        graph.add_connection(connection)

    @classmethod
    def parse_file(cls, filepath: str) -> Graph:
        """Parses and verifies the complete map file."""
        graph = Graph()
        has_nb_drones = False
        connections_to_parse = []
        with open(filepath, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, start=1):
                clean_line = line.split("#")[0].strip()
                if not clean_line:
                    continue
                if clean_line.startswith("nb_drones:"):
                    if has_nb_drones:
                        raise ParseError(line_num, "Duplicate 'nb_drones'")
                    cls._parse_nb_drones(clean_line, line_num, graph)
                    has_nb_drones = True
                elif not has_nb_drones:
                    raise ParseError(line_num,
                                     "The first line must be 'nb_drones:'")
                elif clean_line.startswith("connection:"):
                    connections_to_parse.append((clean_line, line_num))
                elif ":" in clean_line:
                    cls._parse_hub(clean_line, line_num, graph)
                else:
                    raise ParseError(
                        line_num,
                        f"Invalid syntax: '{clean_line}'"
                    )
            if not has_nb_drones:
                raise ParseError(0, "Missing 'nb_drones' declaration.")
            if graph.start_hub is None:
                raise ParseError(0, "Missing 'start_hub' zone.")
            if graph.end_hub is None:
                raise ParseError(0, "Missing 'end_hub' zone.")
            for connection, line_num in connections_to_parse:
                cls._parse_connection(connection, line_num, graph)
        return graph
