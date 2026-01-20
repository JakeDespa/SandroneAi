"""
Local Search Cache - Manual knowledge addition system
When web search is blocked, you can manually add information here
"""

import json
from pathlib import Path
from datetime import datetime


class LocalSearchCache:
    """Cache for manually added search results"""
    
    def __init__(self, cache_file="local_search_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache from file"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"entries": {}, "metadata": {"created": str(datetime.now())}}
    
    def _save_cache(self):
        """Save cache to file"""
        self.cache["metadata"]["last_updated"] = str(datetime.now())
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2)
    
    def add_entry(self, topic, content, source="Manual Entry"):
        """Add a search result manually"""
        entry_id = topic.lower().replace(' ', '_')
        
        self.cache["entries"][entry_id] = {
            "topic": topic,
            "content": content,
            "source": source,
            "added_date": str(datetime.now()),
            "tags": self._generate_tags(topic)
        }
        
        self._save_cache()
        print(f"✓ Added entry: {topic}")
    
    def search(self, query):
        """Search cached entries"""
        query_lower = query.lower()
        results = []
        
        for entry_id, entry in self.cache["entries"].items():
            # Check if query matches topic or content
            if query_lower in entry["topic"].lower() or \
               query_lower in entry["content"].lower() or \
               any(query_lower in tag.lower() for tag in entry.get("tags", [])):
                results.append(entry)
        
        return results
    
    def _generate_tags(self, topic):
        """Generate search tags from topic"""
        words = topic.lower().split()
        return [word for word in words if len(word) > 3]
    
    def get_all_topics(self):
        """Get list of all cached topics"""
        return [entry["topic"] for entry in self.cache["entries"].values()]
    
    def format_results(self, results):
        """Format search results for display"""
        if not results:
            return None
        
        output = ["Locally cached information:\n"]
        
        for i, result in enumerate(results, 1):
            output.append(f"{i}. {result['topic']}")
            output.append(f"   {result['content'][:200]}...")
            output.append(f"   Source: {result['source']}")
            output.append(f"   Added: {result['added_date'][:10]}\n")
        
        return "\n".join(output)


# Example usage and pre-populated entries
def initialize_cache():
    """Initialize cache with some useful entries"""
    cache = LocalSearchCache()
    
    # Add some example entries about recent topics
    if not cache.cache["entries"]:
        cache.add_entry(
            "Genshin Impact Version 5.3",
            "Genshin Impact version 5.3 'Incandescent Ode of Resurrection' was released in January 2026. "
            "It features the conclusion of Natlan's Archon Quest Act V 'Beyond the Smoke and Mirrors', "
            "new character Mavuika (Pyro Archon), and the Pyro Traveler element unlocking. "
            "The update includes the Night Kingdom's secret realm and major story developments about the Abyss conflict.",
            "Game Updates"
        )
        
        cache.add_entry(
            "Python 3.13 Features",
            "Python 3.13 introduces improved error messages, better performance through bytecode optimizations, "
            "and experimental JIT compiler support. The release focuses on developer experience with clearer "
            "tracebacks and faster execution speeds.",
            "Programming Languages"
        )
        
        cache.add_entry(
            "Latest AI Developments 2026",
            "In 2026, AI developments include: improved local LLMs that run on consumer hardware, "
            "better multimodal models combining text/image/audio, enhanced reasoning capabilities, "
            "and increased focus on privacy-preserving AI that runs locally without cloud dependence.",
            "Technology News"
        )
        
        print(f"✓ Initialized cache with {len(cache.cache['entries'])} sample entries")
    
    return cache


if __name__ == "__main__":
    # Initialize and test
    cache = initialize_cache()
    
    print("\n" + "="*60)
    print("Local Search Cache - Testing")
    print("="*60)
    
    print("\nAll Topics:")
    for topic in cache.get_all_topics():
        print(f"  - {topic}")
    
    print("\n" + "="*60)
    print("Test Search: 'Genshin Impact'")
    print("="*60)
    results = cache.search("Genshin Impact")
    print(cache.format_results(results))
    
    print("\n" + "="*60)
    print("Test Search: 'Python'")
    print("="*60)
    results = cache.search("Python")
    print(cache.format_results(results))
