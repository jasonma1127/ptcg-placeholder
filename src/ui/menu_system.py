"""
Interactive menu system for the Pokemon card generator.
Uses Rich for beautiful terminal UI.
"""

import sys
from typing import List, Dict, Any, Optional, Union
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn

from src.models import PokemonData, SearchResult
from src.utils.error_handler import ValidationError, log_error
from src.ui.input_validator import InputValidator
from config.constants import (
    GENERATION_RANGES, GENERATION_NAMES, LANGUAGE_NAMES,
    SEARCH_METHODS, MAX_VALUES
)

console = Console()


class MenuSystem:
    """Interactive menu system for user input."""

    def __init__(self):
        self.validator = InputValidator()
        self.console = console

    def display_welcome(self) -> None:
        """Display welcome message and application info."""
        welcome_text = Text()
        welcome_text.append("🎮 ", style="bold blue")
        welcome_text.append("Pokemon Card Generator", style="bold cyan")
        welcome_text.append(" 🎴", style="bold blue")

        welcome_panel = Panel(
            welcome_text,
            subtitle="Generate printable Pokemon cards from PokeAPI",
            style="cyan",
            padding=(1, 2)
        )

        self.console.print()
        self.console.print(welcome_panel)
        self.console.print()

    def show_main_menu(self) -> str:
        """Show main menu and get search method selection."""
        self.console.print("[bold yellow]Select search method:[/bold yellow]")
        self.console.print()

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Option", style="cyan")
        table.add_column("Description", style="white")

        for i, (method, description) in enumerate(SEARCH_METHODS, 1):
            table.add_row(f"[bold]{i}[/bold]", description)

        self.console.print(table)
        self.console.print()

        while True:
            choice = Prompt.ask(
                "Choose option",
                choices=["1", "2", "3"],
                default="1"
            )

            method_map = {"1": "generation", "2": "id", "3": "name"}
            return method_map[choice]

    def select_generations(self) -> List[int]:
        """Show generation selection menu."""
        self.console.print("[bold yellow]Select Pokemon generations:[/bold yellow]")
        self.console.print()

        # Display generations in a nice table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Gen", style="cyan", width=4)
        table.add_column("Name", style="white", width=20)
        table.add_column("Pokemon Range", style="yellow", width=15)
        table.add_column("Count", style="green", width=8)

        for gen_id, (start, end) in GENERATION_RANGES.items():
            gen_name = GENERATION_NAMES[gen_id]
            count = end - start + 1
            table.add_row(
                str(gen_id),
                gen_name,
                f"{start}-{end}",
                str(count)
            )

        self.console.print(table)
        self.console.print()

        # Allow multiple selection
        self.console.print("[dim]You can select multiple generations (e.g., '1,2,3' or '1-3')[/dim]")

        while True:
            try:
                input_str = Prompt.ask("Select generation(s)")
                generations = self.validator.parse_generation_input(input_str)

                if generations:
                    # Show confirmation
                    selected_names = [GENERATION_NAMES[g] for g in generations]
                    self.console.print(f"[green]Selected: {', '.join(selected_names)}[/green]")
                    return generations
                else:
                    self.console.print("[red]Please select at least one generation.[/red]")

            except ValidationError as e:
                self.console.print(f"[red]Error: {e.message}[/red]")

    def input_pokemon_ids(self) -> List[int]:
        """Get Pokemon IDs from user input."""
        self.console.print("[bold yellow]Enter Pokemon IDs:[/bold yellow]")
        self.console.print()
        self.console.print("[dim]You can enter:[/dim]")
        self.console.print("[dim]• Single ID: 25[/dim]")
        self.console.print("[dim]• Multiple IDs: 1,25,150[/dim]")
        self.console.print("[dim]• Range: 1-10[/dim]")
        self.console.print("[dim]• Mixed: 1,25,100-150[/dim]")
        self.console.print()

        while True:
            try:
                input_str = Prompt.ask("Enter Pokemon ID(s)")
                pokemon_ids = self.validator.parse_pokemon_id_input(input_str)

                if pokemon_ids:
                    self.console.print(f"[green]Selected {len(pokemon_ids)} Pokemon: {pokemon_ids[:10]}{'...' if len(pokemon_ids) > 10 else ''}[/green]")
                    return pokemon_ids
                else:
                    self.console.print("[red]Please enter at least one valid Pokemon ID.[/red]")

            except ValidationError as e:
                self.console.print(f"[red]Error: {e.message}[/red]")

    def select_language(self) -> Union[str, List[str]]:
        """Language selection menu with multi-language support."""
        self.console.print("[bold yellow]Select card language(s):[/bold yellow]")
        self.console.print()

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Option", style="cyan")
        table.add_column("Language", style="white")

        language_options = list(LANGUAGE_NAMES.items())
        for i, (code, name) in enumerate(language_options, 1):
            table.add_row(f"[bold]{i}[/bold]", name)

        self.console.print(table)
        self.console.print()

        # Instructions for multi-language selection
        self.console.print("[dim]You can select multiple languages for Pokemon names:[/dim]")
        self.console.print("[dim]• Single language: 1[/dim]")
        self.console.print("[dim]• Multiple languages: 1,3 (for English + Japanese)[/dim]")
        self.console.print("[dim]• Order matters: first language will be shown first[/dim]")
        self.console.print()

        while True:
            choice_input = Prompt.ask(
                "Choose language(s)",
                default="1"
            )

            try:
                # Parse multiple selections
                if ',' in choice_input:
                    # Multiple languages
                    choice_nums = [int(c.strip()) for c in choice_input.split(',')]
                    selected_languages = []
                    selected_names = []

                    for choice_num in choice_nums:
                        if 1 <= choice_num <= len(language_options):
                            lang_code = language_options[choice_num - 1][0]
                            lang_name = LANGUAGE_NAMES[lang_code]
                            selected_languages.append(lang_code)
                            selected_names.append(lang_name)
                        else:
                            raise ValueError(f"Invalid choice: {choice_num}")

                    if selected_languages:
                        self.console.print(f"[green]Selected: {' + '.join(selected_names)}[/green]")
                        return selected_languages
                else:
                    # Single language
                    choice_num = int(choice_input)
                    if 1 <= choice_num <= len(language_options):
                        selected_language = language_options[choice_num - 1][0]
                        language_name = LANGUAGE_NAMES[selected_language]
                        self.console.print(f"[green]Selected: {language_name}[/green]")
                        return selected_language
                    else:
                        raise ValueError(f"Invalid choice: {choice_num}")

            except (ValueError, IndexError) as e:
                self.console.print(f"[red]Invalid input. Please enter valid numbers (1-{len(language_options)}) separated by commas.[/red]")

    def confirm_selection(self, pokemon_count: int, language: Union[str, List[str]], search_info: Dict[str, Any]) -> bool:
        """Show confirmation dialog before processing."""
        self.console.print()
        self.console.print("[bold yellow]Confirmation:[/bold yellow]")

        # Create confirmation table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Item", style="cyan", width=20)
        table.add_column("Value", style="white")

        table.add_row("Search method:", search_info.get('method', 'Unknown'))
        table.add_row("Search query:", str(search_info.get('query', 'Unknown')))
        table.add_row("Pokemon count:", f"{pokemon_count}")

        # Handle both single language and multiple languages
        if isinstance(language, list):
            language_names = [LANGUAGE_NAMES.get(lang, lang) for lang in language]
            language_display = " + ".join(language_names)
        else:
            language_display = LANGUAGE_NAMES.get(language, language)

        table.add_row("Language:", language_display)

        # Calculate estimated cards and pages
        cards_per_page = 9  # 3x3 grid
        total_pages = (pokemon_count + cards_per_page - 1) // cards_per_page

        table.add_row("Estimated cards:", f"{pokemon_count}")
        table.add_row("Estimated pages:", f"{total_pages}")

        self.console.print(Panel(table, title="Generation Summary", border_style="green"))
        self.console.print()

        return Confirm.ask("Proceed with card generation?", default=True)

    def show_progress_header(self, total_steps: int) -> None:
        """Show progress header."""
        self.console.print()
        self.console.print("[bold cyan]Processing Pokemon cards...[/bold cyan]")
        self.console.print()

    def show_search_results(self, pokemon_list: List[PokemonData], search_method: str) -> None:
        """Display search results in a nice format."""
        if not pokemon_list:
            self.console.print("[red]No Pokemon found![/red]")
            return

        self.console.print(f"[bold green]Found {len(pokemon_list)} Pokemon:[/bold green]")
        self.console.print()

        # Show first 10 Pokemon in a table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Name", style="white", width=20)
        table.add_column("Type(s)", style="yellow", width=15)
        table.add_column("Height", style="green", width=8)
        table.add_column("Weight", style="blue", width=8)

        display_count = min(len(pokemon_list), 10)
        for pokemon in pokemon_list[:display_count]:
            types = " / ".join(pokemon.all_types)
            table.add_row(
                str(pokemon.pokemon_id),
                pokemon.basic.name.title(),
                types,
                f"{pokemon.basic.height_meters:.1f}m",
                f"{pokemon.basic.weight_kg:.1f}kg"
            )

        self.console.print(table)

        if len(pokemon_list) > 10:
            self.console.print(f"[dim]... and {len(pokemon_list) - 10} more[/dim]")

        self.console.print()

    def show_generation_info(self, generations: List[int]) -> None:
        """Show information about selected generations."""
        self.console.print("[bold cyan]Generation Information:[/bold cyan]")
        self.console.print()

        total_pokemon = 0
        for gen in generations:
            start, end = GENERATION_RANGES[gen]
            count = end - start + 1
            total_pokemon += count

            gen_name = GENERATION_NAMES[gen]
            self.console.print(f"• [yellow]{gen_name}[/yellow]: {count} Pokemon (#{start}-{end})")

        self.console.print()
        self.console.print(f"[bold green]Total: {total_pokemon} Pokemon[/bold green]")
        self.console.print()

    def show_error(self, error: str) -> None:
        """Display error message."""
        error_panel = Panel(
            f"[red]{error}[/red]",
            title="Error",
            border_style="red"
        )
        self.console.print()
        self.console.print(error_panel)
        self.console.print()

    def show_success(self, message: str, file_path: Optional[str] = None) -> None:
        """Display success message."""
        success_text = Text(message, style="green")

        if file_path:
            success_text.append(f"\n📄 Saved to: {file_path}", style="cyan")

        success_panel = Panel(
            success_text,
            title="Success",
            border_style="green"
        )

        self.console.print()
        self.console.print(success_panel)
        self.console.print()

    def ask_retry(self) -> bool:
        """Ask if user wants to retry after an error."""
        return Confirm.ask("Would you like to try again?", default=True)

    def ask_continue(self) -> bool:
        """Ask if user wants to continue to next step."""
        return Confirm.ask("Continue?", default=True)


class ProgressReporter:
    """Progress reporting for long-running operations."""

    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.progress: Optional[Progress] = None
        self.task_id = None
        self.use_bar = False

    def start_progress(self, description: str, total: Optional[int] = None) -> None:
        """Start a progress indicator."""
        self.use_bar = total is not None and total > 0

        if self.use_bar:
            # Use progress bar for countable tasks
            self.progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.console
            )
            self.progress.start()
            self.task_id = self.progress.add_task(description, total=total)
        else:
            # Use spinner for indeterminate tasks
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
                console=self.console
            )
            self.progress.start()
            self.task_id = self.progress.add_task(description)

    def update_progress(self, description: str = None, advance: int = 0, completed: int = None) -> None:
        """Update progress."""
        if self.progress and self.task_id is not None:
            if description:
                self.progress.update(self.task_id, description=description)
            if advance > 0:
                self.progress.update(self.task_id, advance=advance)
            if completed is not None:
                self.progress.update(self.task_id, completed=completed)

    def stop_progress(self) -> None:
        """Stop progress indicator."""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.task_id = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_progress()


class InteractiveSession:
    """Complete interactive session manager."""

    def __init__(self):
        self.menu = MenuSystem()
        self.session_data = {}

    def run_search_workflow(self) -> Dict[str, Any]:
        """Run the complete search workflow."""
        try:
            # Welcome
            self.menu.display_welcome()

            # Main menu
            search_method = self.menu.show_main_menu()
            self.session_data['search_method'] = search_method

            # Get search parameters
            if search_method == "generation":
                generations = self.menu.select_generations()
                self.session_data['generations'] = generations
                self.menu.show_generation_info(generations)
            elif search_method == "id":
                pokemon_ids = self.menu.input_pokemon_ids()
                self.session_data['pokemon_ids'] = pokemon_ids
            else:  # name search
                self.menu.show_error("Name search is not implemented yet.")
                return {}

            # Language selection
            language = self.menu.select_language()
            self.session_data['language'] = language

            return self.session_data

        except KeyboardInterrupt:
            self.menu.console.print("\n[yellow]Operation cancelled by user.[/yellow]")
            return {}
        except Exception as e:
            self.menu.show_error(str(e))
            return {}

    def confirm_and_proceed(self, pokemon_count: int) -> bool:
        """Show confirmation and get user approval."""
        search_info = {
            'method': self.session_data.get('search_method', 'Unknown'),
            'query': self._get_search_query_display()
        }

        return self.menu.confirm_selection(
            pokemon_count,
            self.session_data.get('language', 'en'),
            search_info
        )

    def _get_search_query_display(self) -> str:
        """Get display string for search query."""
        method = self.session_data.get('search_method')

        if method == 'generation':
            generations = self.session_data.get('generations', [])
            gen_names = [GENERATION_NAMES[g] for g in generations]
            return ', '.join(gen_names)
        elif method == 'id':
            pokemon_ids = self.session_data.get('pokemon_ids', [])
            if len(pokemon_ids) <= 5:
                return ', '.join(map(str, pokemon_ids))
            else:
                return f"{', '.join(map(str, pokemon_ids[:5]))}... ({len(pokemon_ids)} total)"
        else:
            return "Unknown"


# Global instances for easy access
menu_system = MenuSystem()
progress_reporter = ProgressReporter()