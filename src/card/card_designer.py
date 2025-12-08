"""
Pokemon card designer - creates the visual layout and design of cards.
"""

from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io

from src.models import PokemonData, CardData
from src.utils.error_handler import (
    ImageDownloadError, FontNotFoundError,
    handle_errors, log_error, create_error_context
)
from src.card.text_renderer import TextRenderer
from src.utils.type_icon_manager import type_icon_manager
from config.settings import settings
from config.constants import FONT_CONFIG, FALLBACK_FONTS


class CardDesigner:
    """Main card designer for creating Pokemon cards."""

    def __init__(self):
        self.card_width = settings.card.width_pixels
        self.card_height = settings.card.height_pixels
        self.background_color = settings.card.background_color
        self.border_width = settings.card.border_width
        self.border_color = settings.card.border_color
        self.image_padding = settings.card.image_padding_pixels
        self.text_height = settings.card.text_height_pixels
        self.text_renderer = TextRenderer()

    @create_error_context("create Pokemon card")
    def create_card(self, pokemon_data: PokemonData, image_path: Path, language: str = 'en') -> Image.Image:
        """
        Create a complete Pokemon card image.

        Args:
            pokemon_data: Complete Pokemon data
            image_path: Path to Pokemon image
            language: Language for Pokemon name

        Returns:
            PIL Image object of the completed card
        """
        # Create base card
        card = self._create_base_card()

        # Add Pokemon image
        card = self._add_pokemon_image(card, image_path)

        # Add Pokemon name
        card = self._add_pokemon_name(card, pokemon_data, language)

        # Add decorative elements
        card = self._add_decorative_elements(card, pokemon_data)

        # Add border
        card = self._add_border(card)

        return card

    def _create_base_card(self) -> Image.Image:
        """Create the base card with background."""
        card = Image.new('RGBA', (self.card_width, self.card_height), self.background_color)

        # Add subtle gradient background
        card = self._add_gradient_background(card)

        return card

    def _add_gradient_background(self, card: Image.Image) -> Image.Image:
        """Add a subtle gradient background to the card."""
        # Create gradient from light gray to white
        gradient = Image.new('RGBA', (self.card_width, self.card_height))
        draw = ImageDraw.Draw(gradient)

        for y in range(self.card_height):
            # Calculate gradient intensity (lighter at top)
            intensity = int(255 - (y / self.card_height) * 20)  # Subtle gradient
            color = (intensity, intensity, intensity, 255)
            draw.line([(0, y), (self.card_width, y)], fill=color)

        # Blend with original card
        return Image.alpha_composite(card, gradient)

    def _add_pokemon_image(self, card: Image.Image, image_path: Path) -> Image.Image:
        """Add Pokemon image to the card."""
        try:
            # Load and process Pokemon image
            with Image.open(image_path) as pokemon_img:
                # Convert to RGBA
                if pokemon_img.mode != 'RGBA':
                    pokemon_img = pokemon_img.convert('RGBA')

                # Calculate available space for image
                available_width = self.card_width - (2 * self.image_padding)
                available_height = self.card_height - self.text_height - (2 * self.image_padding)

                # Resize image to fit while maintaining aspect ratio
                pokemon_img = self._resize_with_aspect_ratio(
                    pokemon_img, available_width, available_height
                )

                # Enhance image quality
                pokemon_img = self._enhance_image(pokemon_img)

                # Calculate position to center image both horizontally and vertically
                x_pos = (self.card_width - pokemon_img.width) // 2

                # Center vertically within available image area
                available_image_height = available_height
                y_pos = self.image_padding + (available_image_height - pokemon_img.height) // 2

                # Paste image onto card
                card.paste(pokemon_img, (x_pos, y_pos), pokemon_img)

        except Exception as e:
            log_error(ImageDownloadError(0, str(image_path), f"Could not add Pokemon image: {e}"), "ERROR")
            # Add placeholder if image fails
            card = self._add_image_placeholder(card)

        return card

    def _resize_with_aspect_ratio(self, image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Resize image maintaining aspect ratio."""
        img_ratio = image.width / image.height
        container_ratio = max_width / max_height

        if img_ratio > container_ratio:
            # Image is wider than container
            new_width = max_width
            new_height = int(max_width / img_ratio)
        else:
            # Image is taller than container
            new_height = max_height
            new_width = int(max_height * img_ratio)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Enhance image for better card appearance."""
        # Slightly increase contrast and saturation
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)

        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)

        return image

    def _add_image_placeholder(self, card: Image.Image) -> Image.Image:
        """Add placeholder when Pokemon image is not available."""
        draw = ImageDraw.Draw(card)

        # Calculate placeholder position and size
        available_width = self.card_width - (2 * self.image_padding)
        available_height = self.card_height - self.text_height - (2 * self.image_padding)

        x1 = self.image_padding
        y1 = self.image_padding
        x2 = x1 + available_width
        y2 = y1 + available_height

        # Draw placeholder box
        draw.rectangle([x1, y1, x2, y2], outline="gray", fill="lightgray", width=2)

        # Draw X pattern
        draw.line([x1, y1, x2, y2], fill="gray", width=3)
        draw.line([x1, y2, x2, y1], fill="gray", width=3)

        # Add text
        try:
            # Try to get a font for placeholder text
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        text = "Image not available"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = x1 + (available_width - text_width) // 2
        text_y = y1 + (available_height - text_height) // 2

        draw.text((text_x, text_y), text, fill="gray", font=font)

        return card

    def _add_pokemon_name(self, card: Image.Image, pokemon_data: PokemonData, languages) -> Image.Image:
        """Add Pokemon name(s) to the card in multiple languages."""
        # Handle single language (backward compatibility)
        if isinstance(languages, str):
            languages = [languages]

        # Get names in all requested languages
        names = []
        for lang in languages:
            name = pokemon_data.get_display_name(lang)
            if name and name.strip():  # Only add non-empty names
                names.append((name, lang))

        if not names:
            return card

        # Define text area
        text_y = self.card_height - self.text_height + settings.card.text_padding_mm
        text_area = {
            'x': settings.card.text_padding_mm,
            'y': text_y,
            'width': self.card_width - (2 * settings.card.text_padding_mm),
            'height': self.text_height - settings.card.text_padding_mm
        }

        # Format multi-language text
        if len(names) == 1:
            # Single language - use original formatting
            final_text = names[0][0]
            primary_lang = names[0][1]
            font_size = 48

            # Render single language text
            card = self.text_renderer.add_text_to_card(
                card, final_text, text_area, primary_lang,
                font_size=font_size, style='bold', align='center'
            )
        else:
            # Multiple languages - render each language separately in vertical stack
            base_font_size = 36  # Smaller for multi-language
            line_spacing = 8  # Spacing between language lines

            # Calculate total height needed
            total_languages = len(names)
            total_text_height = (base_font_size * total_languages) + (line_spacing * (total_languages - 1))

            # Calculate starting Y position to center the text block
            start_y = text_area['y'] + (text_area['height'] - total_text_height) // 2

            # Render each language line
            for i, (name, lang) in enumerate(names):
                # Create individual text area for this language
                line_text_area = {
                    'x': text_area['x'],
                    'y': start_y + i * (base_font_size + line_spacing),
                    'width': text_area['width'],
                    'height': base_font_size + line_spacing
                }

                # Render this language line
                card = self.text_renderer.add_text_to_card(
                    card, name, line_text_area, lang,
                    font_size=base_font_size, style='bold', align='center'
                )

        return card

    def _add_decorative_elements(self, card: Image.Image, pokemon_data: PokemonData) -> Image.Image:
        """Add decorative elements like type indicators."""
        # Add small type indicators in corners
        card = self._add_type_indicators(card, pokemon_data)

        # Add Pokemon ID
        card = self._add_pokemon_id(card, pokemon_data.pokemon_id)

        return card

    def _add_type_indicators(self, card: Image.Image, pokemon_data: PokemonData) -> Image.Image:
        """Add type indicator icons to the card."""
        # Ensure type icons are available
        type_icon_manager.ensure_type_icons_cached()

        # Get Pokemon types
        types = pokemon_data.all_types

        # Type indicator settings
        indicator_size = 140  # Increased from 100 to 140 pixels for better visibility
        x_start = self.card_width - indicator_size - 10
        y_start = 10

        for i, type_name in enumerate(types[:2]):  # Max 2 types
            x = x_start - (i * (indicator_size + 5))
            y = y_start

            # Try to load type icon
            type_icon = type_icon_manager.load_type_icon(type_name)

            if type_icon:
                # Scale icon proportionally to fit within indicator_size if needed
                icon_width, icon_height = type_icon.size
                max_size = indicator_size

                if icon_width > max_size or icon_height > max_size:
                    # Scale down proportionally
                    scale_factor = min(max_size / icon_width, max_size / icon_height)
                    new_width = int(icon_width * scale_factor)
                    new_height = int(icon_height * scale_factor)
                    type_icon = type_icon.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Center the icon within the indicator area
                icon_width, icon_height = type_icon.size
                center_x = x + (indicator_size - icon_width) // 2
                center_y = y + (indicator_size - icon_height) // 2

                # Paste type icon on card (handle transparency)
                if type_icon.mode == 'RGBA':
                    card.paste(type_icon, (center_x, center_y), type_icon)
                else:
                    card.paste(type_icon, (center_x, center_y))

            else:
                # Fallback to colored circle if icon not available
                draw = ImageDraw.Draw(card)

                # Fallback type colors
                type_colors = {
                    'normal': '#A8A878', 'fire': '#F08030', 'water': '#6890F0',
                    'electric': '#F8D030', 'grass': '#78C850', 'ice': '#98D8D8',
                    'fighting': '#C03028', 'poison': '#A040A0', 'ground': '#E0C068',
                    'flying': '#A890F0', 'psychic': '#F85888', 'bug': '#A8B820',
                    'rock': '#B8A038', 'ghost': '#705898', 'dragon': '#7038F8',
                    'dark': '#705848', 'steel': '#B8B8D0', 'fairy': '#EE99AC',
                }

                color = type_colors.get(type_name.lower(), '#68A090')
                draw.ellipse([x, y, x + indicator_size, y + indicator_size],
                           fill=color, outline='white', width=3)

                log_error(ImageDownloadError(0, type_name, f"Type icon not available, using fallback"), "WARNING")

        return card

    def _add_pokemon_id(self, card: Image.Image, pokemon_id: int) -> Image.Image:
        """Add Pokemon ID to the card."""
        draw = ImageDraw.Draw(card)

        # Try to get a much larger font for better visibility
        try:
            font = ImageFont.truetype("Arial", 72)
        except:
            try:
                # Fallback to system font path
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 72)
            except:
                # Last resort: use a larger default font size if possible
                try:
                    font = ImageFont.truetype("STHeiti Medium", 72)
                except:
                    font = ImageFont.load_default()

        # Format ID with leading hash
        id_text = f"#{pokemon_id:03d}"

        # Position in top-left corner
        x = 10
        y = 10

        # Add background for better readability
        bbox = draw.textbbox((x, y), id_text, font=font)
        padding = 2
        draw.rectangle([bbox[0] - padding, bbox[1] - padding,
                       bbox[2] + padding, bbox[3] + padding],
                      fill='white', outline='gray')

        # Draw text
        draw.text((x, y), id_text, fill='black', font=font)

        return card

    def _add_border(self, card: Image.Image) -> Image.Image:
        """Add border to the card."""
        if self.border_width <= 0:
            return card

        draw = ImageDraw.Draw(card)

        # Draw border
        for i in range(self.border_width):
            draw.rectangle([i, i, self.card_width - 1 - i, self.card_height - 1 - i],
                          outline=self.border_color, width=1)

        return card

    def create_card_back(self) -> Image.Image:
        """Create a generic card back design."""
        card = Image.new('RGBA', (self.card_width, self.card_height), '#4A90E2')

        draw = ImageDraw.Draw(card)

        # Add pattern
        center_x = self.card_width // 2
        center_y = self.card_height // 2

        # Draw concentric circles
        colors = ['#6BB6FF', '#87CEEB', '#B0E0E6']
        for i, color in enumerate(colors):
            radius = 80 - (i * 20)
            draw.ellipse([center_x - radius, center_y - radius,
                         center_x + radius, center_y + radius],
                        outline=color, width=3)

        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        text = "Pokemon Card"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.card_width - text_width) // 2
        text_y = center_y + 50

        draw.text((text_x, text_y), text, fill='white', font=font)

        # Add border
        return self._add_border(card)

    def optimize_for_print(self, card: Image.Image) -> Image.Image:
        """Optimize card for print quality."""
        # Convert to RGB for printing
        if card.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', card.size, (255, 255, 255))
            background.paste(card, mask=card.split()[-1])  # Use alpha as mask
            card = background
        elif card.mode != 'RGB':
            card = card.convert('RGB')

        return card

    def create_card_batch(self, pokemon_data_list: list, image_paths: dict,
                         language: str = 'en') -> Dict[int, Image.Image]:
        """Create multiple cards in batch."""
        cards = {}

        for pokemon_data in pokemon_data_list:
            pokemon_id = pokemon_data.pokemon_id
            image_path = image_paths.get(pokemon_id)

            if image_path and Path(image_path).exists():
                try:
                    card = self.create_card(pokemon_data, image_path, language)
                    cards[pokemon_id] = card
                except Exception as e:
                    log_error(ImageDownloadError(pokemon_id, str(image_path), str(e)), "ERROR")

        return cards


# Global designer instance
card_designer = CardDesigner()