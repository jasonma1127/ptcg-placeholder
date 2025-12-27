"""
Configuration settings for the Pokemon card generator.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class CardSettings:
    """Settings for Pokemon card design."""
    width_mm: float = 63.0
    height_mm: float = 88.0
    dpi: int = 300
    background_color: str = "white"
    border_width: int = 2
    border_color: str = "black"
    image_padding_mm: float = 5.0
    text_height_mm: float = 10.0
    text_padding_mm: float = 2.0

    @property
    def width_pixels(self) -> int:
        """Calculate card width in pixels."""
        return int((self.width_mm / 25.4) * self.dpi)

    @property
    def height_pixels(self) -> int:
        """Calculate card height in pixels."""
        return int((self.height_mm / 25.4) * self.dpi)

    @property
    def image_padding_pixels(self) -> int:
        """Calculate image padding in pixels."""
        return int((self.image_padding_mm / 25.4) * self.dpi)

    @property
    def text_height_pixels(self) -> int:
        """Calculate text area height in pixels."""
        return int((self.text_height_mm / 25.4) * self.dpi)


@dataclass
class APISettings:
    """Settings for PokeAPI integration."""
    base_url: str = "https://pokeapi.co/api/v2"
    cache_duration_hours: int = 24
    max_retries: int = 3
    timeout_seconds: int = 30
    rate_limit_delay: float = 0.1  # Seconds between requests


@dataclass
class PDFSettings:
    """Settings for PDF generation."""
    page_size: str = "A4"  # (210x297mm)
    margin_mm: float = 5.0
    card_spacing_mm: float = 2.0
    cards_per_row: int = 3
    cards_per_column: int = 3

    @property
    def cards_per_page(self) -> int:
        """Calculate total cards per page."""
        return self.cards_per_row * self.cards_per_column


@dataclass
class FontSettings:
    """Font settings for different languages."""
    default_font_size: int = 16
    font_paths: Dict[str, str] = None

    def __post_init__(self):
        if self.font_paths is None:
            self.font_paths = {
                'en': 'fonts/arial.ttf',
                'zh-Hant': 'fonts/noto-sans-tc.ttf',
                'ja': 'fonts/noto-sans-jp.ttf',
            }


@dataclass
class AppSettings:
    """Main application settings container."""
    card: CardSettings = None
    api: APISettings = None
    pdf: PDFSettings = None
    font: FontSettings = None

    def __post_init__(self):
        if self.card is None:
            self.card = CardSettings()
        if self.api is None:
            self.api = APISettings()
        if self.pdf is None:
            self.pdf = PDFSettings()
        if self.font is None:
            self.font = FontSettings()


# Global settings instance
settings = AppSettings()