# Dwarf Fortress

A Dwarf Fortress-inspired civilization simulator in Observer Mode. Watch autonomous civilizations compete for resources, expand territory, and experience emergent narratives.

## Features

- **Tick-Based Simulation Engine**: Each tick represents one day. Update order: Climate → Resources → Civilization Actions → Random Events → Population Changes
- **Autonomous Civilizations**: Civilizations make decisions using a Finite State Machine (FSM):
  - **Hunting**: When food per capita is critically low
  - **Gathering**: When food is low but not critical
  - **Expanding**: When resources are abundant and territory is available
  - **Diplomacy**: When encountering other civilizations
- **2D World Map**: 20x20 grid of cells with:
  - Terrain types (Plains, Forest, Mountain, Water, Desert)
  - Physical properties (altitude, temperature)
  - Mineral resources (Iron, Gold, Copper, Stone)
  - Food resources that regenerate over time
- **Random Events**: Droughts, bountiful harvests, plagues, technological discoveries, morale crises
- **Chronicle System**: Logs important events for emergent storytelling

## Installation

Requires Python 3.7+

```bash
# Clone the repository
git clone https://github.com/pacoSanz123/Dwarn-Fortress.git
cd Dwarn-Fortress

# Run the simulation
python main.py
```

## Usage

```bash
# Run with defaults (10 years simulation)
python main.py

# Run for 50 years
python main.py --years 50

# Use a specific random seed for reproducible simulations
python main.py --seed 42

# Minimal output mode
python main.py --quiet

# Custom map size
python main.py --map-size 30
```

## ASCII Map Legend

```
. Plains  - High food production
T Forest  - Very high food production
^ Mountain - Low food, has minerals
~ Water   - Fish (food), impassable
: Desert  - Very low food

1, 2, etc. - Civilization territories
```

## Civilization Traits

Each civilization is randomly assigned a personality trait that affects behavior:
- **Aggressive**: More likely to expand territory
- **Peaceful**: Builds better diplomatic relations
- **Expansionist**: Prioritizes territory growth
- **Isolationist**: Less likely to interact with others
- **Trading**: Good at building relations and resource management

## Project Structure

```
Dwarn-Fortress/
├── main.py              # Entry point
├── src/
│   ├── __init__.py
│   ├── cell.py          # Cell class for map tiles
│   ├── world.py         # World class (2D map)
│   ├── civilization.py  # Civilization class with FSM
│   ├── chronicle.py     # Event logging system
│   ├── events.py        # Random event system
│   └── simulation.py    # Main simulation engine
└── README.md
```

## Example Output

```
=== Year 10, Day 1 (Winter) ===
+--------------------+
|^^...~T~TTT^~:..^..:|
|.T:^.:~~...TT^.^T~~^|
|..~T.^.~TTT.T^T.T^~.|
|~^..T^.~^^~^.^^11^.T|
|...^^.........111..^|
|T^^.T...^T~.^.^1^..^|
...
+--------------------+
Legend: . Plains, T Forest, ^ Mountain, ~ Water, : Desert
  1 = Order of Humans's territory
  2 = Order of Dwarves's territory

*** Order of Humans is the sole surviving civilization! ***
```

## License

MIT License