"""
Knowledge Base System for Sandrone AI
Loads and queries structured Genshin Impact lore and information
"""

import json
import os
from pathlib import Path


class KnowledgeBase:
    """Knowledge base system for accessing structured lore information"""
    
    def __init__(self, knowledge_file="knowledge_base.json"):
        """Initialize the knowledge base"""
        self.base_dir = Path(__file__).parent
        self.knowledge_file = self.base_dir / knowledge_file
        
        # Load knowledge base
        self.knowledge = self._load_knowledge()
        
        print(f"[Knowledge Base] Loaded from {self.knowledge_file}")
        print(f"[Knowledge Base] Version: {self.knowledge.get('version', 'unknown')}")
    
    def _load_knowledge(self):
        """Load knowledge from JSON file"""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Knowledge Base] Error loading: {e}")
                return {}
        else:
            print(f"[Knowledge Base] File not found: {self.knowledge_file}")
            return {}
    
    def reload_knowledge(self):
        """Reload knowledge base from file"""
        self.knowledge = self._load_knowledge()
        return True
    
    def get_nation_info(self, nation_name):
        """Get information about a specific nation"""
        nation_name = nation_name.lower()
        nations = self.knowledge.get('nations', {})
        
        if nation_name in nations:
            return nations[nation_name]
        return None
    
    def get_harbinger_info(self, harbinger_name):
        """Get information about a specific Harbinger"""
        harbingers = self.knowledge.get('fatui_harbingers', {})
        
        # Try to find by name or number
        for key, info in harbingers.items():
            if harbinger_name.lower() in key.lower():
                return info
            if info.get('name', '').lower() == harbinger_name.lower():
                return info
            if info.get('title', '').lower() == harbinger_name.lower():
                return info
        
        return None
    
    def get_all_harbingers(self):
        """Get information about all Harbingers"""
        return self.knowledge.get('fatui_harbingers', {})
    
    def get_lore_topic(self, topic):
        """Get information about a major lore topic"""
        topic = topic.lower()
        lore = self.knowledge.get('major_lore', {})
        
        if topic in lore:
            return lore[topic]
        
        # Try partial matching
        for key, info in lore.items():
            if topic in key.lower():
                return info
        
        return None
    
    def get_recent_updates(self):
        """Get recent story updates"""
        return self.knowledge.get('recent_story_updates', {})
    
    def get_sandrone_info(self):
        """Get Sandrone-specific information"""
        return self.knowledge.get('sandrone_specific', {})
    
    def get_technical_knowledge(self, topic=None):
        """Get technical knowledge about game mechanics"""
        tech = self.knowledge.get('technical_knowledge', {})
        
        if topic:
            topic = topic.lower()
            for key, info in tech.items():
                if topic in key.lower():
                    return info
        
        return tech
    
    def search(self, query):
        """Search through knowledge base for relevant information"""
        query = query.lower()
        results = []
        
        # Search nations
        for name, info in self.knowledge.get('nations', {}).items():
            if query in name.lower() or query in str(info).lower():
                results.append({
                    'category': 'Nation',
                    'name': name.title(),
                    'data': info
                })
        
        # Search Harbingers
        for key, info in self.knowledge.get('fatui_harbingers', {}).items():
            if query in key.lower() or query in str(info).lower():
                results.append({
                    'category': 'Fatui Harbinger',
                    'name': info.get('name', key),
                    'data': info
                })
        
        # Search major lore
        for topic, info in self.knowledge.get('major_lore', {}).items():
            if query in topic.lower() or query in str(info).lower():
                results.append({
                    'category': 'Lore',
                    'name': topic.title(),
                    'data': info
                })
        
        # Search recent updates
        for version, info in self.knowledge.get('recent_story_updates', {}).items():
            if query in version.lower() or query in str(info).lower():
                results.append({
                    'category': 'Recent Update',
                    'name': version,
                    'data': info
                })
        
        return results
    
    def build_context_string(self, relevant_topics=None):
        """Build a context string for AI prompt"""
        if not relevant_topics:
            # Return summary of available knowledge
            context_parts = ["=== KNOWLEDGE BASE ACCESS ==="]
            context_parts.append("You have access to detailed information about:")
            context_parts.append(f"- {len(self.knowledge.get('nations', {}))} Nations")
            context_parts.append(f"- {len(self.knowledge.get('fatui_harbingers', {}))} Fatui Harbingers")
            context_parts.append(f"- Major lore topics (Celestia, Khaenri'ah, Abyss, etc.)")
            context_parts.append(f"- Recent updates (Version {self.knowledge.get('version', 'unknown')})")
            context_parts.append("=== END KNOWLEDGE BASE ===\n")
            return "\n".join(context_parts)
        
        # Return specific information
        context_parts = ["=== KNOWLEDGE BASE - RELEVANT INFORMATION ==="]
        
        for topic in relevant_topics:
            # Try to find relevant info
            if topic in self.knowledge.get('nations', {}):
                info = self.get_nation_info(topic)
                context_parts.append(f"\n{topic.upper()}:")
                context_parts.append(json.dumps(info, indent=2))
            
            elif topic in self.knowledge.get('major_lore', {}):
                info = self.get_lore_topic(topic)
                context_parts.append(f"\n{topic.upper()}:")
                context_parts.append(json.dumps(info, indent=2))
        
        context_parts.append("\n=== END KNOWLEDGE BASE ===\n")
        return "\n".join(context_parts)
    
    def get_summary(self):
        """Get summary of knowledge base contents"""
        summary = []
        summary.append(f"Knowledge Base Version: {self.knowledge.get('version', 'unknown')}")
        summary.append(f"Last Updated: {self.knowledge.get('last_updated', 'unknown')}")
        summary.append(f"\nContents:")
        summary.append(f"- Nations: {len(self.knowledge.get('nations', {}))}")
        summary.append(f"- Fatui Harbingers: {len(self.knowledge.get('fatui_harbingers', {}))}")
        summary.append(f"- Major Lore Topics: {len(self.knowledge.get('major_lore', {}))}")
        summary.append(f"- Recent Story Updates: {len(self.knowledge.get('recent_story_updates', {}))}")
        summary.append(f"- Technical Knowledge: {len(self.knowledge.get('technical_knowledge', {}))}")
        
        # Sandrone-specific
        sandrone_info = self.get_sandrone_info()
        if sandrone_info:
            summary.append(f"\nSandrone-Specific Information:")
            summary.append(f"- Current Research Projects: {len(sandrone_info.get('current_research', []))}")
            summary.append(f"- Known Creations: {len(sandrone_info.get('known_creations', []))}")
        
        return "\n".join(summary)
    
    def format_for_display(self, data, indent=0):
        """Format data for human-readable display"""
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                indent_str = "  " * indent
                if isinstance(value, (dict, list)):
                    lines.append(f"{indent_str}{key}:")
                    lines.append(self.format_for_display(value, indent + 1))
                else:
                    lines.append(f"{indent_str}{key}: {value}")
            return "\n".join(lines)
        elif isinstance(data, list):
            lines = []
            for item in data:
                indent_str = "  " * indent
                if isinstance(item, (dict, list)):
                    lines.append(self.format_for_display(item, indent))
                else:
                    lines.append(f"{indent_str}- {item}")
            return "\n".join(lines)
        else:
            return str(data)
