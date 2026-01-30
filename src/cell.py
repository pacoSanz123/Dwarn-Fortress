"""
Cell module - Represents a single tile in the world map.
Each cell has physical properties that affect civilization behavior.
"""

import random
from enum import Enum
from typing import Optional


class TerrainType(Enum):
    """Types of terrain in the world."""
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    WATER = "water"
    DESERT = "desert"


class MineralType(Enum):
    """Types of minerals that can be found in cells."""
    NONE = "none"
    IRON = "iron"
    GOLD = "gold"
    COPPER = "copper"
    STONE = "stone"


class Cell:
    """
    Represents a single cell/tile in the world map.
    
    Attributes:
        x: X coordinate in the world
        y: Y coordinate in the world
        altitude: Height level (0-100)
        temperature: Temperature in the cell (-50 to 50)
        terrain: Type of terrain
        mineral: Type of mineral resource
        food_resource: Amount of food available (replenishes over time)
        owner: Reference to civilization that controls this cell
    """
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.altitude = random.randint(0, 100)
        self.base_temperature = random.randint(-20, 40)
        self.temperature = self.base_temperature
        self.terrain = self._generate_terrain()
        self.mineral = self._generate_mineral()
        self.food_resource = self._initial_food()
        self.max_food = self.food_resource
        self.owner: Optional[str] = None  # Civilization name
    
    def _generate_terrain(self) -> TerrainType:
        """Generate terrain based on altitude."""
        if self.altitude > 80:
            return TerrainType.MOUNTAIN
        elif self.altitude < 10:
            return TerrainType.WATER
        elif self.base_temperature > 35:
            return TerrainType.DESERT
        elif random.random() < 0.3:
            return TerrainType.FOREST
        else:
            return TerrainType.PLAINS
    
    def _generate_mineral(self) -> MineralType:
        """Generate mineral resources based on terrain."""
        if self.terrain == TerrainType.MOUNTAIN:
            minerals = [MineralType.IRON, MineralType.GOLD, MineralType.COPPER, MineralType.STONE]
            return random.choice(minerals)
        elif self.terrain == TerrainType.PLAINS and random.random() < 0.1:
            return MineralType.STONE
        return MineralType.NONE
    
    def _initial_food(self) -> int:
        """Calculate initial food based on terrain type."""
        food_by_terrain = {
            TerrainType.PLAINS: random.randint(50, 100),
            TerrainType.FOREST: random.randint(80, 150),
            TerrainType.MOUNTAIN: random.randint(10, 30),
            TerrainType.WATER: random.randint(60, 120),  # Fish
            TerrainType.DESERT: random.randint(5, 20),
        }
        return food_by_terrain.get(self.terrain, 50)
    
    def is_passable(self) -> bool:
        """Check if civilizations can pass through this cell."""
        return self.terrain not in [TerrainType.WATER, TerrainType.MOUNTAIN]
    
    def update_climate(self, season_modifier: int):
        """Update temperature based on climate/season."""
        self.temperature = self.base_temperature + season_modifier
    
    def regenerate_food(self, rate: float = 0.1):
        """Regenerate food resources over time."""
        if self.terrain != TerrainType.WATER:
            growth = int(self.max_food * rate)
            self.food_resource = min(self.max_food, self.food_resource + growth)
    
    def harvest_food(self, amount: int) -> int:
        """Harvest food from the cell, returns actual amount harvested."""
        harvested = min(amount, self.food_resource)
        self.food_resource -= harvested
        return harvested
    
    def get_ascii_repr(self) -> str:
        """Return ASCII representation for visualization."""
        terrain_chars = {
            TerrainType.PLAINS: '.',
            TerrainType.FOREST: 'T',
            TerrainType.MOUNTAIN: '^',
            TerrainType.WATER: '~',
            TerrainType.DESERT: ':',
        }
        return terrain_chars.get(self.terrain, '?')
    
    def __repr__(self):
        return f"Cell({self.x}, {self.y}, {self.terrain.value})"
