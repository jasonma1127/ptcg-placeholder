#!/usr/bin/env python3
"""
Pokemon Card Generator - Main Entry Point

A comprehensive tool for generating printable Pokemon cards from PokeAPI.
Supports generation/ID search, multi-language names, and A4-optimized PDF output.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union
from rich.console import Console

# Import core modules
from src.api.pokemon_api import get_pokemon_api_client, get_pokemon_batch_async
from src.api.image_downloader import download_pokemon_images_async
from src.card.card_designer import CardDesigner
from src.pdf.pdf_generator import PDFGenerator
from src.ui.menu_system import InteractiveSession, ProgressReporter
from src.ui.input_validator import InputValidator
from src.utils.cache_manager import cache_manager
from src.utils.error_handler import (
    PokemonCardGeneratorError, log_error, display_error
)
from src.models import PokemonData
from config.constants import GENERATION_RANGES, GENERATION_NAMES

# Initialize components
console = Console()
validator = InputValidator()


class PokemonCardGenerator:
    """Main application class."""

    def __init__(self):
        self.session = InteractiveSession()
        self.progress = ProgressReporter(console)
        self.card_designer = CardDesigner()
        self.pdf_generator = PDFGenerator()
        self._show_first_run_message()

    def _show_first_run_message(self):
        """Show cache location on first run."""
        if cache_manager.is_first_run():
            console.print("[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]")
            console.print("[cyan]Welcome to Pokemon Card Generator![/cyan]")
            console.print(f"[dim]Cache: {cache_manager.get_cache_location()}[/dim]")
            console.print(f"[dim]Images: {cache_manager.get_image_cache_location()}[/dim]")
            console.print("[dim]Cached data will speed up future runs.[/dim]")
            console.print("[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]\n")

    async def run(self):
        """Main application workflow."""
        try:
            # Get user preferences through interactive session
            session_data = self.session.run_search_workflow()

            if not session_data:
                console.print("[yellow]No search performed. Exiting.[/yellow]")
                return

            # Fetch Pokemon data
            console.print("\n[cyan]Fetching Pokemon data from PokeAPI...[/cyan]")
            pokemon_list = await self._fetch_pokemon_data(session_data)

            if not pokemon_list:
                console.print("[red]No Pokemon found! Please try different search criteria.[/red]")
                return

            # Show results and get confirmation
            self.session.menu.show_search_results(pokemon_list, session_data['search_method'])

            if not self.session.confirm_and_proceed(len(pokemon_list)):
                console.print("[yellow]Operation cancelled.[/yellow]")
                return

            # Download images
            console.print("\n[cyan]Step 1: Downloading Pokemon images...[/cyan]")
            image_paths = await self._download_images(pokemon_list)

            # Generate cards
            console.print("\n[cyan]Step 2: Generating Pokemon cards...[/cyan]")
            cards = await self._generate_cards(pokemon_list, image_paths, session_data['language'])

            # Create PDF
            console.print("\n[cyan]Step 3: Creating PDF...[/cyan]")
            pdf_result = await self._create_pdf(cards, session_data)

            # Show success
            self.session.menu.show_success(
                f"Successfully generated {pdf_result.total_cards} cards in {pdf_result.total_pages} pages!",
                pdf_result.file_path
            )

            # Show summary
            self._show_generation_summary(pdf_result, session_data)

        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        except PokemonCardGeneratorError as e:
            display_error(e)
        except Exception as e:
            log_error(e, "CRITICAL")
            display_error(e)

    async def _fetch_pokemon_data(self, session_data: dict) -> List[PokemonData]:
        """Fetch Pokemon data based on search method."""
        search_method = session_data.get('search_method')

        try:
            if search_method == 'generation':
                generations = session_data['generations']

                # Collect all Pokemon IDs from selected generations
                all_pokemon_ids = []
                for gen in generations:
                    start_id, end_id = GENERATION_RANGES[gen]
                    all_pokemon_ids.extend(range(start_id, end_id + 1))

                # Use async client for batch requests with progress tracking
                from src.api.pokemon_api import AsyncPokemonAPIClient
                client = AsyncPokemonAPIClient()

                with self.progress:
                    self.progress.start_progress(
                        f"Fetching {len(all_pokemon_ids)} Pokemon from {len(generations)} generation(s)...",
                        total=len(all_pokemon_ids)
                    )

                    # Fetch in batches and update progress
                    pokemon_list = []
                    batch_size = 20

                    for i in range(0, len(all_pokemon_ids), batch_size):
                        batch_ids = all_pokemon_ids[i:i + batch_size]
                        batch_pokemon = await client.get_pokemon_batch(batch_ids)
                        pokemon_list.extend(batch_pokemon)
                        self.progress.update_progress(completed=min(i + batch_size, len(all_pokemon_ids)))

                    self.progress.stop_progress()

            elif search_method == 'id':
                pokemon_ids = session_data['pokemon_ids']

                with self.progress:
                    self.progress.start_progress(
                        f"Fetching {len(pokemon_ids)} Pokemon...",
                        total=len(pokemon_ids)
                    )

                    # Use async client for batch requests with progress tracking
                    from src.api.pokemon_api import AsyncPokemonAPIClient
                    client = AsyncPokemonAPIClient()

                    # Fetch in batches and update progress
                    pokemon_list = []
                    batch_size = 20

                    for i in range(0, len(pokemon_ids), batch_size):
                        batch_ids = pokemon_ids[i:i + batch_size]
                        batch_pokemon = await client.get_pokemon_batch(batch_ids)
                        pokemon_list.extend(batch_pokemon)
                        self.progress.update_progress(completed=min(i + batch_size, len(pokemon_ids)))

                    self.progress.stop_progress()

            else:
                raise PokemonCardGeneratorError("Name search not implemented yet")

            return pokemon_list

        except Exception as e:
            if hasattr(self, 'progress') and self.progress.progress:
                self.progress.stop_progress()
            raise

    async def _download_images(self, pokemon_list: List[PokemonData]) -> Dict[int, Optional[Path]]:
        """Download Pokemon images."""
        pokemon_ids = [p.pokemon_id for p in pokemon_list]

        try:
            # Check which images are already cached
            cached_count = 0
            missing_ids = []

            for pokemon_id in pokemon_ids:
                if cache_manager.has_pokemon_image(pokemon_id):
                    cached_count += 1
                else:
                    missing_ids.append(pokemon_id)

            if cached_count > 0:
                console.print(f"[green]✓ Found {cached_count}/{len(pokemon_ids)} cached images[/green]")

            if missing_ids:
                console.print(f"[yellow]→ Need to download {len(missing_ids)} images[/yellow]")
                # Start progress bar for downloads
                with self.progress:
                    self.progress.start_progress(
                        f"Downloading {len(missing_ids)} images...",
                        total=len(missing_ids)
                    )

                    # Progress callback
                    def update_download_progress(completed, total, pokemon_id):
                        self.progress.update_progress(completed=completed)

                    # Download missing images asynchronously with high concurrency
                    await download_pokemon_images_async(
                        missing_ids,
                        progress_callback=update_download_progress,
                        max_concurrent=20
                    )

            # Get all image paths
            image_paths = {}
            for pokemon_id in pokemon_ids:
                path = cache_manager.get_pokemon_image_path(pokemon_id)
                image_paths[pokemon_id] = path

            return image_paths

        except Exception as e:
            raise

    async def _generate_cards(self, pokemon_list: List[PokemonData],
                            image_paths: Dict[int, Optional[Path]],
                            language: Union[str, List[str]]) -> List:
        """Generate Pokemon cards."""
        cards = []

        with self.progress:
            self.progress.start_progress(f"Generating {len(pokemon_list)} cards...")

            try:
                for i, pokemon in enumerate(pokemon_list):
                    # Handle display name for progress - use first language for display
                    if isinstance(language, list):
                        display_lang = language[0]
                    else:
                        display_lang = language

                    self.progress.update_progress(f"Generating card {i+1}/{len(pokemon_list)}: {pokemon.get_display_name(display_lang)}")

                    image_path = image_paths.get(pokemon.pokemon_id)
                    if image_path and image_path.exists():
                        card = self.card_designer.create_card(pokemon, image_path, language)
                        cards.append(card)
                    else:
                        console.print(f"[yellow]Warning: No image for {pokemon.get_display_name(display_lang)} (ID: {pokemon.pokemon_id})[/yellow]")

                self.progress.stop_progress()
                return cards

            except Exception as e:
                self.progress.stop_progress()
                raise

    async def _create_pdf(self, cards: List, session_data: dict):
        """Create PDF from cards."""
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_method = session_data.get('search_method', 'custom')

        if search_method == 'generation':
            generations = session_data.get('generations', [])
            if len(generations) == 1:
                filename = f"pokemon_cards_gen{generations[0]}_{timestamp}.pdf"
            else:
                gen_str = "_".join(map(str, generations))
                filename = f"pokemon_cards_gen{gen_str}_{timestamp}.pdf"
        else:
            filename = f"pokemon_cards_custom_{timestamp}.pdf"

        # Ask user where to save the PDF
        output_path = self._get_output_path(filename)

        with self.progress:
            self.progress.start_progress("Creating PDF...")

            try:
                metadata = {
                    'title': f'Pokemon Cards - {session_data.get("search_method", "Custom").title()}',
                    'language': session_data.get('language', 'en'),
                    'generated_at': datetime.now().isoformat(),
                    'total_cards': len(cards)
                }

                result = self.pdf_generator.generate_cards_pdf(cards, str(output_path), metadata)
                self.progress.stop_progress()
                return result

            except Exception as e:
                self.progress.stop_progress()
                raise

    def _get_output_path(self, filename: str) -> Path:
        """Ask user where to save the PDF."""
        from rich.panel import Panel
        from rich.prompt import Prompt

        # Show default locations
        default_locations = {
            "1": ("Desktop", Path.home() / "Desktop"),
            "2": ("Downloads", Path.home() / "Downloads"),
            "3": ("Documents", Path.home() / "Documents"),
            "4": ("Current directory", Path.cwd()),
            "5": ("Custom path", None)
        }

        # Display options
        options_text = "\n".join([f"  {key}. {name}" for key, (name, _) in default_locations.items()])

        console.print(Panel(
            f"[bold cyan]Where would you like to save the PDF?[/bold cyan]\n\n{options_text}\n\n"
            f"[dim]Filename: {filename}[/dim]",
            title="📁 Choose Output Location",
            border_style="cyan"
        ))

        choice = Prompt.ask(
            "Select location",
            choices=list(default_locations.keys()),
            default="2"
        )

        if choice == "5":
            # Custom path
            custom_path = Prompt.ask("Enter full path (folder or full file path)")
            custom_path = Path(custom_path).expanduser()

            # Check if it's a directory or file path
            if custom_path.suffix == ".pdf":
                output_path = custom_path
            else:
                # It's a directory
                output_path = custom_path / filename
                output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Use default location
            _, directory = default_locations[choice]
            directory.mkdir(parents=True, exist_ok=True)
            output_path = directory / filename

        console.print(f"[green]✓[/green] Will save to: [cyan]{output_path}[/cyan]\n")
        return output_path

    def _show_generation_summary(self, pdf_result, session_data: dict):
        """Show generation summary."""
        from rich.table import Table
        from rich.panel import Panel

        # Create summary table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Item", style="cyan", width=20)
        table.add_column("Value", style="white")

        table.add_row("Search method:", session_data.get('search_method', 'Unknown'))
        # Handle both single language and multiple languages
        language = session_data.get('language', 'en')
        if isinstance(language, list):
            from config.constants import LANGUAGE_NAMES
            language_names = [LANGUAGE_NAMES.get(lang, lang) for lang in language]
            language_display = " + ".join(language_names)
        else:
            from config.constants import LANGUAGE_NAMES
            language_display = LANGUAGE_NAMES.get(language, language)

        table.add_row("Language:", language_display)
        table.add_row("Total cards:", str(pdf_result.total_cards))
        table.add_row("Total pages:", str(pdf_result.total_pages))
        table.add_row("Cards per page:", str(pdf_result.cards_per_page))
        table.add_row("File size:", f"{pdf_result.file_size_mb:.2f} MB")
        table.add_row("Generation time:", f"{pdf_result.generation_time_seconds:.2f} seconds")

        summary_panel = Panel(table, title="📊 Generation Summary", border_style="green")
        console.print()
        console.print(summary_panel)

        # Show cache stats
        cache_stats = cache_manager.get_comprehensive_stats()
        console.print(f"\n[dim]Cache: {cache_stats['image_cache']['total_images']} images, "
                     f"{cache_stats['memory_cache']['total_entries']} memory entries, "
                     f"{cache_stats['file_cache']['total_files']} cached files[/dim]")


def main():
    """Main entry point for interactive mode."""
    app = PokemonCardGenerator()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
