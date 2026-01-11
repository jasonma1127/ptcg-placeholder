"""
Welcome screen for Pokemon Card Generator with retro pixel art style.
"""

import random
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align


# Pokemon fun facts
POKEMON_FACTS = [
    "🎮 Pikachu's original design had a second evolution called Gorochu!",
    "⚡ The first Pokemon ever designed was Rhydon, not Pikachu!",
    "🌟 Mew was secretly added to Pokemon Red/Blue by one developer!",
    "🎨 Clefairy was originally meant to be Pokemon's mascot, not Pikachu!",
    "🔮 Ditto and Mew share the exact same base stats (48 each)!",
    "🎯 The Pokemon world has over 1000 Pokemon species now!",
    "💎 Magikarp is considered one of the weakest but evolves into powerful Gyarados!",
    "🌙 Eevee has the most evolutions of any Pokemon (8 forms)!",
    "🎪 Pokemon means 'Pocket Monsters' in Japanese!",
    "🏆 The rarest Pokemon card ever sold for over $5 million USD!",
]


def show_welcome_screen(version: str = "2.0.0", console: Console = None):
    """
    Display a retro pixel art welcome screen.

    Args:
        version: Version number to display
        console: Rich console instance (creates new if None)
    """
    if console is None:
        console = Console()

    # Clear screen for better presentation
    console.clear()

    # Create the main title with retro styling (POKEMON)
    title = Text()
    title.append("  ██████╗  ██████╗ ██╗  ██╗███████╗███╗   ███╗ ██████╗ ███╗   ██╗\n", style="bold red")
    title.append("  ██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝████╗ ████║██╔═══██╗████╗  ██║\n", style="bold red")
    title.append("  ██████╔╝██║   ██║█████╔╝ █████╗  ██╔████╔██║██║   ██║██╔██╗ ██║\n", style="bold red")
    title.append("  ██╔═══╝ ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║\n", style="bold red")
    title.append("  ██║     ╚██████╔╝██║  ██╗███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║\n", style="bold red")
    title.append("  ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝\n", style="bold red")

    subtitle = Text()
    subtitle.append("      ██████╗ █████╗ ██████╗ ██████╗      ██████╗ ███████╗███╗   ██╗\n", style="bold yellow")
    subtitle.append("     ██╔════╝██╔══██╗██╔══██╗██╔══██╗    ██╔════╝ ██╔════╝████╗  ██║\n", style="bold yellow")
    subtitle.append("     ██║     ███████║██████╔╝██║  ██║    ██║  ███╗█████╗  ██╔██╗ ██║\n", style="bold yellow")
    subtitle.append("     ██║     ██╔══██║██╔══██╗██║  ██║    ██║   ██║██╔══╝  ██║╚██╗██║\n", style="bold yellow")
    subtitle.append("     ╚██████╗██║  ██║██║  ██║██████╔╝    ╚██████╔╝███████╗██║ ╚████║\n", style="bold yellow")
    subtitle.append("      ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝      ╚═════╝ ╚══════╝╚═╝  ╚═══╝\n", style="bold yellow")

    # Combine title sections
    header = Text()
    header.append(title)
    header.append(subtitle)

    # Create version and features info
    info = Text()
    info.append(f"\n      Version {version}\n", style="bold cyan")
    info.append("      Made by jasonma1127\n", style="dim white")
    info.append("\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", style="dim cyan")
    info.append("\n  ✨ Features:\n", style="bold magenta")
    info.append("     🔍 Search by Generation (1-9)\n", style="white")
    info.append("     🎯 Search by Pokemon ID\n", style="white")
    info.append("     🌏 Multi-language Support\n", style="white")
    info.append("     📄 A4 PDF Output (300 DPI)\n", style="white")
    info.append("     ⚡ Async Image Downloading\n", style="white")

    # Add random Pokemon fact
    fact = random.choice(POKEMON_FACTS)
    info.append(f"\n  💡 Did you know?\n     {fact}\n", style="bold green")
    info.append("\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", style="dim cyan")

    # Combine all elements
    content = Text()
    content.append(header)
    content.append(info)

    # Create panel with retro border
    panel = Panel(
        Align.center(content),
        border_style="bold blue",
        padding=(1, 2),
        title="[bold white]◢◤ RETRO EDITION ◥◣[/bold white]",
        subtitle="[dim]Press CTRL+C to exit anytime[/dim]"
    )

    console.print(panel)
    console.print()


def show_first_run_message(cache_location: str, image_location: str, console: Console = None):
    """
    Show cache location info on first run.

    Args:
        cache_location: Path to cache directory
        image_location: Path to image cache directory
        console: Rich console instance
    """
    if console is None:
        console = Console()

    message = Text()
    message.append("📁 Cache Locations\n\n", style="bold cyan")
    message.append(f"   Data: {cache_location}\n", style="dim white")
    message.append(f"   Images: {image_location}\n", style="dim white")
    message.append("\n💡 Cached data will speed up future runs!\n", style="green")

    panel = Panel(
        message,
        border_style="cyan",
        padding=(0, 2),
        title="[bold cyan]First Run Setup[/bold cyan]"
    )

    console.print(panel)
    console.print()
