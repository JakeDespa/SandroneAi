# How to Add Custom Information to Local Cache

## What is the Local Cache?
Since web search is blocked on your network, the local cache allows you to manually add information that Sandrone can search and reference.

## Quick Start

### 1. Run the cache script to add an entry:

```powershell
& ".venv\Scripts\python.exe" -c "from local_search_cache import LocalSearchCache; cache = LocalSearchCache(); cache.add_entry('Topic Name', 'Detailed information about the topic...', 'Your Source')"
```

### 2. Or use the interactive script:

```python
from local_search_cache import LocalSearchCache

cache = LocalSearchCache()

# Add an entry
cache.add_entry(
    topic="Your Topic Here",
    content="Detailed information, facts, and data about the topic. "
            "Include as much detail as you want - the AI will search through this.",
    source="Where you got this info (optional)"
)

print("✓ Entry added!")
```

## Examples

### Example 1: Add Game Information
```python
from local_search_cache import LocalSearchCache
cache = LocalSearchCache()

cache.add_entry(
    "Genshin Impact 5.4 Leaks",
    "Version 5.4 is rumored to feature new characters including Arlecchino's banner rerun. "
    "The update may include the next chapter of the Fontaine storyline and new events. "
    "Expected release: March 2026.",
    "Community Forums"
)
```

### Example 2: Add Technical Information
```python
cache.add_entry(
    "Python Type Hints Best Practices",
    "Type hints improve code readability and enable better IDE support. "
    "Use from typing import List, Dict, Optional for generic types. "
    "Python 3.10+ supports using list, dict directly. "
    "Use mypy for static type checking.",
    "Python Documentation"
)
```

### Example 3: Add Current Events
```python
cache.add_entry(
    "Tech News January 2026",
    "Major tech developments in January 2026 include advances in quantum computing, "
    "new AI models from OpenAI and Anthropic, and the release of several major software updates. "
    "Apple announced new M4 chips with improved AI acceleration.",
    "Tech News Websites"
)
```

## Check What's in the Cache

```python
from local_search_cache import LocalSearchCache
cache = LocalSearchCache()

# List all topics
topics = cache.get_all_topics()
for topic in topics:
    print(f"  - {topic}")

# Search for something
results = cache.search("your search query")
print(cache.format_results(results))
```

## Directly Edit the Cache File

The cache is stored in `local_search_cache.json`. You can edit it directly:

```json
{
  "entries": {
    "your_topic_id": {
      "topic": "Your Topic Name",
      "content": "Your detailed content here...",
      "source": "Where you got this",
      "added_date": "2026-01-20 22:00:00",
      "tags": ["topic", "name"]
    }
  },
  "metadata": {
    "created": "2026-01-20 22:00:00",
    "last_updated": "2026-01-20 22:05:00"
  }
}
```

## How Sandrone Uses the Cache

When you ask Sandrone a question, she will:
1. **First check the local cache** for matching information
2. If found, use the cached information immediately
3. If not found, try web search (which will fail due to network blocks)
4. Fall back to her built-in AI knowledge

## Adding Bulk Information

Create a Python script to add multiple entries at once:

```python
from local_search_cache import LocalSearchCache

cache = LocalSearchCache()

entries = [
    ("Topic 1", "Content for topic 1...", "Source 1"),
    ("Topic 2", "Content for topic 2...", "Source 2"),
    ("Topic 3", "Content for topic 3...", "Source 3"),
]

for topic, content, source in entries:
    cache.add_entry(topic, content, source)

print(f"✓ Added {len(entries)} entries!")
```

## Tips

1. **Be Detailed**: Add as much detail as you can - the AI searches through all content
2. **Use Keywords**: Include relevant keywords that someone might search for
3. **Update Regularly**: Add new information as you learn it
4. **Organize by Category**: Use consistent source names to group related topics
5. **Include Dates**: Mention when information is from (especially for news/updates)

## Pre-populated Entries

The cache comes with these sample entries:
- Genshin Impact Version 5.3
- Python 3.13 Features
- Latest AI Developments 2026

You can delete or modify these by editing `local_search_cache.json`.

## Testing Your Entries

After adding entries, test them:

```python
from local_search_cache import LocalSearchCache

cache = LocalSearchCache()

# Search for your new entry
results = cache.search("your topic keywords")

if results:
    print("✓ Found!")
    print(cache.format_results(results))
else:
    print("✗ Not found - try different keywords")
```

## Integration with Sandrone

The local cache is automatically integrated. When Sandrone needs information:
- She checks the cache first (instant results)
- Uses her AI knowledge if not in cache
- Learns from conversations (memory system)

You can also tell her explicitly:
- "Search for [topic] in the local cache"
- "What do you know about [cached topic]"
- "Check the cache for information about [topic]"
