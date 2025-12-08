"""
Constants used throughout the Pokemon card generator.
"""

from typing import Any, Dict, List, Tuple

# Pokemon generation ranges (ID ranges for each generation)
GENERATION_RANGES: Dict[int, Tuple[int, int]] = {
    1: (1, 151),      # Kanto (Bulbasaur to Mew)
    2: (152, 251),    # Johto (Chikorita to Celebi)
    3: (252, 386),    # Hoenn (Treecko to Deoxys)
    4: (387, 493),    # Sinnoh (Turtwig to Arceus)
    5: (494, 649),    # Unova (Victini to Genesect)
    6: (650, 721),    # Kalos (Chespin to Volcanion)
    7: (722, 809),    # Alola (Rowlet to Melmetal)
    8: (810, 905),    # Galar (Grookey to Enamorus)
    9: (906, 1025),   # Paldea (Sprigatito to Pecharunt)
}

# Generation names
GENERATION_NAMES: Dict[int, str] = {
    1: "Kanto (Gen I)",
    2: "Johto (Gen II)",
    3: "Hoenn (Gen III)",
    4: "Sinnoh (Gen IV)",
    5: "Unova (Gen V)",
    6: "Kalos (Gen VI)",
    7: "Alola (Gen VII)",
    8: "Galar (Gen VIII)",
    9: "Paldea (Gen IX)",
}

# Language mappings for PokeAPI
LANGUAGE_MAP: Dict[str, str] = {
    'en': 'english',
    'zh-Hant': 'zh-Hant',  # Traditional Chinese
    'ja': 'ja-Hrkt',       # Japanese
}

# Language display names
LANGUAGE_NAMES: Dict[str, str] = {
    'en': 'English',
    'zh-Hant': '繁體中文',
    'ja': '日本語',
}

# Font configuration for different languages
FONT_CONFIG: Dict[str, str] = {
    'en': 'fonts/arial.ttf',
    'zh-Hant': 'fonts/noto-sans-tc.ttf',
    'ja': 'fonts/noto-sans-jp.ttf',
}

# Default fallback fonts (system fonts)
FALLBACK_FONTS: Dict[str, List[str]] = {
    'en': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
    'zh-Hant': ['STHeiti Medium', 'STHeiti Light', 'Hiragino Sans GB', 'PingFang SC', 'Microsoft JhengHei'],
    'ja': ['Hiragino Sans GB', 'STHeiti Medium', 'Yu Gothic', 'Hiragino Sans'],
}

# API endpoints
API_ENDPOINTS: Dict[str, str] = {
    'pokemon': '/pokemon/{id}',
    'pokemon_species': '/pokemon-species/{id}',
    'generation': '/generation/{id}',
    'pokemon_form': '/pokemon-form/{id}',
}

# Image URLs patterns
IMAGE_URL_PATTERNS: Dict[str, str] = {
    'official_artwork': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{id}.png',
    'official_artwork_shiny': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/shiny/{id}.png',
    'home': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{id}.png',
    'home_shiny': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/shiny/{id}.png',
}

# Cache settings
CACHE_KEYS: Dict[str, str] = {
    'pokemon': 'pokemon_{id}',
    'species': 'species_{id}',
    'generation': 'generation_{id}',
    'names': 'names_{id}_{language}',
}

# File extensions and MIME types
SUPPORTED_IMAGE_FORMATS: Dict[str, str] = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml',
}

# PDF settings
PDF_CONSTANTS: Dict[str, Any] = {
    'A4_WIDTH_MM': 210,
    'A4_HEIGHT_MM': 297,
    'POINTS_PER_MM': 2.83465,  # 72 DPI points per mm
    'DEFAULT_QUALITY': 300,    # DPI for images
}

# Error messages
ERROR_MESSAGES: Dict[str, str] = {
    'POKEMON_NOT_FOUND': 'Pokemon with ID {id} not found',
    'GENERATION_INVALID': 'Invalid generation {gen}. Must be between 1 and 9',
    'NETWORK_ERROR': 'Network error occurred: {error}',
    'IMAGE_DOWNLOAD_FAILED': 'Failed to download image for Pokemon {id}',
    'CACHE_ERROR': 'Cache operation failed: {error}',
    'PDF_GENERATION_FAILED': 'PDF generation failed: {error}',
    'FONT_NOT_FOUND': 'Font not found for language {language}',
}

# Success messages
SUCCESS_MESSAGES: Dict[str, str] = {
    'POKEMON_FOUND': 'Found {count} Pokemon for generation {gen}',
    'IMAGE_DOWNLOADED': 'Successfully downloaded image for {name}',
    'PDF_GENERATED': 'PDF generated successfully: {path}',
    'CACHE_UPDATED': 'Cache updated for {type}: {id}',
}

# Menu options
SEARCH_METHODS: List[Tuple[str, str]] = [
    ('generation', 'Search by Generation'),
    ('id', 'Search by Pokemon ID'),
    ('name', 'Search by Pokemon Name'),
]

# Progress bar settings
PROGRESS_BAR_STYLE = {
    'bar_width': 40,
    'show_percentage': True,
    'show_eta': True,
    'refresh_rate': 0.1,
}

# Maximum values for validation
MAX_VALUES: Dict[str, int] = {
    'POKEMON_ID': 1025,      # Current maximum Pokemon ID
    'GENERATION': 9,         # Current maximum generation
    'BATCH_SIZE': 50,        # Maximum Pokemon to process at once
    'CACHE_SIZE_MB': 100,    # Maximum cache size in MB
}

# Default values
DEFAULTS: Dict[str, Any] = {
    'LANGUAGE': 'en',
    'CARD_FORMAT': 'standard',
    'OUTPUT_FORMAT': 'pdf',
    'IMAGE_QUALITY': 'high',
    'CACHE_ENABLED': True,
}