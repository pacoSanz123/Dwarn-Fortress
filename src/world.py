"""
World module - Represents the 2D world map as a matrix of Cell objects.
"""

from typing import List, Tuple, Optional
from .cell import Cell, TerrainType


class World:
    """
    The world is a 2D grid of cells representing the game map.
    
    Attributes:
        width: Width of the world in cells
        height: Height of the world in cells
        grid: 2D matrix of Cell objects
        current_day: Current simulation day
        current_year: Current simulation year
    """
    
    DAYS_PER_YEAR = 365
    
    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self.grid: List[List[Cell]] = self._generate_world()
        self.current_day = 0
        self.current_year = 1
    
    def _generate_world(self) -> List[List[Cell]]:
        """Generate the world grid."""
        return [[Cell(x, y) for x in range(self.width)] for y in range(self.height)]
    
    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """Get a cell at specific coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
    
    def get_neighbors(self, x: int, y: int) -> List[Cell]:
        """Get all neighboring cells (8-directional)."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                cell = self.get_cell(x + dx, y + dy)
                if cell is not None:
                    neighbors.append(cell)
        return neighbors
    
    def get_passable_neighbors(self, x: int, y: int) -> List[Cell]:
        """Get neighboring cells that can be traversed."""
        return [cell for cell in self.get_neighbors(x, y) if cell.is_passable()]
    
    def get_season_modifier(self) -> int:
        """Get temperature modifier based on current day of year."""
        day_of_year = self.current_day % self.DAYS_PER_YEAR
        
        # Simple seasonal model: warmest in summer (day 182), coldest in winter (day 0/365)
        if day_of_year < 91:  # Winter -> Spring
            return -15 + (day_of_year // 6)
        elif day_of_year < 182:  # Spring -> Summer
            return (day_of_year - 91) // 6
        elif day_of_year < 273:  # Summer -> Autumn
            return 15 - ((day_of_year - 182) // 6)
        else:  # Autumn -> Winter
            return -((day_of_year - 273) // 6)
    
    def update_climate(self):
        """Update climate for all cells."""
        modifier = self.get_season_modifier()
        for row in self.grid:
            for cell in row:
                cell.update_climate(modifier)
    
    def update_resources(self):
        """Update/regenerate resources across the world."""
        # Food regenerates slower in harsh seasons
        season_modifier = self.get_season_modifier()
        regen_rate = 0.1 if season_modifier > -10 else 0.02
        
        for row in self.grid:
            for cell in row:
                cell.regenerate_food(regen_rate)
    
    def advance_day(self):
        """Advance the simulation by one day."""
        self.current_day += 1
        if self.current_day % self.DAYS_PER_YEAR == 0:
            self.current_year += 1
    
    def get_season_name(self) -> str:
        """Get current season name."""
        day_of_year = self.current_day % self.DAYS_PER_YEAR
        if day_of_year < 91:
            return "Winter"
        elif day_of_year < 182:
            return "Spring"
        elif day_of_year < 273:
            return "Summer"
        else:
            return "Autumn"
    
    def get_cells_by_owner(self, owner_name: str) -> List[Cell]:
        """Get all cells owned by a specific civilization."""
        cells = []
        for row in self.grid:
            for cell in row:
                if cell.owner == owner_name:
                    cells.append(cell)
        return cells
    
    def find_unowned_passable_cells(self) -> List[Cell]:
        """Find all unowned cells that can be claimed."""
        cells = []
        for row in self.grid:
            for cell in row:
                if cell.owner is None and cell.is_passable():
                    cells.append(cell)
        return cells
    
    def render_ascii(self, civilizations: dict = None) -> str:
        """Render the world as ASCII art."""
        lines = []
        lines.append(f"=== Year {self.current_year}, Day {self.current_day % self.DAYS_PER_YEAR + 1} ({self.get_season_name()}) ===")
        lines.append("+" + "-" * self.width + "+")
        
        # Create civilization markers
        civ_markers = {}
        if civilizations:
            for i, name in enumerate(civilizations.keys()):
                civ_markers[name] = str(i + 1)
        
        for row in self.grid:
            line = "|"
            for cell in row:
                if cell.owner and cell.owner in civ_markers:
                    line += civ_markers[cell.owner]
                else:
                    line += cell.get_ascii_repr()
            line += "|"
            lines.append(line)
        
        lines.append("+" + "-" * self.width + "+")
        lines.append("Legend: . Plains, T Forest, ^ Mountain, ~ Water, : Desert")
        if civilizations:
            for name, marker in civ_markers.items():
                lines.append(f"  {marker} = {name}'s territory")
        
        return "\n".join(lines)
    
    def __repr__(self):
        return f"World({self.width}x{self.height}, Year {self.current_year})"
