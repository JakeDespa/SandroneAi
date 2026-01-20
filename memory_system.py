"""
Memory System for Sandrone AI
Persistent memory that learns and remembers across conversations
"""

import json
import os
from datetime import datetime
from pathlib import Path


class MemorySystem:
    """Persistent memory system for storing and retrieving learned information"""
    
    def __init__(self, memory_file="sandrone_memory.json"):
        """Initialize the memory system"""
        self.memory_dir = Path.home() / "SandroneAI_Files"
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / memory_file
        
        # Load existing memories
        self.memories = self._load_memories()
    
    def _load_memories(self):
        """Load memories from file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Memory] Error loading memories: {e}")
                return self._create_empty_memory()
        return self._create_empty_memory()
    
    def _create_empty_memory(self):
        """Create empty memory structure"""
        return {
            "visitors": {},  # Information about people who talk to Sandrone
            "facts": [],  # Important facts learned
            "research_notes": [],  # Her research discoveries
            "events": [],  # Significant events/conversations
            "preferences": {},  # Her preferences and opinions
            "last_updated": datetime.now().isoformat()
        }
    
    def save_memories(self):
        """Save memories to file"""
        try:
            self.memories["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, indent=2, ensure_ascii=False)
            print(f"[Memory] Saved to {self.memory_file}")
        except Exception as e:
            print(f"[Memory] Error saving memories: {e}")
    
    def add_visitor_info(self, visitor_id, info):
        """Add or update information about a visitor"""
        if visitor_id not in self.memories["visitors"]:
            self.memories["visitors"][visitor_id] = {
                "first_contact": datetime.now().isoformat(),
                "facts": [],
                "interactions": 0
            }
        
        self.memories["visitors"][visitor_id]["facts"].append({
            "info": info,
            "timestamp": datetime.now().isoformat()
        })
        self.memories["visitors"][visitor_id]["interactions"] += 1
        self.save_memories()
    
    def add_fact(self, fact, category="general"):
        """Add a learned fact"""
        self.memories["facts"].append({
            "fact": fact,
            "category": category,
            "learned_on": datetime.now().isoformat()
        })
        self.save_memories()
    
    def add_research_note(self, note):
        """Add a research note"""
        self.memories["research_notes"].append({
            "note": note,
            "timestamp": datetime.now().isoformat()
        })
        self.save_memories()
    
    def add_event(self, event_description):
        """Record a significant event"""
        self.memories["events"].append({
            "event": event_description,
            "timestamp": datetime.now().isoformat()
        })
        self.save_memories()
    
    def set_preference(self, key, value):
        """Set a preference or opinion"""
        self.memories["preferences"][key] = {
            "value": value,
            "set_on": datetime.now().isoformat()
        }
        self.save_memories()
    
    def get_visitor_info(self, visitor_id):
        """Get information about a specific visitor"""
        return self.memories["visitors"].get(visitor_id, None)
    
    def get_recent_facts(self, limit=10):
        """Get recent facts learned"""
        return self.memories["facts"][-limit:] if self.memories["facts"] else []
    
    def get_recent_events(self, limit=5):
        """Get recent events"""
        return self.memories["events"][-limit:] if self.memories["events"] else []
    
    def get_all_research_notes(self):
        """Get all research notes"""
        return self.memories["research_notes"]
    
    def search_memories(self, query):
        """Search through memories for relevant information"""
        results = []
        query_lower = query.lower()
        
        # Search facts
        for fact in self.memories["facts"]:
            if query_lower in fact["fact"].lower():
                results.append(f"Fact: {fact['fact']}")
        
        # Search research notes
        for note in self.memories["research_notes"]:
            if query_lower in note["note"].lower():
                results.append(f"Research: {note['note']}")
        
        # Search events
        for event in self.memories["events"]:
            if query_lower in event["event"].lower():
                results.append(f"Event: {event['event']}")
        
        return results
    
    def get_memory_summary(self):
        """Get a summary of current memories"""
        summary = []
        
        # Visitor count
        visitor_count = len(self.memories["visitors"])
        if visitor_count > 0:
            summary.append(f"I have interacted with {visitor_count} visitor(s).")
        
        # Recent facts
        recent_facts = self.get_recent_facts(5)
        if recent_facts:
            summary.append("\nRecent facts I've learned:")
            for fact in recent_facts:
                summary.append(f"- {fact['fact']}")
        
        # Research notes
        if self.memories["research_notes"]:
            summary.append(f"\nI have recorded {len(self.memories['research_notes'])} research notes.")
        
        # Recent events
        recent_events = self.get_recent_events(3)
        if recent_events:
            summary.append("\nRecent events:")
            for event in recent_events:
                summary.append(f"- {event['event']}")
        
        return "\n".join(summary) if summary else "No memories recorded yet."
    
    def build_memory_context(self):
        """Build context string from memories for AI prompt"""
        context_parts = []
        
        # Add recent important facts
        recent_facts = self.get_recent_facts(15)
        if recent_facts:
            context_parts.append("=== YOUR RECORDED MEMORIES ===")
            context_parts.append("Facts you have learned:")
            for fact in recent_facts:
                context_parts.append(f"- {fact['fact']}")
        
        # Add research notes
        research_notes = self.get_all_research_notes()
        if research_notes and len(research_notes) > 0:
            context_parts.append("\nYour research notes:")
            for note in research_notes[-10:]:  # Last 10 notes
                context_parts.append(f"- {note['note']}")
        
        # Add recent events
        recent_events = self.get_recent_events(5)
        if recent_events:
            context_parts.append("\nRecent events in your workshop:")
            for event in recent_events:
                context_parts.append(f"- {event['event']}")
        
        # Add preferences
        if self.memories["preferences"]:
            context_parts.append("\nYour documented preferences:")
            for key, pref in list(self.memories["preferences"].items())[:10]:
                context_parts.append(f"- {key}: {pref['value']}")
        
        if context_parts:
            context_parts.append("=== END MEMORIES ===\n")
            return "\n".join(context_parts)
        
        return ""
    
    def extract_learnable_info(self, user_message, ai_response):
        """
        Automatically extract and save learnable information from conversation
        This is a simple implementation - can be enhanced with better NLP
        """
        # Keywords that indicate important information
        learning_keywords = [
            "my name is", "i am", "i'm", "i work", "i like", "i hate",
            "remember", "note that", "important", "discovered", "learned"
        ]
        
        user_lower = user_message.lower()
        
        # Check if user is sharing personal information
        for keyword in learning_keywords:
            if keyword in user_lower:
                # This is something worth remembering
                self.add_fact(user_message, category="visitor_info")
                return True
        
        # Check if AI mentioned research or discoveries in response
        if any(word in ai_response.lower() for word in ["research", "experiment", "discovered", "analyzed"]):
            # Could be a research note
            if len(ai_response) < 500:  # Only save concise notes
                self.add_research_note(ai_response[:200])
        
        return False
    
    def clear_memories(self):
        """Clear all memories (use with caution)"""
        self.memories = self._create_empty_memory()
        self.save_memories()
        print("[Memory] All memories cleared")
    
    def export_memories(self, export_path=None):
        """Export memories to a readable text file"""
        if export_path is None:
            export_path = self.memory_dir / "memory_export.txt"
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write("=== SANDRONE'S MEMORY BANK ===\n")
                f.write(f"Last Updated: {self.memories['last_updated']}\n\n")
                
                f.write(f"--- VISITORS ({len(self.memories['visitors'])}) ---\n")
                for visitor_id, info in self.memories['visitors'].items():
                    f.write(f"\nVisitor: {visitor_id}\n")
                    f.write(f"First Contact: {info['first_contact']}\n")
                    f.write(f"Interactions: {info['interactions']}\n")
                    f.write("Facts:\n")
                    for fact in info['facts']:
                        f.write(f"  - {fact['info']}\n")
                
                f.write(f"\n--- FACTS ({len(self.memories['facts'])}) ---\n")
                for fact in self.memories['facts']:
                    f.write(f"- {fact['fact']} (Category: {fact['category']})\n")
                
                f.write(f"\n--- RESEARCH NOTES ({len(self.memories['research_notes'])}) ---\n")
                for note in self.memories['research_notes']:
                    f.write(f"- {note['note']}\n")
                
                f.write(f"\n--- EVENTS ({len(self.memories['events'])}) ---\n")
                for event in self.memories['events']:
                    f.write(f"- {event['event']}\n")
                
                f.write(f"\n--- PREFERENCES ({len(self.memories['preferences'])}) ---\n")
                for key, pref in self.memories['preferences'].items():
                    f.write(f"- {key}: {pref['value']}\n")
            
            print(f"[Memory] Exported to {export_path}")
            return str(export_path)
        except Exception as e:
            print(f"[Memory] Export error: {e}")
            return None
