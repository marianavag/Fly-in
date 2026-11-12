from typing import Optional
import sys


class TerminalVisual:
    """Manages colours and the visual representation of the temrinal."""
    RESET = "\033[0m"
    COLORS = {
        "black": "\033[30m",
        "green": "\033[32m",
        "red": "\033[31m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "purple": "\033[38;5;93m",
        "cyan": "\033[36m",
        "orange": "\033[38;5;208m",
        "brown": "\033[38;5;94m",
        "maroon": "\033[38;5;88m",
        "gold": "\033[38;5;220m",
        "darkred": "\033[38;5;52m",
        "violet": "\033[38;5;177m",
        "crimson": "\033[38;5;160m",
        "gray": "\033[90m",
        "magenta": "\033[35m",
        "lime": "\033[38;5;118m",
    }

    @classmethod
    def format_zone(cls, zone_name: str, zone_type: str,
                    color: Optional[str] = None) -> str:
        """Returns the zone name formated with the color."""
        if not sys.stdout.isatty():
            return zone_name
        if color and color in cls.COLORS:
            return f"{cls.COLORS[color]}{zone_name}{cls.RESET}"
        if zone_type == "priority":
            return f"{cls.COLORS['blue']}{zone_name}{cls.RESET}"
        elif zone_type == "restricted":
            return f"{cls.COLORS['red']}{zone_name}{cls.RESET}"
        return f"{cls.COLORS['yellow']}{zone_name}{cls.RESET}"
