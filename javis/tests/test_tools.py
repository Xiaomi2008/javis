"""Tests for tools module."""

import pytest
from pathlib import Path
import tempfile

from javis.tools import ToolExecutor, FileTools


class TestToolExecutor:
    """Test ToolExecutor functionality."""
    
    def test_exec_success(self):
        executor = ToolExecutor()
        result = executor.exec("echo 'Hello World'")
        
        assert result.success
        assert "Hello World" in result.stdout
        assert result.returncode == 0
    
    def test_exec_failure(self):
        executor = ToolExecutor()
        result = executor.exec("exit 1")
        
        assert not result.success
        assert result.returncode == 1


class TestFileTools:
    """Test FileTools functionality."""
    
    def test_write_and_read(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ft = FileTools()
            path = Path(tmpdir) / "test.txt"
            
            ft.write(str(path), "Hello World")
            content = ft.read(str(path))
            
            assert content == "Hello World"
    
    def test_edit_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ft = FileTools()
            path = Path(tmpdir) / "test.txt"
            
            ft.write(str(path), "Hello World")
            ft.edit(str(path), "World", "Universe")
            content = ft.read(str(path))
            
            assert content == "Hello Universe"
    
    def test_read_nonexistent_file(self):
        ft = FileTools()
        
        with pytest.raises(FileNotFoundError):
            ft.read("/definitely/does/not/exist.txt")
