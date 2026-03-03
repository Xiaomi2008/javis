"""Tests for core Javis class."""

import pytest
from pathlib import Path
import tempfile

from javis import Javis
from javis.config import Config


class TestJavis:
    """Test Javis functionality."""
    
    def test_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(memory_dir=Path(tmpdir) / "memory")
            javis = Javis(config)
            
            assert javis.skills.list_skills()
            assert "echo" in javis.list_skills()
    
    def test_remember(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(memory_dir=Path(tmpdir) / "memory")
            javis = Javis(config)
            
            entry = javis.remember("Test memory")
            assert entry.content == "Test memory"
            
            # Verify recall
            results = javis.recall("Test")
            assert "Test memory" in results or "No memories" in results
    
    def test_file_operations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(memory_dir=Path(tmpdir) / "memory")
            javis = Javis(config)
            
            test_path = Path(tmpdir) / "test.txt"
            javis.write_file(str(test_path), "Hello World")
            
            content = javis.read_file(str(test_path))
            assert content == "Hello World"
            
            assert javis.file_exists(str(test_path))
