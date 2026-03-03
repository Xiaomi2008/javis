"""Tests for memory module."""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile

from javis.memory import MemoryManager, MemoryEntry


class TestMemoryManager:
    """Test MemoryManager functionality."""
    
    def test_init_creates_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mm = MemoryManager(Path(tmpdir))
            assert mm.memory_dir.exists()
            assert mm.daily_dir.exists()
    
    def test_remember_creates_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mm = MemoryManager(Path(tmpdir))
            entry = mm.remember("Test content", category="test")
            
            assert entry.content == "Test content"
            assert entry.category == "test"
            
            # Verify it was stored
            daily = mm.read_daily()
            assert "Test content" in daily
    
    def test_search_finds_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mm = MemoryManager(Path(tmpdir))
            mm.remember("Python is great", category="code")
            mm.remember("JavaScript is also good", category="code")
            
            results = mm.search("Python")
            assert len(results) >= 1
            
            found_python = any("Python" in r[1].content for r in results)
            assert found_python


class TestMemoryEntry:
    """Test MemoryEntry functionality."""
    
    def test_to_dict_roundtrip(self):
        entry = MemoryEntry(
            content="Test",
            category="test",
            tags=["a", "b"],
            important=True,
        )
        
        data = entry.to_dict()
        restored = MemoryEntry.from_dict(data)
        
        assert restored.content == entry.content
        assert restored.category == entry.category
        assert restored.tags == entry.tags
        assert restored.important == entry.important
