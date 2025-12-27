"""Tests for PDF generator module."""
import pytest
from pathlib import Path
from PIL import Image
from src.pdf.pdf_generator import PDFGenerator


@pytest.fixture
def pdf_generator():
    """Create PDFGenerator instance."""
    return PDFGenerator()


@pytest.fixture
def sample_cards():
    """Create sample card images."""
    cards = []
    for i in range(3):
        card = Image.new('RGBA', (744, 1039), (255, 255, 255, 255))
        card.info['dpi'] = (300, 300)
        cards.append(card)
    return cards


def test_pdf_generator_initialization(pdf_generator):
    """Test PDFGenerator initializes correctly."""
    assert pdf_generator is not None
    # Check that page_layout is initialized
    assert pdf_generator.page_layout is not None


def test_generate_pdf_basic(pdf_generator, sample_cards, tmp_path):
    """Test basic PDF generation."""
    output_path = tmp_path / "test_cards.pdf"

    metadata = {
        'title': 'Test Pokemon Cards',
        'language': 'en',
        'total_cards': len(sample_cards)
    }

    result = pdf_generator.generate_cards_pdf(sample_cards, str(output_path), metadata)

    # Verify PDF was created
    assert output_path.exists()
    assert result.total_cards == 3
    assert result.total_pages >= 1
    assert result.file_size_mb > 0


def test_pdf_file_size(pdf_generator, sample_cards, tmp_path):
    """Test PDF file size is reasonable."""
    output_path = tmp_path / "test_cards.pdf"

    result = pdf_generator.generate_cards_pdf(sample_cards, str(output_path), {})

    # PDF should exist and have reasonable size (not too small, not too large)
    assert output_path.stat().st_size > 1000  # At least 1KB
    assert output_path.stat().st_size < 50 * 1024 * 1024  # Less than 50MB


def test_pdf_cards_per_page(pdf_generator, sample_cards, tmp_path):
    """Test correct number of cards per page."""
    output_path = tmp_path / "test_cards.pdf"

    result = pdf_generator.generate_cards_pdf(sample_cards, str(output_path), {})

    # Should have 9 cards per page
    assert result.cards_per_page == 9


def test_pdf_with_many_cards(pdf_generator, tmp_path):
    """Test PDF generation with multiple pages."""
    # Create 20 cards (should be 3 pages with 9 cards per page)
    cards = []
    for i in range(20):
        card = Image.new('RGBA', (744, 1039), (255, 255, 255, 255))
        card.info['dpi'] = (300, 300)
        cards.append(card)

    output_path = tmp_path / "test_many_cards.pdf"
    result = pdf_generator.generate_cards_pdf(cards, str(output_path), {})

    assert result.total_cards == 20
    assert result.total_pages == 3  # ceil(20 / 9) = 3


def test_pdf_output_path_creation(pdf_generator, sample_cards, tmp_path):
    """Test PDF creates parent directories if needed."""
    output_path = tmp_path / "subdir" / "nested" / "test.pdf"

    result = pdf_generator.generate_cards_pdf(sample_cards, str(output_path), {})

    assert output_path.exists()
    assert result.total_cards == 3
