"""
Tools System for Sandrone AI
Provides web search and file system access capabilities
"""

import os
import json
import requests
import time
import urllib.request
import urllib.parse
import ssl
from pathlib import Path
from datetime import datetime

# Try to import local search cache
try:
    from local_search_cache import LocalSearchCache
    LOCAL_CACHE_AVAILABLE = True
except ImportError:
    LOCAL_CACHE_AVAILABLE = False


class Tools:
    """Tool system for web search and file operations"""
    
    def __init__(self):
        self.available_tools = {
            'web_search': self.web_search,
            'read_file': self.read_file,
            'write_file': self.write_file,
            'list_files': self.list_files,
            'create_directory': self.create_directory,
            'get_file_info': self.get_file_info
        }
        
        # Safe directory for file operations (user's documents or a specific folder)
        self.safe_directory = Path.home() / "SandroneAI_Files"
        self.safe_directory.mkdir(exist_ok=True)
        
        # Initialize local search cache
        if LOCAL_CACHE_AVAILABLE:
            try:
                self.local_cache = LocalSearchCache()
                print("[Local Cache] Initialized successfully")
            except Exception as e:
                print(f"[Local Cache] Failed to initialize: {e}")
                self.local_cache = None
        else:
            self.local_cache = None
        
        # Configure requests session with retry logic
        self.session = requests.Session()
        self.session.max_redirects = 5
        
        # Disable SSL warnings (for corporate SSL inspection)
        import warnings
        from urllib3.exceptions import InsecureRequestWarning
        warnings.simplefilter('ignore', InsecureRequestWarning)
    
    def get_tool_descriptions(self):
        """Return descriptions of available tools for the AI"""
        return """
AVAILABLE TOOLS:
You can use the following tools by requesting them in your response. Format: [TOOL:tool_name:parameters]

1. [TOOL:web_search:query] - Search the internet for information
   Example: [TOOL:web_search:latest news about Genshin Impact]

2. [TOOL:read_file:filename] - Read contents of a file
   Example: [TOOL:read_file:research_notes.txt]

3. [TOOL:write_file:filename:content] - Write content to a file
   Example: [TOOL:write_file:notes.txt:My research findings...]

4. [TOOL:list_files:directory] - List files in a directory (optional, defaults to your workspace)
   Example: [TOOL:list_files:] or [TOOL:list_files:subfolder]

5. [TOOL:create_directory:directory_name] - Create a new directory
   Example: [TOOL:create_directory:research_data]

6. [TOOL:get_file_info:filename] - Get information about a file
   Example: [TOOL:get_file_info:data.txt]

When you need to use a tool, include the tool call in your response. The tool will be executed and you'll be informed of the results.
All file operations happen in: {safe_dir}
"""
    
    def web_search(self, query):
        """Search the web using multiple methods for better results"""
        try:
            print(f"[Web Search] Querying: {query}")
            
            # Method 0: Check local cache first (when internet is blocked)
            if self.local_cache:
                cache_results = self.local_cache.search(query)
                if cache_results:
                    formatted = self.local_cache.format_results(cache_results)
                    print(f"[Local Cache] Found {len(cache_results)} cached results")
                    return formatted
            
            # Method 1: Try Wikipedia API for factual queries
            wiki_result = self._try_wikipedia(query)
            if wiki_result and len(wiki_result) > 100:
                print(f"[Web Search] Wikipedia result found")
                return wiki_result
            
            # Method 2: Try Wikimedia (alternative Wikipedia endpoint)
            wikimedia_result = self._try_wikimedia(query)
            if wikimedia_result and len(wikimedia_result) > 100:
                print(f"[Web Search] Wikimedia result found")
                return wikimedia_result
            
            # Method 3: Try DuckDuckGo instant answer
            ddg_result = self._try_instant_answer(query)
            if ddg_result and "Limited information" not in ddg_result:
                print(f"[Web Search] DuckDuckGo instant answer found")
                return ddg_result
            
            # Method 4: Try HTML scraping with better headers and retry logic
            html_result = self._try_html_scraping(query)
            if html_result:
                return html_result
            
            # Method 5: Try SearxNG public instance
            searx_result = self._try_searxng(query)
            if searx_result:
                return searx_result
            
            # Method 6: Try Brave Search API (free tier)
            brave_result = self._try_brave_search(query)
            if brave_result:
                return brave_result
            
            # Method 7: Try direct HTTP without HTTPS
            http_result = self._try_http_fallback(query)
            if http_result:
                return http_result
            
            # If all methods fail, return a helpful message
            print("[Web Search] All methods exhausted")
            return f"Web search was attempted for '{query}' but current detailed results are unavailable. This could be due to search rate limits or network restrictions. The AI will answer based on its training knowledge."
                
        except Exception as e:
            print(f"[Web Search] Error: {str(e)}")
            return f"Web search encountered an error but the AI can still answer based on knowledge: {str(e)}"
    
    def _try_html_scraping(self, query):
        """Try HTML scraping with enhanced methods"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        search_urls = [
            f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}",
            f"https://lite.duckduckgo.com/lite/?q={requests.utils.quote(query)}"
        ]
        
        for attempt, (url, ua) in enumerate([(u, user_agents[i % len(user_agents)]) for i, u in enumerate(search_urls)]):
            try:
                headers = {
                    'User-Agent': ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                print(f"[HTML Scraping] Attempt {attempt + 1} with {url.split('/')[2]}")
                response = requests.get(url, headers=headers, timeout=15)
                
                print(f"[HTML Scraping] Status: {response.status_code}")
                
                if response.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract results
                    results = []
                    
                    # Try multiple selectors
                    result_divs = soup.find_all('div', class_='result') or \
                                  soup.find_all('div', class_='web-result') or \
                                  soup.find_all('tr')
                    
                    for i, div in enumerate(result_divs[:5], 1):
                        title = None
                        snippet = None
                        link = None
                        
                        # Try different structures
                        title_elem = div.find('a', class_='result__a') or \
                                     div.find('a', class_='result-link') or \
                                     div.find('a')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link = title_elem.get('href', '')
                        
                        snippet_elem = div.find('div', class_='result__snippet') or \
                                       div.find('td', class_='result-snippet') or \
                                       div.find('div', class_='snippet')
                        
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)
                        
                        if title and snippet:
                            results.append(f"{i}. {title}\n   {snippet}\n   Source: {link}\n")
                    
                    if results:
                        result_text = f"Web search results for '{query}':\n\n" + "\n".join(results)
                        print(f"[HTML Scraping] Found {len(results)} results")
                        return result_text
                
                # Rate limit backoff
                if attempt < len(search_urls) - 1:
                    time.sleep(2)
                    
            except Exception as e:
                print(f"[HTML Scraping] Attempt {attempt + 1} failed: {str(e)}")
                continue
        
        return None
    
    def _try_wikipedia(self, query):
        """Try Wikipedia API with multiple approaches"""
        wiki_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(query)
        
        # Method 1: urllib (WORKS - bypasses requests/SSL issues)
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(
                wiki_url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get('extract'):
                        result = f"Wikipedia Summary:\n{data['extract']}\n\nSource: {data.get('content_urls', {}).get('desktop', {}).get('page', '')}"
                        print(f"[Wikipedia] Success via urllib")
                        return result
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"[Wikipedia] Page not found for '{query}'")
            else:
                print(f"[Wikipedia] urllib HTTP error: {e.code}")
        except Exception as e:
            print(f"[Wikipedia] urllib method failed: {str(e)}")
        
        # Method 2: Try with requests library as fallback
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            response = self.session.get(wiki_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('extract'):
                    result = f"Wikipedia Summary:\n{data['extract']}\n\nSource: {data.get('content_urls', {}).get('desktop', {}).get('page', '')}"
                    print(f"[Wikipedia] Success via requests")
                    return result
        except Exception as e:
            print(f"[Wikipedia] Requests method failed: {str(e)}")
        
        return None
    
    def _try_wikimedia(self, query):
        """Try alternative Wikimedia API endpoint"""
        try:
            # Try Wikimedia search API
            search_url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'srlimit': 3
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                search_results = data.get('query', {}).get('search', [])
                
                if search_results:
                    results = []
                    results.append(f"Wikipedia search results for '{query}':\n")
                    
                    for i, result in enumerate(search_results, 1):
                        title = result.get('title', '')
                        snippet = result.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
                        
                        # Get full summary for first result
                        if i == 1:
                            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}"
                            try:
                                summary_response = requests.get(summary_url, timeout=10)
                                if summary_response.status_code == 200:
                                    summary_data = summary_response.json()
                                    extract = summary_data.get('extract', snippet)
                                    results.append(f"{i}. {title}\n   {extract}\n")
                                else:
                                    results.append(f"{i}. {title}\n   {snippet}\n")
                            except:
                                results.append(f"{i}. {title}\n   {snippet}\n")
                        else:
                            results.append(f"{i}. {title}\n   {snippet}\n")
                    
                    results.append(f"\nSource: https://en.wikipedia.org/")
                    return "\n".join(results)
                    
        except Exception as e:
            print(f"[Wikimedia] Error: {str(e)}")
        return None
    
    def _try_searxng(self, query):
        """Try SearxNG public instance for search"""
        searx_instances = [
            "https://searx.be",
            "https://search.bus-hit.me",
            "https://searx.tiekoetter.com"
        ]
        
        for instance in searx_instances:
            try:
                search_url = f"{instance}/search"
                params = {
                    'q': query,
                    'format': 'json',
                    'categories': 'general'
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                print(f"[SearxNG] Trying {instance}")
                response = requests.get(search_url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    search_results = data.get('results', [])
                    
                    if search_results:
                        results = []
                        results.append(f"Search results for '{query}':\n")
                        
                        for i, result in enumerate(search_results[:5], 1):
                            title = result.get('title', '')
                            content = result.get('content', '')
                            url = result.get('url', '')
                            
                            if title and content:
                                results.append(f"{i}. {title}\n   {content}\n   Source: {url}\n")
                        
                        if len(results) > 1:
                            print(f"[SearxNG] Found {len(results)-1} results from {instance}")
                            return "\n".join(results)
                        
            except Exception as e:
                print(f"[SearxNG] {instance} failed: {str(e)}")
                continue
        
        return None
    
    def _try_instant_answer(self, query):
        """Try DuckDuckGo instant answer API as fallback"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                results = []
                
                if data.get('Abstract'):
                    results.append(f"Summary: {data['Abstract']}")
                    if data.get('AbstractURL'):
                        results.append(f"Source: {data['AbstractURL']}")
                
                if data.get('RelatedTopics'):
                    results.append("\nRelated Information:")
                    for i, topic in enumerate(data['RelatedTopics'][:5], 1):
                        if isinstance(topic, dict) and topic.get('Text'):
                            results.append(f"{i}. {topic['Text']}")
                
                if results:
                    return "\n".join(results)
                
            return f"Limited information available for query: '{query}'. The search may be too specific or require real-time data."
                
        except Exception as e:
            return f"Instant answer API error: {str(e)}"
    
    def read_file(self, filename):
        """Read a file from the safe directory"""
        try:
            filepath = self.safe_directory / filename
            
            if not filepath.exists():
                return f"File '{filename}' does not exist in {self.safe_directory}"
            
            if not filepath.is_file():
                return f"'{filename}' is not a file"
            
            # Read the file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"File '{filename}' contents:\n{content}"
            
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def write_file(self, filename, content):
        """Write content to a file in the safe directory"""
        try:
            filepath = self.safe_directory / filename
            
            # Prevent directory traversal
            if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
                return "Invalid filename: directory traversal not allowed"
            
            # Write the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote to file '{filename}' in {self.safe_directory}"
            
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def list_files(self, directory=""):
        """List files in the safe directory or subdirectory"""
        try:
            if directory:
                target_dir = self.safe_directory / directory
            else:
                target_dir = self.safe_directory
            
            if not target_dir.exists():
                return f"Directory does not exist: {target_dir}"
            
            if not target_dir.is_dir():
                return f"Not a directory: {target_dir}"
            
            # List all files and directories
            items = []
            for item in sorted(target_dir.iterdir()):
                if item.is_file():
                    size = item.stat().st_size
                    items.append(f"📄 {item.name} ({size} bytes)")
                elif item.is_dir():
                    items.append(f"📁 {item.name}/")
            
            if not items:
                return f"Directory is empty: {target_dir}"
            
            return f"Contents of {target_dir}:\n" + "\n".join(items)
            
        except Exception as e:
            return f"Error listing files: {str(e)}"
    
    def create_directory(self, directory_name):
        """Create a directory in the safe directory"""
        try:
            dirpath = self.safe_directory / directory_name
            
            # Prevent directory traversal
            if '..' in directory_name or directory_name.startswith('/') or directory_name.startswith('\\'):
                return "Invalid directory name: directory traversal not allowed"
            
            dirpath.mkdir(parents=True, exist_ok=True)
            
            return f"Directory '{directory_name}' created at {self.safe_directory}"
            
        except Exception as e:
            return f"Error creating directory: {str(e)}"
    
    def get_file_info(self, filename):
        """Get information about a file"""
        try:
            filepath = self.safe_directory / filename
            
            if not filepath.exists():
                return f"File '{filename}' does not exist"
            
            stat = filepath.stat()
            
            info = [
                f"File: {filename}",
                f"Path: {filepath}",
                f"Size: {stat.st_size} bytes",
                f"Created: {datetime.fromtimestamp(stat.st_ctime)}",
                f"Modified: {datetime.fromtimestamp(stat.st_mtime)}",
                f"Type: {'Directory' if filepath.is_dir() else 'File'}"
            ]
            
            return "\n".join(info)
            
        except Exception as e:
            return f"Error getting file info: {str(e)}"
    
    def parse_tool_calls(self, text):
        """Parse tool calls from AI response"""
        import re
        
        # Pattern: [TOOL:tool_name:param1:param2:...]
        pattern = r'\[TOOL:([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, text)
        
        tool_calls = []
        for tool_name, params in matches:
            tool_name = tool_name.strip()
            
            # Parse parameters (support for multi-part params)
            param_parts = params.split(':', 1)  # Split only on first : for write_file
            
            if tool_name in self.available_tools:
                tool_calls.append({
                    'tool': tool_name,
                    'params': param_parts,
                    'raw': f"[TOOL:{tool_name}:{params}]"
                })
        
        return tool_calls
    
    def execute_tool(self, tool_name, params):
        """Execute a tool with given parameters"""
        if tool_name not in self.available_tools:
            return f"Unknown tool: {tool_name}"
        
        tool_func = self.available_tools[tool_name]
        
        try:
            # Call the tool with unpacked parameters
            result = tool_func(*params)
            return result
        except TypeError as e:
            return f"Tool '{tool_name}' called with incorrect parameters: {str(e)}"
        except Exception as e:
            return f"Tool execution error: {str(e)}"    
    def _try_brave_search(self, query):
        """Try Brave Search API (free tier, might not be blocked)"""
        try:
            # Brave Search has a generous free tier
            search_url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            params = {'q': query, 'count': 5}
            
            print(f"[Brave Search] Attempting...")
            response = self.session.get(search_url, headers=headers, params=params, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for i, result in enumerate(data.get('web', {}).get('results', [])[:5], 1):
                    title = result.get('title', '')
                    description = result.get('description', '')
                    url = result.get('url', '')
                    
                    if title and description:
                        results.append(f"{i}. {title}\\n   {description}\\n   Source: {url}\\n")
                
                if results:
                    print(f"[Brave Search] Found {len(results)} results")
                    return f"Search results for '{query}':\\n\\n" + "\\n".join(results)
                    
        except Exception as e:
            print(f"[Brave Search] Failed: {str(e)}")
        
        return None
    
    def _try_http_fallback(self, query):
        """Try HTTP (not HTTPS) as last resort - some networks block HTTPS inspection"""
        try:
            # Try accessing a simple HTTP-only search service
            search_url = f"http://www.google.com/search?q={urllib.parse.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            print(f"[HTTP Fallback] Trying plain HTTP...")
            
            # Use urllib for HTTP
            req = urllib.request.Request(search_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    html_content = response.read().decode('utf-8', errors='ignore')
                    
                    # Basic parsing - look for search result snippets
                    if '<div' in html_content and len(html_content) > 1000:
                        print(f"[HTTP Fallback] Got response, parsing...")
                        # Very basic extraction - just confirm we got something
                        return f"Search connection successful for '{query}'. Basic HTML parsing available but blocked by network restrictions. Results available but cannot be fully parsed."
                        
        except Exception as e:
            print(f"[HTTP Fallback] Failed: {str(e)}")
        
        return None