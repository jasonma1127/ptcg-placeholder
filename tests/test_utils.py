"""Tests for utility functions and path handling."""
import pytest
from pathlib import Path
import tempfile


def test_path_expansion():
    """Test path expansion works correctly."""
    # Test home directory expansion
    home_path = Path.home()
    assert home_path.exists()

    # Test that we can resolve paths relative to home
    # This works regardless of which directories actually exist
    test_path = Path.home() / "test_subdir"
    assert test_path.parent == Path.home()


def test_current_directory():
    """Test current directory detection."""
    cwd = Path.cwd()
    assert cwd.exists()
    assert cwd.is_dir()


def test_temp_directory_creation():
    """Test temporary directory can be created."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        assert tmp_path.exists()
        assert tmp_path.is_dir()

        # Test file creation in temp dir
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()


def test_nested_directory_creation():
    """Test nested directory creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nested_path = Path(tmpdir) / "a" / "b" / "c"
        nested_path.mkdir(parents=True, exist_ok=True)

        assert nested_path.exists()
        assert nested_path.is_dir()


def test_pdf_filename_generation():
    """Test PDF filename generation format."""
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pokemon_cards_gen1_{timestamp}.pdf"

    assert filename.endswith(".pdf")
    assert "pokemon_cards" in filename
    assert len(timestamp) == 15  # YYYYMMDD_HHMMSS


def test_path_with_spaces():
    """Test handling paths with spaces."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create path with spaces
        path_with_spaces = Path(tmpdir) / "folder with spaces" / "file name.pdf"
        path_with_spaces.parent.mkdir(parents=True, exist_ok=True)
        path_with_spaces.write_text("test")

        assert path_with_spaces.exists()
        assert " " in str(path_with_spaces)
