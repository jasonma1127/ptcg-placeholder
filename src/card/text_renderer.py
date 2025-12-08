"""
Text rendering utilities for Pokemon cards.
Handles multi-language text rendering with appropriate fonts.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
import platform

from src.utils.error_handler import FontNotFoundError, log_error
from config.settings import settings
from config.constants import FONT_CONFIG, FALLBACK_FONTS


class TextRenderer:
    """Text renderer with multi-language font support."""

    def __init__(self):
        self.font_cache: Dict[str, ImageFont.FreeTypeFont] = {}
        self.default_font_size = settings.font.default_font_size
        self._init_font_paths()

    def _init_font_paths(self):
        """Initialize font paths for different platforms."""
        self.system_font_paths = []

        system = platform.system()
        if system == "Windows":
            self.system_font_paths = [
                "C:/Windows/Fonts/",
                "C:/Windows/System32/Fonts/"
            ]
        elif system == "Darwin":  # macOS
            self.system_font_paths = [
                "/Library/Fonts/",
                "/System/Library/Fonts/",
                "/Users/" + str(Path.home().name) + "/Library/Fonts/"
            ]
        else:  # Linux
            self.system_font_paths = [
                "/usr/share/fonts/",
                "/usr/local/share/fonts/",
                str(Path.home()) + "/.fonts/"
            ]

    def get_font(self, language: str = 'en', size: int = None, style: str = 'regular') -> ImageFont.FreeTypeFont:
        """
        Get appropriate font for language and style.

        Args:
            language: Language code ('en', 'zh-Hant', 'ja')
            size: Font size (uses default if None)
            style: Font style ('regular', 'bold', 'italic')

        Returns:
            PIL ImageFont object
        """
        if size is None:
            size = self.default_font_size

        # Create cache key
        cache_key = f"{language}_{size}_{style}"

        # Check cache first
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        # Try to load font
        font = self._load_font_for_language(language, size, style)

        # Cache the font
        self.font_cache[cache_key] = font

        return font

    def _load_font_for_language(self, language: str, size: int, style: str) -> ImageFont.FreeTypeFont:
        """Load font for specific language."""
        # Try project fonts first
        font = self._try_project_font(language, size, style)
        if font and self._test_font_can_render(font, language):
            return font

        # Try system fonts
        font = self._try_system_fonts(language, size, style)
        if font and self._test_font_can_render(font, language):
            return font

        # Enhanced fallback for Chinese and Japanese
        if language in ['zh-Hant', 'ja']:
            font = self._try_enhanced_cjk_fonts(language, size, style)
            if font:
                return font

        # Fallback to default font
        log_error(FontNotFoundError(language, "No suitable font found"), "WARNING")
        return self._get_default_font(size)

    def _try_project_font(self, language: str, size: int, style: str) -> Optional[ImageFont.FreeTypeFont]:
        """Try to load font from project fonts directory."""
        if language not in FONT_CONFIG:
            return None

        font_path = Path(FONT_CONFIG[language])

        # Modify path for style
        if style == 'bold':
            font_path = font_path.with_name(font_path.stem + '-Bold' + font_path.suffix)
        elif style == 'italic':
            font_path = font_path.with_name(font_path.stem + '-Italic' + font_path.suffix)

        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except Exception as e:
                log_error(FontNotFoundError(language, str(e)), "WARNING")

        return None

    def _try_system_fonts(self, language: str, size: int, style: str) -> Optional[ImageFont.FreeTypeFont]:
        """Try to load system fonts."""
        if language not in FALLBACK_FONTS:
            return None

        fallback_fonts = FALLBACK_FONTS[language]

        for font_name in fallback_fonts:
            font = self._try_system_font(font_name, size, style)
            if font:
                return font

        return None

    def _try_system_font(self, font_name: str, size: int, style: str) -> Optional[ImageFont.FreeTypeFont]:
        """Try to load a specific system font."""
        # First try loading font directly by name (works best on macOS)
        try:
            return ImageFont.truetype(font_name, size)
        except Exception:
            pass

        # Common font file extensions
        extensions = ['.ttf', '.otf', '.ttc']

        # Style modifiers
        style_modifiers = {
            'bold': ['-Bold', '_Bold', ' Bold', 'Bold'],
            'italic': ['-Italic', '_Italic', ' Italic', 'Italic'],
            'regular': ['', '-Regular', '_Regular', ' Regular']
        }

        modifiers = style_modifiers.get(style, [''])

        # Try loading from system font paths
        for path_dir in self.system_font_paths:
            path = Path(path_dir)
            if not path.exists():
                continue

            for modifier in modifiers:
                for ext in extensions:
                    font_file = path / f"{font_name}{modifier}{ext}"
                    if font_file.exists():
                        try:
                            return ImageFont.truetype(str(font_file), size)
                        except Exception:
                            continue

        return None

    def _test_font_can_render(self, font: ImageFont.FreeTypeFont, language: str) -> bool:
        """Test if a font can properly render text in the given language."""
        # Test characters for each language
        test_chars = {
            'en': 'ABCabc123',
            'zh-Hant': '妙蛙種子皮卡丘',
            'ja': 'フシギダネピカチュウ'
        }

        test_text = test_chars.get(language, 'ABC')

        try:
            # Try to measure the text - if font doesn't support the characters,
            # this should still work but might use fallback glyphs
            dummy_img = Image.new('RGB', (100, 100))
            draw = ImageDraw.Draw(dummy_img)
            bbox = draw.textbbox((0, 0), test_text, font=font)

            # A very simple check: if width is 0, font probably can't render
            width = bbox[2] - bbox[0]
            return width > 0

        except Exception:
            return False

    def _try_enhanced_cjk_fonts(self, language: str, size: int, style: str) -> Optional[ImageFont.FreeTypeFont]:
        """Enhanced CJK (Chinese/Japanese/Korean) font loading."""
        # Comprehensive list of CJK fonts on macOS
        cjk_fonts = [
            # Primary Chinese fonts
            "PingFang TC",  # Modern Chinese font
            "PingFang SC",
            "STHeiti",
            "STHeiti Light",
            "STHeiti Medium",
            "Hiragino Sans GB",
            "Hiragino Sans CNS",

            # Primary Japanese fonts
            "Hiragino Sans",
            "Hiragino Kaku Gothic Pro",
            "Hiragino Kaku Gothic ProN",
            "Yu Gothic",
            "Yu Gothic Medium",
            "AppleGothic",

            # Universal CJK fonts
            "Arial Unicode MS",
            "Microsoft JhengHei",
            "Microsoft YaHei",
            "SimHei",
            "SimSun"
        ]

        for font_name in cjk_fonts:
            font = self._try_system_font(font_name, size, style)
            if font and self._test_font_can_render(font, language):
                return font

        return None

    def _get_default_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get default PIL font with better system font support."""
        # Try common system fonts in order of preference
        font_candidates = [
            "arial.ttf",  # Windows
            "Arial.ttf",  # macOS
            "/System/Library/Fonts/Arial.ttf",  # macOS system path
            "/System/Library/Fonts/Helvetica.ttc",  # macOS system fallback
            "DejaVu Sans",  # Linux
            "Liberation Sans"  # Linux
        ]

        for font_name in font_candidates:
            try:
                return ImageFont.truetype(font_name, size)
            except:
                continue

        # Ultimate fallback - PIL default font (bitmap, limited sizes)
        return ImageFont.load_default()

    def measure_text(self, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """Measure text dimensions."""
        # Create a dummy image for measuring
        dummy_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_img)

        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        return width, height

    def fit_text_to_width(self, text: str, max_width: int, language: str = 'en',
                         min_size: int = 8, max_size: int = 24) -> Tuple[str, ImageFont.FreeTypeFont]:
        """
        Find the best font size to fit text within width.

        Returns:
            Tuple of (possibly wrapped text, font)
        """
        # Binary search for optimal font size
        low, high = min_size, max_size
        best_font = self.get_font(language, min_size)
        best_text = text

        while low <= high:
            mid_size = (low + high) // 2
            font = self.get_font(language, mid_size)

            # Try original text first
            width, _ = self.measure_text(text, font)

            if width <= max_width:
                best_font = font
                best_text = text
                low = mid_size + 1
            else:
                # Try text wrapping
                wrapped_text = self._wrap_text(text, max_width, font)
                if wrapped_text:
                    best_font = font
                    best_text = wrapped_text
                    low = mid_size + 1
                else:
                    high = mid_size - 1

        return best_text, best_font

    def _wrap_text(self, text: str, max_width: int, font: ImageFont.FreeTypeFont) -> Optional[str]:
        """Wrap text to fit within width."""
        words = text.split()
        if len(words) <= 1:
            return None

        lines = []
        current_line = []

        for word in words:
            test_line = current_line + [word]
            test_text = ' '.join(test_line)
            width, _ = self.measure_text(test_text, font)

            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word too long
                    return None

        if current_line:
            lines.append(' '.join(current_line))

        # Limit to 2 lines for card names
        if len(lines) <= 2:
            return '\n'.join(lines)

        return None

    def add_text_to_card(self, card: Image.Image, text: str, text_area: Dict[str, int],
                        language: str = 'en', font_size: int = None, style: str = 'regular',
                        color: str = 'black', align: str = 'left') -> Image.Image:
        """
        Add text to a card image within specified area.

        Args:
            card: PIL Image to draw on
            text: Text to draw
            text_area: Dict with x, y, width, height
            language: Language for font selection
            font_size: Font size (auto-fit if None)
            style: Font style
            color: Text color
            align: Text alignment ('left', 'center', 'right')

        Returns:
            Modified card image
        """
        draw = ImageDraw.Draw(card)

        if font_size:
            # Use specified font size
            font = self.get_font(language, font_size, style)
            final_text = text
        else:
            # Auto-fit text to area
            final_text, font = self.fit_text_to_width(
                text, text_area['width'], language
            )

        # Calculate position based on alignment
        lines = final_text.split('\n')
        line_height = self.measure_text('Ay', font)[1] + 2  # Add small line spacing

        # Calculate total text height
        total_height = len(lines) * line_height

        # Vertical centering
        start_y = text_area['y'] + (text_area['height'] - total_height) // 2

        # Draw each line
        for i, line in enumerate(lines):
            line_width, _ = self.measure_text(line, font)

            # Horizontal alignment
            if align == 'center':
                x = text_area['x'] + (text_area['width'] - line_width) // 2
            elif align == 'right':
                x = text_area['x'] + text_area['width'] - line_width
            else:  # left
                x = text_area['x']

            y = start_y + (i * line_height)

            # Add text shadow for better readability
            shadow_color = 'white' if color == 'black' else 'black'
            draw.text((x + 1, y + 1), line, font=font, fill=shadow_color)
            draw.text((x, y), line, font=font, fill=color)

        return card

    def add_outlined_text(self, card: Image.Image, text: str, x: int, y: int,
                         font: ImageFont.FreeTypeFont, fill_color: str = 'white',
                         outline_color: str = 'black', outline_width: int = 2) -> Image.Image:
        """Add text with outline for better visibility."""
        draw = ImageDraw.Draw(card)

        # Draw outline
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)

        # Draw main text
        draw.text((x, y), text, font=font, fill=fill_color)

        return card

    def get_text_dimensions(self, text: str, language: str = 'en',
                          font_size: int = None, style: str = 'regular') -> Tuple[int, int]:
        """Get dimensions of text with specified parameters."""
        if font_size is None:
            font_size = self.default_font_size

        font = self.get_font(language, font_size, style)
        return self.measure_text(text, font)

    def clear_font_cache(self):
        """Clear the font cache to free memory."""
        self.font_cache.clear()


# Global text renderer instance
text_renderer = TextRenderer()