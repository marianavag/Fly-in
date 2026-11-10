from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


ZoneType = Literal["normal", "blocked", "restricted", "priority"]


class Drone(BaseModel):
    """Sets a default name for the drone after model initialisation."""
    drone_id: int
    current_zone_name: str
    path: list[str] = Field(default_factory=list)
    progress: int = 0
    in_transit_turns: int = 0


class Zone(BaseModel):
    """Represents a zone (hub) in the graph."""
    name: str
    x: int
    y: int
    zone_type: ZoneType = "normal"
    color: Optional[str] = None
    max_drones: int = Field(default=1, ge=1)
    current_drones: set[int] = Field(default_factory=set)

    @field_validator("color")
    @classmethod
    def normalize_color(cls, value: Optional[str]) -> Optional[str]:
        """Normalizes the color value."""
        if not value or value.lower() == "none":
            return None
        return value.lower()

    @property
    def is_full(self) -> bool:
        """Checks whether the zone is full."""
        return len(self.current_drones) >= self.max_drones


class Connection(BaseModel):
    """Represents a connection between two zones."""
    zone_a: str
    zone_b: str
    max_link_capacity: int = Field(default=1, ge=1)
    current_traversals: int = 0


class Graph(BaseModel):
    """Represents the complete network of zones and connections."""
    nb_drones: int = 0
    start_hub: Optional[str] = None
    end_hub: Optional[str] = None
    zones: dict[str, Zone] = Field(default_factory=dict)
    connections: list[Connection] = Field(default_factory=list)
    adjacency: dict[str, list[str]] = Field(default_factory=dict)

    def add_zone(self, zone: Zone) -> None:
        """Adds a new zone to the graph."""
        self.zones[zone.name] = zone
        if zone.name not in self.adjacency:
            self.adjacency[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        """Adds a two-way connection between two zones."""
        if connection.zone_a not in self.zones:
            raise ValueError(f"Zone '{connection.zone_a}' does not exist.")
        if connection.zone_b not in self.zones:
            raise ValueError(f"Zone '{connection.zone_b}' does not exist.")
        self.connections.append(connection)
        self.adjacency[connection.zone_a].append(connection.zone_b)
        self.adjacency[connection.zone_b].append(connection.zone_a)
