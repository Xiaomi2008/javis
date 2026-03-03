"""Tool execution and web capabilities for Javis."""

import os
import re
import json
import subprocess
import urllib.parse
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import requests


@dataclass
class ExecResult:
    """Result of a shell command execution."""
    
    stdout: str
    stderr: str
    returncode: int
    
    @property
    def success(self) -> bool:
        """Check if command succeeded."""
        return self.returncode == 0
    
    def __str__(self) -> str:
        """String representation."""
        output = self.stdout
        if self.stderr:
            output += f"\n[stderr]:\n{self.stderr}"
        return output


@dataclass
class SearchResult:
    """Web search result."""
    
    title: str
    url: str
    snippet: str
    source: str = "web"


@dataclass
class WebContent:
    """Fetched web content."""
    
    url: str
    title: str
    content: str
    content_type: str


class ToolExecutor:
    """Execute shell commands safely."""
    
    def __init__(self, max_output: int = 50000, default_timeout: int = 60):
        self.max_output = max_output
        self.default_timeout = default_timeout
    
    def exec(self, command: str, cwd: Optional[str] = None, 
             env: Optional[Dict[str, str]] = None,
             timeout: Optional[int] = None,
             pty: bool = False) -> ExecResult:
        """
        Execute a shell command.
        
        Args:
            command: Shell command to execute
            cwd: Working directory
            env: Environment variables
            timeout: Timeout in seconds
            pty: Run in pseudo-terminal (for interactive commands)
        
        Returns:
            ExecResult with stdout, stderr, and return code
        """
        try:
            # Use shell=True for command line features
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                env=env if env else None,
                timeout=timeout or self.default_timeout,
            )
            
            stdout = result.stdout[:self.max_output] if result.stdout else ""
            stderr = result.stderr[:self.max_output] if result.stderr else ""
            
            return ExecResult(
                stdout=stdout,
                stderr=stderr,
                returncode=result.returncode,
            )
            
        except subprocess.TimeoutExpired:
            return ExecResult(
                stdout=f"",
                stderr=f"Command timed out after {timeout or self.default_timeout} seconds",
                returncode=-1,
            )
        except Exception as e:
            return ExecResult(
                stdout="",
                stderr=f"Error executing command: {str(e)}",
                returncode=-1,
            )
    
    def run_background(self, command: str, cwd: Optional[str] = None,
                       env: Optional[Dict[str, str]] = None) -> int:
        """
        Run a command in the background.
        
        Returns:
            Process ID (PID) of the background process
        """
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=cwd,
            env=env if env else None,
        )
        return process.pid


class WebTools:
    """Web search and fetch capabilities."""
    
    def __init__(self, brave_api_key: Optional[str] = None, 
                 search_count: int = 10):
        self.brave_api_key = brave_api_key
        self.search_count = search_count
        
        # Default headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search(self, query: str, count: Optional[int] = None,
               country: str = "US", language: str = "en") -> List[SearchResult]:
        """
        Search the web using Brave Search API.
        
        Args:
            query: Search query
            count: Number of results (default: config.search_count)
            country: 2-letter country code
            language: Language code
        
        Returns:
            List of SearchResult objects
        """
        if not self.brave_api_key:
            # Fallback: just return empty list with info
            return [SearchResult(
                title="Search unavailable",
                url="",
                snippet="BRAVE_API_KEY not configured. Set env var or config to enable search."
            )]
        
        try:
            params = {
                'q': query,
                'count': count or self.search_count,
                'country': country,
                'search_lang': language,
            }
            
            headers = {
                'Accept': 'application/json',
                'X-Subscription-Token': self.brave_api_key,
            }
            
            response = requests.get(
                'https://api.search.brave.com/res/v1/web/search',
                params=params,
                headers=headers,
                timeout=30,
            )
            
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('web', {}).get('results', []):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    snippet=item.get('description', ''),
                    source='brave',
                ))
            
            return results
            
        except Exception as e:
            return [SearchResult(
                title="Search failed",
                url="",
                snippet=f"Error: {str(e)}"
            )]
    
    def fetch(self, url: str, extract_mode: str = "markdown",
              max_chars: int = 10000) -> WebContent:
        """
        Fetch and extract content from a URL.
        
        Args:
            url: URL to fetch
            extract_mode: 'markdown' or 'text'
            max_chars: Maximum characters to return
        
        Returns:
            WebContent with extracted content
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', 'text/html')
            
            if '/html' in content_type:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get title
                title = soup.title.string if soup.title else url
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get main content
                # Try to find main content area
                main = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
                if main:
                    text = main.get_text(separator='\n', strip=True)
                else:
                    text = soup.get_text(separator='\n', strip=True)
                
                # Clean up
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                text = '\n'.join(lines)
                
                if extract_mode == "markdown":
                    # Convert links to markdown
                    text = self._links_to_markdown(text, soup)
                
            elif '/json' in content_type:
                title = url
                text = json.dumps(json.loads(response.text), indent=2)
            else:
                title = url
                text = response.text[:max_chars]
            
            return WebContent(
                url=url,
                title=title[:100],
                content=text[:max_chars],
                content_type=content_type,
            )
            
        except ImportError:
            return WebContent(
                url=url,
                title="Error",
                content="BeautifulSoup not installed. Install with: pip install beautifulsoup4",
                content_type="text/plain",
            )
        except Exception as e:
            return WebContent(
                url=url,
                title="Error",
                content=f"Failed to fetch {url}: {str(e)}",
                content_type="text/plain",
            )
    
    def _links_to_markdown(self, text: str, soup) -> str:
        """Convert HTML links to markdown format."""
        # Simple version - just return text for now
        return text


class FileTools:
    """File operations."""
    
    def read(self, path: str, offset: int = 0, limit: Optional[int] = None) -> str:
        """
        Read file contents.
        
        Args:
            path: File path
            offset: Line number to start from (1-indexed)
            limit: Maximum lines to read
        
        Returns:
            File contents as string
        """
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not file_path.is_file():
            raise ValueError(f"Not a file: {path}")
        
        content = file_path.read_text()
        
        if offset > 0 or limit:
            lines = content.split('\n')
            if offset > 0:
                lines = lines[offset - 1:]
            if limit:
                lines = lines[:limit]
            content = '\n'.join(lines)
        
        return content
    
    def write(self, path: str, content: str) -> None:
        """Write content to file."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
    
    def edit(self, path: str, old_text: str, new_text: str) -> None:
        """
        Edit file by replacing exact text.
        
        Args:
            path: File to edit
            old_text: Exact text to find
            new_text: Text to replace with
        """
        content = self.read(path)
        
        if old_text not in content:
            raise ValueError(f"old_text not found in file: {old_text[:50]}...")
        
        new_content = content.replace(old_text, new_text, 1)
        self.write(path, new_content)
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return Path(path).exists()
    
    def list_dir(self, path: str, pattern: str = "*") -> List[str]:
        """List directory contents."""
        dir_path = Path(path)
        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {path}")
        
        return [str(p) for p in sorted(dir_path.glob(pattern))]
