"""
Chronicle module - Narrative logging system for emergent storytelling.
Records important events and milestones throughout the simulation.
"""

from typing import List, Tuple
from datetime import datetime


class Chronicle:
    """
    The Chronicle records all important events that occur during the simulation.
    This creates the emergent narrative that makes the simulation interesting.
    
    Attributes:
        events: List of (year, message) tuples for regular events
        major_events: List of (year, message) tuples for major milestones
        verbose: Whether to print events as they occur
    """
    
    def __init__(self, verbose: bool = True):
        self.events: List[Tuple[int, str]] = []
        self.major_events: List[Tuple[int, str]] = []
        self.verbose = verbose
    
    def log_event(self, year: int, message: str):
        """Log a regular event."""
        self.events.append((year, message))
        if self.verbose:
            print(f"  [Year {year}] {message}")
    
    def log_major_event(self, year: int, message: str):
        """Log a major milestone event."""
        self.major_events.append((year, message))
        if self.verbose:
            print(f"\n*** [YEAR {year}] {message} ***\n")
    
    def get_events_for_year(self, year: int) -> List[str]:
        """Get all events that occurred in a specific year."""
        return [msg for y, msg in self.events if y == year]
    
    def get_major_events(self) -> List[Tuple[int, str]]:
        """Get all major events."""
        return self.major_events.copy()
    
    def print_summary(self):
        """Print a summary of the simulation history."""
        print("\n" + "=" * 60)
        print("         CHRONICLE OF THE REALM")
        print("=" * 60)
        
        if not self.major_events:
            print("No major events occurred during this period.")
        else:
            print("\nMajor Events:")
            print("-" * 40)
            for year, message in self.major_events:
                print(f"Year {year}: {message}")
        
        print("\n" + "-" * 40)
        print(f"Total events recorded: {len(self.events)}")
        print(f"Major milestones: {len(self.major_events)}")
        print("=" * 60)
    
    def export_to_file(self, filename: str = None):
        """Export the chronicle to a text file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chronicle_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("CHRONICLE OF THE REALM\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("MAJOR EVENTS:\n")
            f.write("-" * 30 + "\n")
            for year, message in self.major_events:
                f.write(f"Year {year}: {message}\n")
            
            f.write("\n\nDETAILED EVENTS:\n")
            f.write("-" * 30 + "\n")
            for year, message in self.events:
                f.write(f"Year {year}: {message}\n")
        
        print(f"Chronicle exported to: {filename}")
        return filename
    
    def __repr__(self):
        return f"Chronicle({len(self.events)} events, {len(self.major_events)} major)"
