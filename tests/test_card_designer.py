"""Tests for card designer module."""
import pytest
from pathlib import Path
from PIL import Image
from src.card.card_designer import CardDesigner
from src.models import PokemonData


@pytest.fixture
def card_designer():
    """Create CardDesigner instance."""
    return CardDesigner()


@pytest.fixture
def sample_pokemon():
    """Create sample Pokemon data."""
    from src.models import PokemonBasicData, PokemonType

    # Create basic Pokemon data
    basic = PokemonBasicData(
        id=25,
        name="pikachu",
        height=4,  # in decimeters
        weight=60,  # in hectograms
        types=[
            PokemonType(
                slot=1,
                type={"name": "electric", "url": "https://pokeapi.co/api/v2/type/13/"}
            )
        ]
    )

    return PokemonData(
        basic=basic,
        names={"en": "Pikachu", "ja": "ピカチュウ", "zh-Hant": "皮卡丘"},
        official_artwork_url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
    )


def test_card_designer_initialization(card_designer):
    """Test CardDesigner initializes correctly."""
    assert card_designer is not None
    assert card_designer.card_width > 0
    assert card_designer.card_height > 0


def test_create_card_basic(card_designer, sample_pokemon, tmp_path):
    """Test basic card creation."""
    # Create a dummy image for testing
    dummy_image = Image.new('RGBA', (100, 100), (255, 255, 255, 255))
    image_path = tmp_path / "test_pokemon.png"
    dummy_image.save(image_path)

    # Generate card
    card = card_designer.create_card(sample_pokemon, image_path, language='en')

    # Verify card properties
    assert isinstance(card, Image.Image)
    assert card.mode == 'RGBA'
    assert card.size == (card_designer.card_width, card_designer.card_height)


def test_create_card_with_dpi(card_designer, sample_pokemon, tmp_path):
    """Test card has correct DPI metadata."""
    dummy_image = Image.new('RGBA', (100, 100), (255, 255, 255, 255))
    image_path = tmp_path / "test_pokemon.png"
    dummy_image.save(image_path)

    card = card_designer.create_card(sample_pokemon, image_path, language='en')

    # Check DPI is set
    assert 'dpi' in card.info
    assert card.info['dpi'] == (300, 300)


def test_create_card_multilanguage(card_designer, sample_pokemon, tmp_path):
    """Test card creation with multiple languages."""
    dummy_image = Image.new('RGBA', (100, 100), (255, 255, 255, 255))
    image_path = tmp_path / "test_pokemon.png"
    dummy_image.save(image_path)

    # Test card creation with different languages
    for language in ['en', 'ja', 'zh-Hant']:
        card = card_designer.create_card(sample_pokemon, image_path, language=language)
        assert isinstance(card, Image.Image)
        assert card.size == (card_designer.card_width, card_designer.card_height)


def test_card_dimensions(card_designer):
    """Test card has correct physical dimensions at 300 DPI."""
    # Card should be 63x88mm at 300 DPI
    expected_width_px = int(63 * 300 / 25.4)  # mm to pixels at 300 DPI
    expected_height_px = int(88 * 300 / 25.4)

    assert abs(card_designer.card_width - expected_width_px) <= 2  # Allow 2px tolerance
    assert abs(card_designer.card_height - expected_height_px) <= 2
