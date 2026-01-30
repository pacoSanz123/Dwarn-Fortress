#!/usr/bin/env python3
"""
Dwarf Fortress - A Dwarf Fortress-inspired Civilization Simulator

This is the main entry point for the simulation.
Run this file to start a simulation with two competing civilizations.

Usage:
    python main.py [--years N] [--quiet] [--seed N]
"""

import argparse
import random
import sys

from src.simulation import Simulation


def create_civilization_names():
    """Generate random civilization names."""
    prefixes = ["The", "Clan", "House", "Kingdom of", "Tribe of", "Order of"]
    cultures = ["Elves", "Dwarves", "Humans", "Orcs", "Goblins", "Gnomes"]
    suffixes = ["of the North", "of the Mountains", "of the Plains", "of the Forest", "the Brave", "the Wise"]
    
    names = []
    used_cultures = set()
    
    for _ in range(2):
        culture = random.choice([c for c in cultures if c not in used_cultures])
        used_cultures.add(culture)
        
        if random.random() < 0.5:
            name = f"{random.choice(prefixes)} {culture}"
        else:
            name = f"{culture} {random.choice(suffixes)}"
        names.append(name)
    
    return names


def main():
    """Main entry point for the simulation."""
    parser = argparse.ArgumentParser(
        description="Dwarf Fortress - Civilization Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                  # Run with defaults (10 years)
    python main.py --years 50       # Simulate 50 years
    python main.py --seed 42        # Use specific random seed
    python main.py --quiet          # Minimal output
        """
    )
    
    parser.add_argument(
        "--years", "-y",
        type=int,
        default=10,
        help="Number of years to simulate (default: 10)"
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducible simulations"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity"
    )
    
    parser.add_argument(
        "--map-size", "-m",
        type=int,
        default=20,
        help="Size of the world map (default: 20x20)"
    )
    
    args = parser.parse_args()
    
    # Set random seed if specified
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    # Create simulation
    sim = Simulation(
        world_width=args.map_size,
        world_height=args.map_size,
        verbose=not args.quiet
    )
    
    # Generate civilization names
    civ_names = create_civilization_names()
    
    # Add civilizations
    for name in civ_names:
        sim.add_civilization(name)
    
    # Run simulation
    days = args.years * 365
    display_interval = 365  # Show status every year
    
    try:
        sim.run(days=days, display_interval=display_interval)
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        sim.stop()
        sim.display_final_status()
        sys.exit(0)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
