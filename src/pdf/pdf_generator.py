"""
PDF generator for Pokemon cards.
Handles page layout, card arrangement, and PDF creation.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
import io

from src.models import PDFGenerationResult, CardData
from src.utils.error_handler import PDFGenerationError, create_error_context, log_error
from src.pdf.page_layout import PageLayoutManager
from config.settings import settings
from config.constants import PDF_CONSTANTS


class CardFlowable(Flowable):
    """Custom flowable for embedding PIL images in ReportLab."""

    def __init__(self, image: Image.Image, width: float, height: float):
        Flowable.__init__(self)
        self.image = image
        self.width = width
        self.height = height

    def draw(self):
        """Draw the image on the canvas."""
        # Convert RGBA to RGB for better PDF compatibility
        if self.image.mode == 'RGBA':
            # Create white background for transparency
            rgb_image = Image.new('RGB', self.image.size, (255, 255, 255))
            rgb_image.paste(self.image, mask=self.image.split()[-1])  # Use alpha as mask
            # Preserve DPI information from original image
            if 'dpi' in self.image.info:
                rgb_image.info['dpi'] = self.image.info['dpi']
            image_to_draw = rgb_image
        else:
            image_to_draw = self.image.convert('RGB')

        # Draw the image with higher quality settings
        # Explicitly specify dimensions to ensure correct print size
        self.canv.drawInlineImage(
            image_to_draw, 0, 0, width=self.width, height=self.height
        )


class PDFGenerator:
    """Main PDF generator for Pokemon cards."""

    def __init__(self):
        self.page_layout = PageLayoutManager()
        self.a4_width = A4[0]
        self.a4_height = A4[1]

    @create_error_context("generate PDF")
    def generate_cards_pdf(self, cards: List[Image.Image], output_path: str,
                          metadata: Optional[Dict] = None) -> PDFGenerationResult:
        """
        Generate PDF with Pokemon cards arranged in optimal layout.

        Args:
            cards: List of PIL Images (cards)
            output_path: Path for output PDF
            metadata: Optional metadata for PDF

        Returns:
            PDFGenerationResult with generation stats
        """
        start_time = time.time()

        if not cards:
            raise PDFGenerationError("No cards provided for PDF generation")

        # Prepare output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Calculate layout
        layout_info = self.page_layout.calculate_optimal_layout(len(cards))

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_file),
                pagesize=A4,
                leftMargin=layout_info['margin'],
                rightMargin=layout_info['margin'],
                topMargin=layout_info['margin'],
                bottomMargin=layout_info['margin']
            )

            # Build document content
            story = []

            # Add metadata if provided (commented out to remove title)
            # if metadata:
            #     story.append(self._create_metadata_section(metadata))
            #     story.append(Spacer(1, 10 * mm))

            # Add cards in pages
            cards_per_page = layout_info['cards_per_page']
            total_pages = (len(cards) + cards_per_page - 1) // cards_per_page

            for page_num in range(total_pages):
                start_idx = page_num * cards_per_page
                end_idx = min(start_idx + cards_per_page, len(cards))
                page_cards = cards[start_idx:end_idx]

                # Create page layout
                page_content = self._create_page_content(page_cards, layout_info)
                story.extend(page_content)

                # Add page break if not last page
                if page_num < total_pages - 1:
                    story.append(Spacer(1, 0))  # Force page break

            # Build PDF
            doc.build(story)

            # Calculate file size
            file_size_mb = output_file.stat().st_size / (1024 * 1024)

            # Calculate generation time
            generation_time = time.time() - start_time

            return PDFGenerationResult(
                file_path=str(output_file),
                total_cards=len(cards),
                total_pages=total_pages,
                cards_per_page=cards_per_page,
                file_size_mb=file_size_mb,
                generation_time_seconds=generation_time
            )

        except Exception as e:
            raise PDFGenerationError(f"Failed to create PDF: {str(e)}", str(output_file))

    def _create_metadata_section(self, metadata: Dict) -> Flowable:
        """Create metadata section for PDF header."""
        # Create a simple text header with metadata
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import getSampleStyleSheet

        styles = getSampleStyleSheet()
        title_style = styles['Title']

        title_text = metadata.get('title', 'Pokemon Cards')
        return Paragraph(title_text, title_style)

    def _create_page_content(self, cards: List[Image.Image], layout_info: Dict) -> List[Flowable]:
        """Create content for a single page using proper table layout."""
        # Calculate card dimensions in points
        card_width_mm = settings.card.width_mm
        card_height_mm = settings.card.height_mm
        card_width_pt = card_width_mm * mm
        card_height_pt = card_height_mm * mm

        rows = layout_info['rows']
        cols = layout_info['cols']

        # Create table data (2D array of flowables)
        table_data = []

        for row in range(rows):
            table_row = []

            for col in range(cols):
                card_index = row * cols + col
                if card_index < len(cards):
                    card = cards[card_index]

                    # Optimize card for print
                    card = self._optimize_card_for_print(card)

                    # Create flowable for card
                    card_flowable = CardFlowable(card, card_width_pt, card_height_pt)
                    table_row.append(card_flowable)
                else:
                    # Fill empty cells with spacer
                    table_row.append("")

            table_data.append(table_row)

        # Create table with proper dimensions
        table = Table(
            table_data,
            colWidths=[card_width_pt] * cols,
            rowHeights=[card_height_pt] * rows
        )

        # Configure table style
        table_style = TableStyle([
            # Remove all borders and backgrounds
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),

            # Center align all cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Add spacing between cards
            ('LEFTPADDING', (0, 0), (-1, -1), layout_info['spacing'] / 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), layout_info['spacing'] / 2),
            ('TOPPADDING', (0, 0), (-1, -1), layout_info['spacing'] / 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), layout_info['spacing'] / 2),
        ])

        table.setStyle(table_style)

        return [table]

    def _optimize_card_for_print(self, card: Image.Image) -> Image.Image:
        """Optimize card image for print quality."""
        # Preserve DPI information
        dpi_info = card.info.get('dpi', None)

        # Ensure RGB mode for printing
        if card.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', card.size, (255, 255, 255))
            if card.mode == 'RGBA':
                background.paste(card, mask=card.split()[-1])
            else:
                background.paste(card)
            card = background
        elif card.mode != 'RGB':
            card = card.convert('RGB')

        # Restore DPI information after conversion
        if dpi_info:
            card.info['dpi'] = dpi_info

        return card

    def generate_proof_sheet(self, cards: List[Image.Image], output_path: str) -> PDFGenerationResult:
        """Generate a proof sheet with multiple cards per page for preview."""
        # Use smaller card size for proof sheet
        proof_cards = []
        proof_size = (int(settings.card.width_pixels * 0.5), int(settings.card.height_pixels * 0.5))

        for card in cards:
            proof_card = card.resize(proof_size, Image.Resampling.LANCZOS)
            proof_cards.append(proof_card)

        # Generate with more cards per page
        return self.generate_cards_pdf(proof_cards, output_path, {
            'title': 'Pokemon Cards - Proof Sheet',
            'cards_per_page': 12  # More cards for preview
        })

    def create_cutting_guides(self, cards: List[Image.Image], output_path: str) -> PDFGenerationResult:
        """Generate PDF with cutting guides for precise card cutting."""
        # Add cutting guides to each card
        cards_with_guides = []

        for card in cards:
            card_with_guide = self._add_cutting_guide(card)
            cards_with_guides.append(card_with_guide)

        return self.generate_cards_pdf(cards_with_guides, output_path, {
            'title': 'Pokemon Cards - With Cutting Guides'
        })

    def _add_cutting_guide(self, card: Image.Image) -> Image.Image:
        """Add cutting guides around a card."""
        from PIL import ImageDraw

        # Create larger canvas for guides
        guide_margin = 20  # pixels
        new_width = card.width + (2 * guide_margin)
        new_height = card.height + (2 * guide_margin)

        guided_card = Image.new('RGB', (new_width, new_height), 'white')

        # Paste original card centered
        guided_card.paste(card, (guide_margin, guide_margin))

        # Add cutting guides
        draw = ImageDraw.Draw(guided_card)

        # Corner marks
        mark_size = 10
        mark_color = 'black'

        # Top-left
        draw.line([0, guide_margin, mark_size, guide_margin], fill=mark_color, width=1)
        draw.line([guide_margin, 0, guide_margin, mark_size], fill=mark_color, width=1)

        # Top-right
        draw.line([new_width - mark_size, guide_margin, new_width, guide_margin], fill=mark_color, width=1)
        draw.line([new_width - guide_margin, 0, new_width - guide_margin, mark_size], fill=mark_color, width=1)

        # Bottom-left
        draw.line([0, new_height - guide_margin, mark_size, new_height - guide_margin], fill=mark_color, width=1)
        draw.line([guide_margin, new_height - mark_size, guide_margin, new_height], fill=mark_color, width=1)

        # Bottom-right
        draw.line([new_width - mark_size, new_height - guide_margin, new_width, new_height - guide_margin], fill=mark_color, width=1)
        draw.line([new_width - guide_margin, new_height - mark_size, new_width - guide_margin, new_height], fill=mark_color, width=1)

        return guided_card

    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> None:
        """Merge multiple PDF files into one."""
        try:
            from PyPDF2 import PdfMerger
            merger = PdfMerger()

            for pdf_file in pdf_files:
                if Path(pdf_file).exists():
                    merger.append(pdf_file)

            merger.write(output_path)
            merger.close()

        except ImportError:
            raise PDFGenerationError("PyPDF2 not available for PDF merging")
        except Exception as e:
            raise PDFGenerationError(f"Failed to merge PDFs: {str(e)}")

    def add_pdf_metadata(self, pdf_path: str, metadata: Dict) -> None:
        """Add metadata to existing PDF file."""
        try:
            from PyPDF2 import PdfReader, PdfWriter

            reader = PdfReader(pdf_path)
            writer = PdfWriter()

            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)

            # Add metadata
            writer.add_metadata({
                '/Title': metadata.get('title', 'Pokemon Cards'),
                '/Author': metadata.get('author', 'Pokemon Card Generator'),
                '/Subject': metadata.get('subject', 'Generated Pokemon Cards'),
                '/Creator': 'Pokemon Card Generator v1.0',
                '/Producer': 'ReportLab',
                '/CreationDate': datetime.now().strftime("D:%Y%m%d%H%M%S")
            })

            # Write updated PDF
            with open(pdf_path, 'wb') as output_file:
                writer.write(output_file)

        except ImportError:
            log_error(PDFGenerationError("PyPDF2 not available for metadata"), "WARNING")
        except Exception as e:
            log_error(PDFGenerationError(f"Failed to add metadata: {str(e)}"), "WARNING")

    def validate_cards_for_pdf(self, cards: List[Image.Image]) -> bool:
        """Validate that cards are suitable for PDF generation."""
        if not cards:
            return False

        for card in cards:
            # Check image mode
            if card.mode not in ['RGB', 'RGBA']:
                return False

            # Check image size (should match card dimensions)
            expected_width = settings.card.width_pixels
            expected_height = settings.card.height_pixels

            if card.size != (expected_width, expected_height):
                return False

        return True

    def estimate_pdf_size(self, num_cards: int) -> Dict[str, float]:
        """Estimate PDF file size and page count."""
        layout_info = self.page_layout.calculate_optimal_layout(num_cards)

        estimated_pages = layout_info['total_pages']

        # Rough estimation: ~500KB per page for high-quality images
        estimated_size_mb = estimated_pages * 0.5

        return {
            'estimated_pages': estimated_pages,
            'estimated_size_mb': estimated_size_mb,
            'cards_per_page': layout_info['cards_per_page']
        }


# Convenience functions
def generate_pokemon_cards_pdf(cards: List[Image.Image], output_path: str,
                              title: str = "Pokemon Cards") -> PDFGenerationResult:
    """Convenience function to generate Pokemon cards PDF."""
    generator = PDFGenerator()
    metadata = {
        'title': title,
        'generated_at': datetime.now().isoformat()
    }
    return generator.generate_cards_pdf(cards, output_path, metadata)


# Global generator instance
pdf_generator = PDFGenerator()