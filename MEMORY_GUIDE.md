# Memory System Guide

## Overview
Sandrone now has a persistent memory system that remembers information across conversations!

## Location
All memories are stored in: `C:\Users\Jake Despa\SandroneAI_Files\sandrone_memory.json`

## What Gets Remembered

### Automatic Learning (when AUTO_MEMORY_LEARNING = True)
- User information (when they share names, preferences, etc.)
- Important facts from conversations
- Research discoveries mentioned by Sandrone
- Key events and interactions

### Memory Categories
1. **Visitors** - Information about people who interact with Sandrone
2. **Facts** - General knowledge and learned information
3. **Research Notes** - Her ongoing research and experiments
4. **Events** - Significant occurrences in her workshop
5. **Preferences** - Her documented opinions and preferences

## API Endpoints

### View Memory Summary
```
GET http://localhost:5000/memory
```
Returns statistics and a summary of what Sandrone remembers.

### Add Memory Manually
```
POST http://localhost:5000/memory/add
{
    "type": "fact",  // or "research" or "event"
    "content": "The visitor prefers tea over coffee",
    "category": "visitor_info"  // optional, for facts
}
```

### Export Memories
```
GET http://localhost:5000/memory/export
```
Exports all memories to a readable text file.

### Clear All Memories (Caution!)
```
POST http://localhost:5000/memory/clear
```
Deletes all stored memories.

## Using Memory in Chat

Sandrone will automatically:
1. **Reference past conversations** - "As we discussed before..."
2. **Remember your preferences** - "I recall you mentioned..."
3. **Build on previous topics** - Continuing research themes
4. **Recognize returning visitors** - Track interaction history

## Manual Memory Management

### Add Important Facts
Tell Sandrone to remember something:
- "Remember that I'm a researcher"
- "Note that I prefer technical discussions"
- "My name is [name]"

### View Her Memories
The AI can access her memories naturally in conversation. Ask:
- "What do you remember about our conversations?"
- "What research have you been working on?"
- "What have you learned recently?"

## Configuration

In `config.py`:
```python
AUTO_MEMORY_LEARNING = True   # AI learns automatically
MEMORY_ENABLED = True          # Enable memory system
```

## Memory File Structure

```json
{
  "visitors": {
    "visitor_123": {
      "first_contact": "2026-01-20T...",
      "facts": [...],
      "interactions": 5
    }
  },
  "facts": [
    {
      "fact": "The visitor studies mechanical engineering",
      "category": "visitor_info",
      "learned_on": "2026-01-20T..."
    }
  ],
  "research_notes": [...],
  "events": [...],
  "preferences": {...}
}
```

## Tips

1. **Be specific** - Detailed information gets stored better
2. **Regular exports** - Backup your memories periodically
3. **Review memories** - Check what's been learned: GET /memory
4. **Clear old data** - Clean up if memory grows too large

## Example Interactions

**User**: "My name is Alex and I'm interested in Khaenri'ah technology"
**System**: *Automatically saves: "The visitor's name is Alex" and "interested in Khaenri'ah technology"*

**Later conversation...**
**User**: "What do you remember about me?"
**Sandrone**: "You mentioned your name is Alex, and you've shown interest in Khaenri'ahn technology..."

## Advanced: Python API

```python
from memory_system import MemorySystem

memory = MemorySystem()

# Add fact
memory.add_fact("Discovered new automaton design", category="research")

# Add event
memory.add_event("Successfully tested puppet Mark VII")

# Search memories
results = memory.search_memories("automaton")

# Get summary
summary = memory.get_memory_summary()
```

## Troubleshooting

**Memories not persisting?**
- Check if memory file exists: `C:\Users\Jake Despa\SandroneAI_Files\sandrone_memory.json`
- Ensure AUTO_MEMORY_LEARNING = True in config.py
- Verify file permissions

**Too much memory being stored?**
- Review with: GET /memory
- Clear selectively or completely with: POST /memory/clear
- Adjust learning sensitivity in memory_system.py

**Want more control?**
- Disable AUTO_MEMORY_LEARNING
- Manually add important facts via API
- Create custom memory categories
