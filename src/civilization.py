"""
Civilization module - Represents an autonomous civilization with FSM decision-making.
"""

import random
from enum import Enum
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World
    from .cell import Cell


class CivilizationState(Enum):
    """States for the Finite State Machine."""
    IDLE = "idle"
    HUNTING = "hunting"
    GATHERING = "gathering"
    EXPANDING = "expanding"
    DIPLOMACY = "diplomacy"
    DEFENDING = "defending"
    COLLAPSED = "collapsed"


class PersonalityTrait(Enum):
    """Personality traits that affect diplomatic decisions."""
    AGGRESSIVE = "aggressive"
    PEACEFUL = "peaceful"
    ISOLATIONIST = "isolationist"
    EXPANSIONIST = "expansionist"
    TRADING = "trading"


class Civilization:
    """
    Represents an autonomous civilization in the simulation.
    
    Attributes:
        name: Name of the civilization
        population: Number of inhabitants
        food: Current food stockpile
        morale: Overall happiness (0-100)
        tech_level: Technological advancement level
        state: Current FSM state
        personality: Diplomatic personality trait
        territory: List of controlled cell coordinates
        capital: Main settlement coordinates
    """
    
    # Thresholds for state transitions
    FOOD_STARVING = 20
    FOOD_LOW = 50
    FOOD_EXCESS = 150
    MORALE_CRITICAL = 10  # Very low threshold - only collapse when morale is dangerously low
    POPULATION_MIN = 10
    
    def __init__(self, name: str, start_x: int, start_y: int, world: 'World'):
        self.name = name
        self.world = world
        self.population = random.randint(30, 60)  # Start smaller for sustainability
        self.food = 200  # More starting food
        self.morale = random.randint(70, 90)  # Start with better morale
        self.tech_level = 1
        self.state = CivilizationState.IDLE
        self.personality = random.choice(list(PersonalityTrait))
        self.capital = (start_x, start_y)
        self.territory: List[tuple] = []
        self.relations: dict = {}  # Relations with other civilizations
        self.is_alive = True
        self.death_cause: Optional[str] = None
        
        # Claim starting territory
        self._claim_starting_territory(start_x, start_y)
    
    def _claim_starting_territory(self, x: int, y: int):
        """Claim initial territory around the capital."""
        # Claim 3x3 area around starting position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                cell = self.world.get_cell(x + dx, y + dy)
                if cell and cell.is_passable() and cell.owner is None:
                    cell.owner = self.name
                    self.territory.append((cell.x, cell.y))
    
    def get_food_per_capita(self) -> float:
        """Calculate food per person."""
        if self.population == 0:
            return 0
        return self.food / self.population
    
    def update_state(self, nearby_civilizations: List['Civilization']):
        """
        Finite State Machine - Update civilization state based on conditions.
        Priority: Survival > Diplomacy > Expansion
        """
        if not self.is_alive:
            return
        
        food_per_capita = self.get_food_per_capita()
        
        # Priority 1: Critical survival - Food shortage
        if food_per_capita < self.FOOD_STARVING:
            self.state = CivilizationState.HUNTING
            return
        
        if food_per_capita < self.FOOD_LOW:
            self.state = CivilizationState.GATHERING
            return
        
        # Priority 2: Diplomatic encounters
        if nearby_civilizations and self.state != CivilizationState.DIPLOMACY:
            for other in nearby_civilizations:
                if other.name not in self.relations:
                    self.state = CivilizationState.DIPLOMACY
                    return
        
        # Priority 3: Expansion when resources are abundant
        if food_per_capita > self.FOOD_EXCESS and len(self.territory) < 30:
            if self.personality in [PersonalityTrait.EXPANSIONIST, PersonalityTrait.AGGRESSIVE]:
                self.state = CivilizationState.EXPANDING
                return
            elif random.random() < 0.3:  # Other personalities expand less often
                self.state = CivilizationState.EXPANDING
                return
        
        # Default: Idle state (maintenance)
        self.state = CivilizationState.IDLE
    
    def execute_action(self, nearby_civilizations: List['Civilization'], chronicle) -> str:
        """Execute action based on current state. Returns action description."""
        if not self.is_alive:
            return ""
        
        actions = {
            CivilizationState.IDLE: self._action_idle,
            CivilizationState.HUNTING: self._action_hunt,
            CivilizationState.GATHERING: self._action_gather,
            CivilizationState.EXPANDING: self._action_expand,
            CivilizationState.DIPLOMACY: lambda: self._action_diplomacy(nearby_civilizations, chronicle),
            CivilizationState.DEFENDING: self._action_defend,
        }
        
        action_func = actions.get(self.state, self._action_idle)
        return action_func()
    
    def _action_idle(self) -> str:
        """Idle state - basic maintenance and passive food consumption."""
        # Consume food
        food_consumed = max(1, self.population // 20)  # Reduced consumption
        self.food = max(0, self.food - food_consumed)
        
        # Morale recovery when idle and food is OK
        if self.food > self.FOOD_LOW:
            self.morale = min(100, self.morale + 2)
        else:
            self.morale = min(100, self.morale + 1)
        
        return f"{self.name} rests and tends to daily affairs."
    
    def _action_hunt(self) -> str:
        """Hunting state - actively search for food (more aggressive)."""
        total_harvested = 0
        
        for x, y in self.territory:
            cell = self.world.get_cell(x, y)
            if cell:
                harvested = cell.harvest_food(20)  # Aggressive harvesting
                total_harvested += harvested
        
        # Food consumption is lower than normal (efficient hunters)
        food_consumed = max(1, self.population // 30)
        self.food = max(0, self.food + total_harvested - food_consumed)
        
        # Hunting provides food which improves morale slightly
        if total_harvested > 0:
            self.morale = min(100, self.morale + 1)
        
        return f"{self.name} hunts desperately, gathering {total_harvested} food."
    
    def _action_gather(self) -> str:
        """Gathering state - moderate food collection."""
        total_harvested = 0
        
        for x, y in self.territory:
            cell = self.world.get_cell(x, y)
            if cell:
                harvested = cell.harvest_food(12)  # Moderate harvesting
                total_harvested += harvested
        
        # Food consumption
        food_consumed = max(1, self.population // 25)
        self.food = max(0, self.food + total_harvested - food_consumed)
        
        # Gathering is productive, slight morale recovery
        if total_harvested > 0:
            self.morale = min(100, self.morale + 1)
        
        return f"{self.name} gathers resources, collecting {total_harvested} food."
    
    def _action_expand(self) -> str:
        """Expanding state - claim new territory."""
        expanded = False
        
        # Find adjacent unclaimed cells
        for x, y in self.territory.copy():
            neighbors = self.world.get_passable_neighbors(x, y)
            for cell in neighbors:
                if cell.owner is None:
                    cell.owner = self.name
                    self.territory.append((cell.x, cell.y))
                    expanded = True
                    
                    # Expansion costs resources
                    self.food -= 10
                    
                    return f"{self.name} expands territory to ({cell.x}, {cell.y})!"
        
        if not expanded:
            return f"{self.name} cannot find room to expand."
        
        return ""
    
    def _action_diplomacy(self, nearby_civilizations: List['Civilization'], chronicle) -> str:
        """Diplomacy state - evaluate relations with other civilizations."""
        for other in nearby_civilizations:
            if other.name in self.relations:
                continue
            
            # Determine relationship based on personality traits
            relation_score = self._calculate_initial_relations(other)
            self.relations[other.name] = relation_score
            other.relations[self.name] = relation_score
            
            if relation_score > 50:
                chronicle.log_event(
                    self.world.current_year,
                    f"{self.name} and {other.name} establish friendly relations!"
                )
                return f"{self.name} befriends {other.name}."
            elif relation_score < 20:
                chronicle.log_event(
                    self.world.current_year,
                    f"Tensions rise between {self.name} and {other.name}!"
                )
                return f"{self.name} views {other.name} with hostility."
            else:
                return f"{self.name} maintains neutral relations with {other.name}."
        
        self.state = CivilizationState.IDLE
        return ""
    
    def _calculate_initial_relations(self, other: 'Civilization') -> int:
        """Calculate initial diplomatic relations based on personalities."""
        base_score = 50
        
        # Personality compatibility
        compatibility = {
            (PersonalityTrait.PEACEFUL, PersonalityTrait.PEACEFUL): 30,
            (PersonalityTrait.PEACEFUL, PersonalityTrait.TRADING): 25,
            (PersonalityTrait.TRADING, PersonalityTrait.TRADING): 20,
            (PersonalityTrait.AGGRESSIVE, PersonalityTrait.AGGRESSIVE): -30,
            (PersonalityTrait.AGGRESSIVE, PersonalityTrait.PEACEFUL): -10,
            (PersonalityTrait.EXPANSIONIST, PersonalityTrait.EXPANSIONIST): -20,
            (PersonalityTrait.ISOLATIONIST, PersonalityTrait.ISOLATIONIST): 10,
        }
        
        pair = (self.personality, other.personality)
        reverse_pair = (other.personality, self.personality)
        
        modifier = compatibility.get(pair, compatibility.get(reverse_pair, 0))
        base_score += modifier
        
        # Random factor
        base_score += random.randint(-15, 15)
        
        return max(0, min(100, base_score))
    
    def _action_defend(self) -> str:
        """Defensive state - protect territory."""
        self.morale = max(0, self.morale - 2)
        return f"{self.name} fortifies defenses."
    
    def process_population_changes(self, chronicle):
        """Process births, deaths, and population effects."""
        if not self.is_alive:
            return
        
        food_per_capita = self.get_food_per_capita()
        
        # Starvation deaths - only when food per capita is very low
        if food_per_capita < 0.3:
            deaths = int(self.population * 0.02)  # 2% die from starvation
            self.population = max(0, self.population - deaths)
            self.morale = max(0, self.morale - 3)  # Reduced morale impact
            if deaths > 0:
                chronicle.log_event(
                    self.world.current_year,
                    f"{deaths} of {self.name}'s people starve to death."
                )
        
        # Natural births (when conditions are good)
        elif food_per_capita > 2.0 and self.morale > 50:
            births = int(self.population * 0.01)  # 1% birth rate per day
            self.population += max(1, births)
        
        # Natural deaths (very low rate)
        if random.random() < 0.1:  # Only 10% chance per day
            natural_deaths = max(0, int(self.population * 0.002))  # 0.2% natural death rate
            self.population = max(0, self.population - natural_deaths)
        
        # Check for collapse - population too low
        if self.population < self.POPULATION_MIN:
            self.is_alive = False
            self.state = CivilizationState.COLLAPSED
            self.death_cause = "population collapse"
            chronicle.log_major_event(
                self.world.current_year,
                f"The civilization of {self.name} has COLLAPSED due to {self.death_cause}!"
            )
            return
        
        # Civil unrest collapse only triggers after morale stays critically low for a while
        if self.morale < self.MORALE_CRITICAL and self.is_alive:
            # Very low chance of collapse - only 0.5% per day when morale is critical
            if random.random() < 0.005:
                self.is_alive = False
                self.state = CivilizationState.COLLAPSED
                self.death_cause = "civil unrest"
                chronicle.log_major_event(
                    self.world.current_year,
                    f"The civilization of {self.name} has COLLAPSED due to {self.death_cause}!"
                )
    
    def get_status_string(self) -> str:
        """Get a status summary string."""
        if not self.is_alive:
            return f"{self.name} [COLLAPSED - {self.death_cause}]"
        
        return (
            f"{self.name} | Pop: {self.population} | Food: {self.food} | "
            f"Morale: {self.morale}% | Tech: {self.tech_level} | "
            f"Territory: {len(self.territory)} | State: {self.state.value} | "
            f"Trait: {self.personality.value}"
        )
    
    def __repr__(self):
        return f"Civilization({self.name}, pop={self.population}, alive={self.is_alive})"
