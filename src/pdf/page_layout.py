"""
Page layout manager for A4 PDF optimization.
Handles card arrangement and spacing calculations.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4

from config.settings import settings
from config.constants import PDF_CONSTANTS


@dataclass
class LayoutResult:
    """Result of layout calculation."""
    rows: int
    cols: int
    cards_per_page: int
    total_pages: int
    card_width_mm: float
    card_height_mm: float
    spacing_mm: float
    margin_mm: float
    usable_width_mm: float
    usable_height_mm: float


class PageLayoutManager:
    """Manager for calculating optimal card layouts on A4 pages."""

    def __init__(self):
        # A4 dimensions in mm
        self.a4_width_mm = PDF_CONSTANTS['A4_WIDTH_MM']  # 210mm
        self.a4_height_mm = PDF_CONSTANTS['A4_HEIGHT_MM']  # 297mm

        # Card dimensions from settings
        self.card_width_mm = settings.card.width_mm  # 63mm
        self.card_height_mm = settings.card.height_mm  # 88mm

        # PDF settings
        self.margin_mm = settings.pdf.margin_mm  # 10mm
        self.card_spacing_mm = settings.pdf.card_spacing_mm  # 2mm

    def calculate_optimal_layout(self, total_cards: int) -> Dict:
        """
        Calculate optimal layout for cards on A4 pages.

        Args:
            total_cards: Total number of cards to layout

        Returns:
            Dictionary with layout information
        """
        # Calculate usable area
        usable_width = self.a4_width_mm - (2 * self.margin_mm)
        usable_height = self.a4_height_mm - (2 * self.margin_mm)

        # Calculate how many cards fit horizontally and vertically
        cols = self._calculate_cards_per_row(usable_width)
        rows = self._calculate_cards_per_column(usable_height)

        cards_per_page = rows * cols
        total_pages = (total_cards + cards_per_page - 1) // cards_per_page

        # Calculate actual spacing after fitting cards
        actual_h_spacing = self._calculate_actual_horizontal_spacing(usable_width, cols)
        actual_v_spacing = self._calculate_actual_vertical_spacing(usable_height, rows)

        return {
            'rows': rows,
            'cols': cols,
            'cards_per_page': cards_per_page,
            'total_pages': total_pages,
            'usable_width_mm': usable_width,
            'usable_height_mm': usable_height,
            'margin': self.margin_mm * mm,  # Convert to ReportLab units
            'spacing': min(actual_h_spacing, actual_v_spacing) * mm,
            'card_width_mm': self.card_width_mm,
            'card_height_mm': self.card_height_mm,
            'horizontal_spacing_mm': actual_h_spacing,
            'vertical_spacing_mm': actual_v_spacing
        }

    def _calculate_cards_per_row(self, usable_width: float) -> int:
        """Calculate how many cards fit in one row."""
        # Account for spacing between cards
        card_plus_spacing = self.card_width_mm + self.card_spacing_mm

        # Calculate maximum cards (subtract spacing for last card)
        max_cards = int((usable_width + self.card_spacing_mm) // card_plus_spacing)

        # Ensure at least 1 card fits
        return max(1, max_cards)

    def _calculate_cards_per_column(self, usable_height: float) -> int:
        """Calculate how many cards fit in one column."""
        # Account for spacing between cards
        card_plus_spacing = self.card_height_mm + self.card_spacing_mm

        # Calculate maximum cards (subtract spacing for last card)
        max_cards = int((usable_height + self.card_spacing_mm) // card_plus_spacing)

        # Ensure at least 1 card fits
        return max(1, max_cards)

    def _calculate_actual_horizontal_spacing(self, usable_width: float, cols: int) -> float:
        """Calculate actual horizontal spacing after fitting cards."""
        if cols <= 1:
            return 0

        total_card_width = cols * self.card_width_mm
        remaining_space = usable_width - total_card_width

        # Distribute remaining space as spacing between cards
        spacing_gaps = cols - 1
        return remaining_space / spacing_gaps if spacing_gaps > 0 else 0

    def _calculate_actual_vertical_spacing(self, usable_height: float, rows: int) -> float:
        """Calculate actual vertical spacing after fitting cards."""
        if rows <= 1:
            return 0

        total_card_height = rows * self.card_height_mm
        remaining_space = usable_height - total_card_height

        # Distribute remaining space as spacing between cards
        spacing_gaps = rows - 1
        return remaining_space / spacing_gaps if spacing_gaps > 0 else 0

    def get_card_positions(self, layout: Dict) -> List[Tuple[float, float]]:
        """
        Calculate exact positions for each card on a page.

        Args:
            layout: Layout information from calculate_optimal_layout

        Returns:
            List of (x, y) positions in mm for each card
        """
        positions = []
        rows = layout['rows']
        cols = layout['cols']

        h_spacing = layout['horizontal_spacing_mm']
        v_spacing = layout['vertical_spacing_mm']

        # Starting position (top-left, accounting for margin)
        start_x = self.margin_mm
        start_y = self.margin_mm

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (self.card_width_mm + h_spacing)
                y = start_y + row * (self.card_height_mm + v_spacing)
                positions.append((x, y))

        return positions

    def validate_layout(self, total_cards: int) -> bool:
        """Validate that the layout will work for given number of cards."""
        try:
            layout = self.calculate_optimal_layout(total_cards)
            return layout['cards_per_page'] > 0 and layout['total_pages'] > 0
        except:
            return False

    def get_layout_summary(self, total_cards: int) -> Dict:
        """Get human-readable layout summary."""
        layout = self.calculate_optimal_layout(total_cards)

        return {
            'total_cards': total_cards,
            'cards_per_page': layout['cards_per_page'],
            'total_pages': layout['total_pages'],
            'grid_layout': f"{layout['rows']} x {layout['cols']}",
            'card_size_mm': f"{self.card_width_mm} x {self.card_height_mm}",
            'page_utilization': self._calculate_page_utilization(layout),
            'estimated_print_time': self._estimate_print_time(layout['total_pages'])
        }

    def _calculate_page_utilization(self, layout: Dict) -> float:
        """Calculate what percentage of the page is used by cards."""
        cards_per_page = layout['cards_per_page']
        total_card_area = cards_per_page * self.card_width_mm * self.card_height_mm

        usable_area = layout['usable_width_mm'] * layout['usable_height_mm']

        return (total_card_area / usable_area) * 100 if usable_area > 0 else 0

    def _estimate_print_time(self, pages: int) -> str:
        """Estimate print time based on number of pages."""
        # Rough estimate: 30 seconds per page for high-quality color printing
        estimated_minutes = (pages * 0.5)

        if estimated_minutes < 1:
            return "< 1 minute"
        elif estimated_minutes < 60:
            return f"{int(estimated_minutes)} minutes"
        else:
            hours = int(estimated_minutes // 60)
            minutes = int(estimated_minutes % 60)
            return f"{hours}h {minutes}m"

    def optimize_for_paper_size(self, total_cards: int, paper_size: str = "A4") -> Dict:
        """
        Optimize layout for different paper sizes.

        Args:
            total_cards: Number of cards
            paper_size: Paper size ("A4", "Letter", etc.)

        Returns:
            Optimized layout information
        """
        if paper_size == "Letter":
            # US Letter: 8.5" x 11" = 215.9mm x 279.4mm
            original_width = self.a4_width_mm
            original_height = self.a4_height_mm

            self.a4_width_mm = 215.9
            self.a4_height_mm = 279.4

            layout = self.calculate_optimal_layout(total_cards)

            # Restore original dimensions
            self.a4_width_mm = original_width
            self.a4_height_mm = original_height

            return layout
        else:
            # Default to A4
            return self.calculate_optimal_layout(total_cards)

    def suggest_alternative_layouts(self, total_cards: int) -> List[Dict]:
        """Suggest alternative layouts with different orientations or settings."""
        alternatives = []

        # Current optimal layout
        current = self.calculate_optimal_layout(total_cards)
        alternatives.append({
            'name': 'Optimal (Portrait)',
            'layout': current,
            'description': 'Best fit for A4 portrait'
        })

        # Landscape orientation
        original_width = self.a4_width_mm
        original_height = self.a4_height_mm

        self.a4_width_mm = original_height  # Swap dimensions
        self.a4_height_mm = original_width

        landscape = self.calculate_optimal_layout(total_cards)
        alternatives.append({
            'name': 'Landscape',
            'layout': landscape,
            'description': 'A4 landscape orientation'
        })

        # Restore original dimensions
        self.a4_width_mm = original_width
        self.a4_height_mm = original_height

        # Compact layout (smaller margins)
        original_margin = self.margin_mm
        self.margin_mm = 5  # Reduce margin

        compact = self.calculate_optimal_layout(total_cards)
        alternatives.append({
            'name': 'Compact',
            'layout': compact,
            'description': 'Smaller margins, more cards per page'
        })

        # Restore original margin
        self.margin_mm = original_margin

        return alternatives

    def calculate_cutting_layout(self, total_cards: int) -> Dict:
        """Calculate layout with extra space for cutting guides."""
        # Add extra margin for cutting guides
        original_margin = self.margin_mm
        original_spacing = self.card_spacing_mm

        # Increase margins and spacing for cutting guides
        self.margin_mm += 5  # Extra 5mm margin
        self.card_spacing_mm += 3  # Extra 3mm spacing for guides

        cutting_layout = self.calculate_optimal_layout(total_cards)

        # Restore original values
        self.margin_mm = original_margin
        self.card_spacing_mm = original_spacing

        cutting_layout['has_cutting_guides'] = True
        return cutting_layout


# Global layout manager instance
page_layout_manager = PageLayoutManager()