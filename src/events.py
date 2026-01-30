"""
Events module - Random event system for the simulation.
Adds unpredictability and drama to the world.
"""

import random
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .world import World
    from .civilization import Civilization
    from .chronicle import Chronicle


class RandomEvent:
    """Base class for random events."""
    
    def __init__(self, name: str, probability: float):
        self.name = name
        self.probability = probability  # Chance per tick (0-1)
    
    def should_trigger(self) -> bool:
        """Check if the event should trigger this tick."""
        return random.random() < self.probability
    
    def execute(self, world: 'World', civilizations: list, chronicle: 'Chronicle') -> str:
        """Execute the event. Override in subclasses."""
        raise NotImplementedError


class DroughtEvent(RandomEvent):
    """A drought reduces food production in affected areas."""
    
    def __init__(self):
        super().__init__("Drought", 0.001)  # ~1 per 3 years
    
    def execute(self, world: 'World', civilizations: list, chronicle: 'Chronicle') -> str:
        # Reduce food in random area
        center_x = random.randint(0, world.width - 1)
        center_y = random.randint(0, world.height - 1)
        
        affected_cells = 0
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                cell = world.get_cell(center_x + dx, center_y + dy)
                if cell:
                    cell.food_resource = max(0, cell.food_resource - 30)
                    affected_cells += 1
        
        chronicle.log_event(
            world.current_year,
            f"A terrible drought strikes the region around ({center_x}, {center_y})!"
        )
        return f"Drought affected {affected_cells} cells"


class BountifulHarvestEvent(RandomEvent):
    """A bountiful harvest increases food in affected areas."""
    
    def __init__(self):
        super().__init__("Bountiful Harvest", 0.002)
    
    def execute(self, world: 'World', civilizations: list, chronicle: 'Chronicle') -> str:
        center_x = random.randint(0, world.width - 1)
        center_y = random.randint(0, world.height - 1)
        
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                cell = world.get_cell(center_x + dx, center_y + dy)
                if cell:
                    cell.food_resource = min(cell.max_food * 2, cell.food_resource + 50)
        
        chronicle.log_event(
            world.current_year,
            f"The lands around ({center_x}, {center_y}) enjoy a bountiful harvest!"
        )
        return "Bountiful harvest occurred"


class PlagueEvent(RandomEvent):
    """A plague affects a civilization's population."""
    
    def __init__(self):
        super().__init__("Plague", 0.0005)  # Rare
    
    def execute(self, world: 'World', civilizations: list, chronicle: 'Chronicle') -> str:
        living_civs = [c for c in civilizations if c.is_alive]
        if not living_civs:
            return "No civilizations to affect"
        
        target = random.choice(living_civs)
        deaths = int(target.population * random.uniform(0.1, 0.3))
        target.population = max(10, target.population - deaths)
        target.morale = max(0, target.morale - 20)
        
        chronicle.log_major_event(
            world.current_year,
            f"A plague devastates {target.name}, killing {deaths} people!"
        )
        return f"Plague killed {deaths} in {target.name}"


class TechnologicalDiscoveryEvent(RandomEvent):
    """A civilization makes a technological breakthrough."""
    
    def __init__(self):
        super().__init__("Technological Discovery", 0.001)
    
    def execute(self, world: 'World', civilizations: list, chronicle: 'Chronicle') -> str:
        living_civs = [c for c in civilizations if c.is_alive]
        if not living_civs:
            return "No civilizations to affect"
        
        # Higher tech civs have slightly better chances
        target = random.choice(living_civs)
        target.tech_level += 1
        target.morale = min(100, target.morale + 10)
        
        discoveries = [
            "improved farming techniques",
            "better hunting tools",
            "advanced construction methods",
            "new preservation methods",
            "improved irrigation",
        ]
        
        discovery = random.choice(discoveries)
        chronicle.log_event(
            world.current_year,
            f"{target.name} discovers {discovery}! (Tech Level: {target.tech_level})"
        )
        return f"{target.name} reached tech level {target.tech_level}"


class MoraleCrisisEvent(RandomEvent):
    """A morale crisis affects a civilization."""
    
    def __init__(self):
        super().__init__("Morale Crisis", 0.0003)  # Rarer morale crises
    
    def execute(self, world: 'World', civilizations: list, chronicle: 'Chronicle') -> str:
        living_civs = [c for c in civilizations if c.is_alive]
        if not living_civs:
            return "No civilizations to affect"
        
        target = random.choice(living_civs)
        morale_loss = random.randint(5, 15)  # Less severe morale loss
        target.morale = max(0, target.morale - morale_loss)
        
        crises = [
            "religious schism",
            "political scandal",
            "failed harvest celebration",
            "disputed succession",
        ]
        
        crisis = random.choice(crises)
        chronicle.log_event(
            world.current_year,
            f"A {crisis} causes unrest in {target.name}. Morale drops by {morale_loss}."
        )
        return f"Morale crisis in {target.name}"


class EventManager:
    """Manages all random events in the simulation."""
    
    def __init__(self):
        self.events = [
            DroughtEvent(),
            BountifulHarvestEvent(),
            PlagueEvent(),
            TechnologicalDiscoveryEvent(),
            MoraleCrisisEvent(),
        ]
    
    def process_events(self, world: 'World', civilizations: list, chronicle: 'Chronicle'):
        """Process all possible random events for this tick."""
        for event in self.events:
            if event.should_trigger():
                event.execute(world, civilizations, chronicle)
