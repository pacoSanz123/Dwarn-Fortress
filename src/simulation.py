"""
Simulation module - Main game loop and simulation engine.
Orchestrates the tick-based simulation of the world.
"""

import time
from typing import List, Optional

from .world import World
from .civilization import Civilization
from .chronicle import Chronicle
from .events import EventManager


class Simulation:
    """
    Main simulation engine that runs the tick-based game loop.
    
    Each tick represents one day in the simulation.
    Update order per tick:
    1. Climate update
    2. Resource regeneration  
    3. Civilization actions
    4. Random events
    5. Population changes
    
    Attributes:
        world: The game world
        civilizations: List of civilizations in the simulation
        chronicle: Event logging system
        event_manager: Random event handler
        ticks_per_year: Number of ticks that make up one year
    """
    
    def __init__(self, world_width: int = 20, world_height: int = 20, verbose: bool = True):
        self.world = World(world_width, world_height)
        self.civilizations: List[Civilization] = []
        self.chronicle = Chronicle(verbose=verbose)
        self.event_manager = EventManager()
        self.running = False
        self.verbose = verbose
    
    def add_civilization(self, name: str, start_x: int = None, start_y: int = None) -> Civilization:
        """
        Add a new civilization to the simulation.
        
        Args:
            name: Name of the civilization
            start_x: Starting X coordinate (random if not specified)
            start_y: Starting Y coordinate (random if not specified)
        
        Returns:
            The created Civilization object
        """
        import random
        
        # Find a valid starting position if not specified
        if start_x is None or start_y is None:
            attempts = 0
            while attempts < 100:
                x = random.randint(2, self.world.width - 3)
                y = random.randint(2, self.world.height - 3)
                cell = self.world.get_cell(x, y)
                
                if cell and cell.is_passable() and cell.owner is None:
                    # Check if far enough from other civilizations
                    too_close = False
                    for civ in self.civilizations:
                        cx, cy = civ.capital
                        distance = abs(x - cx) + abs(y - cy)
                        if distance < 6:  # Minimum distance
                            too_close = True
                            break
                    
                    if not too_close:
                        start_x, start_y = x, y
                        break
                
                attempts += 1
            
            if start_x is None:
                raise ValueError("Could not find valid starting position for civilization")
        
        civ = Civilization(name, start_x, start_y, self.world)
        self.civilizations.append(civ)
        
        self.chronicle.log_major_event(
            self.world.current_year,
            f"The civilization of {name} is founded at ({start_x}, {start_y})! "
            f"Population: {civ.population}, Trait: {civ.personality.value}"
        )
        
        return civ
    
    def get_nearby_civilizations(self, civ: Civilization) -> List[Civilization]:
        """Find civilizations that are nearby (territories adjacent)."""
        nearby = []
        
        for other in self.civilizations:
            if other.name == civ.name or not other.is_alive:
                continue
            
            # Check if territories are adjacent
            for x, y in civ.territory:
                neighbors = self.world.get_neighbors(x, y)
                for neighbor in neighbors:
                    if neighbor.owner == other.name:
                        if other not in nearby:
                            nearby.append(other)
                        break
        
        return nearby
    
    def tick(self):
        """
        Execute one simulation tick (one day).
        Update order: Climate -> Resources -> Civilizations -> Events
        """
        # 1. Update climate
        self.world.update_climate()
        
        # 2. Update resources
        self.world.update_resources()
        
        # 3. Civilization actions
        for civ in self.civilizations:
            if not civ.is_alive:
                continue
            
            # Find nearby civilizations
            nearby = self.get_nearby_civilizations(civ)
            
            # Update state machine
            civ.update_state(nearby)
            
            # Execute action (result not currently used but available for future logging)
            civ.execute_action(nearby, self.chronicle)
        
        # 4. Random events
        self.event_manager.process_events(self.world, self.civilizations, self.chronicle)
        
        # 5. Population changes
        for civ in self.civilizations:
            civ.process_population_changes(self.chronicle)
        
        # Advance time
        self.world.advance_day()
    
    def run(self, days: int = 3650, display_interval: int = 365, delay: float = 0):
        """
        Run the simulation for a specified number of days.
        
        Args:
            days: Number of days (ticks) to simulate
            display_interval: How often to display status (in days)
            delay: Time delay between ticks (for visualization)
        """
        self.running = True
        
        if self.verbose:
            print("\n" + "=" * 60)
            print("       DWARF FORTRESS - CIVILIZATION SIMULATOR")
            print("=" * 60)
            print(f"Simulating {days} days ({days // 365} years)")
            print(f"World size: {self.world.width}x{self.world.height}")
            print(f"Civilizations: {len(self.civilizations)}")
            print("=" * 60 + "\n")
        
        start_tick = self.world.current_day
        
        for day in range(days):
            if not self.running:
                break
            
            self.tick()
            
            # Check if all civilizations are dead
            living_civs = [c for c in self.civilizations if c.is_alive]
            if not living_civs:
                self.chronicle.log_major_event(
                    self.world.current_year,
                    "All civilizations have perished. The world falls silent."
                )
                break
            
            # Display status periodically
            if (self.world.current_day - start_tick) % display_interval == 0:
                self.display_status()
            
            if delay > 0:
                time.sleep(delay)
        
        self.running = False
        
        if self.verbose:
            self.display_final_status()
    
    def display_status(self):
        """Display current simulation status."""
        print("\n" + "-" * 60)
        
        # Display world map
        civ_dict = {c.name: c for c in self.civilizations}
        print(self.world.render_ascii(civ_dict))
        
        # Display civilization stats
        print("\nCivilization Status:")
        for civ in self.civilizations:
            print(f"  {civ.get_status_string()}")
        
        print("-" * 60)
    
    def display_final_status(self):
        """Display final simulation results."""
        print("\n" + "=" * 60)
        print("              SIMULATION COMPLETE")
        print("=" * 60)
        
        # Final map
        civ_dict = {c.name: c for c in self.civilizations}
        print(self.world.render_ascii(civ_dict))
        
        # Final stats
        print("\nFinal Civilization Status:")
        for civ in self.civilizations:
            print(f"  {civ.get_status_string()}")
        
        # Determine winner
        living_civs = [c for c in self.civilizations if c.is_alive]
        if len(living_civs) == 1:
            winner = living_civs[0]
            print(f"\n*** {winner.name} is the sole surviving civilization! ***")
        elif len(living_civs) > 1:
            # Winner by territory
            winner = max(living_civs, key=lambda c: len(c.territory))
            print(f"\n*** {winner.name} dominates with {len(winner.territory)} territories! ***")
        else:
            print("\n*** No civilizations survived. The world is empty. ***")
        
        # Print chronicle summary
        self.chronicle.print_summary()
    
    def stop(self):
        """Stop the simulation."""
        self.running = False
