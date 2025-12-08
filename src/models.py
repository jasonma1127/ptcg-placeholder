"""
Data models for the Pokemon card generator using Pydantic.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, validator


class PokemonSprite(BaseModel):
    """Model for Pokemon sprite URLs."""
    front_default: Optional[HttpUrl] = None
    back_default: Optional[HttpUrl] = None
    front_shiny: Optional[HttpUrl] = None
    back_shiny: Optional[HttpUrl] = None


class PokemonOtherSprites(BaseModel):
    """Model for other Pokemon sprites (official artwork, home, etc.)."""
    official_artwork: Optional[PokemonSprite] = Field(alias="official-artwork", default=None)
    home: Optional[PokemonSprite] = None
    dream_world: Optional[Dict[str, Optional[HttpUrl]]] = Field(alias="dream_world", default=None)
    showdown: Optional[PokemonSprite] = None

    model_config = {"validate_by_name": True}


class PokemonSprites(BaseModel):
    """Model for all Pokemon sprites."""
    front_default: Optional[HttpUrl] = None
    back_default: Optional[HttpUrl] = None
    front_shiny: Optional[HttpUrl] = None
    back_shiny: Optional[HttpUrl] = None
    other: Optional[PokemonOtherSprites] = None


class PokemonType(BaseModel):
    """Model for Pokemon type information."""
    slot: int
    type: Dict[str, Union[str, HttpUrl]]

    @property
    def name(self) -> str:
        """Get the type name."""
        return self.type.get("name", "")


class PokemonAbility(BaseModel):
    """Model for Pokemon ability information."""
    slot: int
    is_hidden: bool
    ability: Dict[str, Union[str, HttpUrl]]

    @property
    def name(self) -> str:
        """Get the ability name."""
        return self.ability.get("name", "")


class PokemonStat(BaseModel):
    """Model for Pokemon base stats."""
    base_stat: int
    effort: int
    stat: Dict[str, Union[str, HttpUrl]]

    @property
    def name(self) -> str:
        """Get the stat name."""
        return self.stat.get("name", "")


class PokemonSpeciesInfo(BaseModel):
    """Model for Pokemon species reference."""
    name: str
    url: HttpUrl


class PokemonBasicData(BaseModel):
    """Basic Pokemon data model from PokeAPI."""
    id: int
    name: str
    height: int  # in decimeters
    weight: int  # in hectograms
    base_experience: Optional[int] = None
    types: List[PokemonType]
    abilities: List[PokemonAbility] = []
    stats: List[PokemonStat] = []
    sprites: Optional[PokemonSprites] = None
    species: Optional[PokemonSpeciesInfo] = None

    @validator('id')
    def validate_id(cls, v):
        if v < 1:
            raise ValueError("Pokemon ID must be positive")
        return v

    @property
    def height_meters(self) -> float:
        """Convert height to meters."""
        return self.height / 10.0

    @property
    def weight_kg(self) -> float:
        """Convert weight to kilograms."""
        return self.weight / 10.0

    @property
    def primary_type(self) -> Optional[str]:
        """Get the primary (first) type."""
        if self.types:
            return self.types[0].name
        return None

    @property
    def secondary_type(self) -> Optional[str]:
        """Get the secondary type, if any."""
        if len(self.types) > 1:
            return self.types[1].name
        return None


class LanguageReference(BaseModel):
    """Model for language reference objects."""
    name: str
    url: HttpUrl


class VersionReference(BaseModel):
    """Model for version reference objects."""
    name: str
    url: HttpUrl


class PokemonName(BaseModel):
    """Model for Pokemon names in different languages."""
    language: LanguageReference
    name: str

    @property
    def language_code(self) -> str:
        """Get the language code for easier access."""
        return self.language.name


class FlavorTextEntry(BaseModel):
    """Model for Pokemon flavor text entries."""
    flavor_text: str
    language: LanguageReference
    version: VersionReference

    @property
    def language_code(self) -> str:
        """Get the language code for easier access."""
        return self.language.name

    @property
    def version_name(self) -> str:
        """Get the version name for easier access."""
        return self.version.name


class PokemonSpeciesData(BaseModel):
    """Pokemon species data model from PokeAPI."""
    id: int
    name: str
    names: List[PokemonName] = []
    flavor_text_entries: List[FlavorTextEntry] = []
    generation: Optional[Dict[str, Union[str, HttpUrl]]] = None
    is_legendary: bool = False
    is_mythical: bool = False

    def get_name_by_language(self, language: str) -> Optional[str]:
        """Get Pokemon name in specific language."""
        for name_entry in self.names:
            if name_entry.language_code == language:
                return name_entry.name
        return None

    def get_flavor_text_by_language(self, language: str, version: Optional[str] = None) -> Optional[str]:
        """Get flavor text in specific language and optionally specific version."""
        for entry in self.flavor_text_entries:
            if entry.language_code == language:
                if version is None or entry.version_name == version:
                    return entry.flavor_text
        return None


class PokemonData(BaseModel):
    """Complete Pokemon data combining basic and species information."""
    basic: PokemonBasicData
    species: Optional[PokemonSpeciesData] = None
    names: Dict[str, str] = {}  # language -> name mapping
    official_artwork_url: Optional[HttpUrl] = None
    cached_at: Optional[datetime] = None

    def get_name(self, language: str = 'en') -> str:
        """Get Pokemon name in specified language, fallback to English."""
        if language in self.names:
            return self.names[language]
        if self.species:
            name = self.species.get_name_by_language(language)
            if name:
                return name
        return self.basic.name.capitalize()

    def get_display_name(self, language: str = 'en') -> str:
        """Get formatted display name for the card."""
        name = self.get_name(language)
        # Clean up name formatting
        return name.replace('-', ' ').title() if name else self.basic.name.capitalize()

    @property
    def pokemon_id(self) -> int:
        """Get Pokemon ID."""
        return self.basic.id

    @property
    def primary_type(self) -> Optional[str]:
        """Get primary type."""
        return self.basic.primary_type

    @property
    def all_types(self) -> List[str]:
        """Get all types as a list."""
        return [t.name for t in self.basic.types]


class GenerationData(BaseModel):
    """Model for Pokemon generation data."""
    id: int
    name: str
    pokemon_species: List[Dict[str, Union[str, HttpUrl]]]
    main_region: Optional[Dict[str, Union[str, HttpUrl]]] = None

    @property
    def pokemon_count(self) -> int:
        """Get number of Pokemon in this generation."""
        return len(self.pokemon_species)


class SearchResult(BaseModel):
    """Model for search results."""
    query: str
    search_type: str  # 'generation', 'id', 'name'
    pokemon_ids: List[int]
    total_count: int
    searched_at: datetime = Field(default_factory=datetime.now)

    @validator('search_type')
    def validate_search_type(cls, v):
        valid_types = ['generation', 'id', 'name']
        if v not in valid_types:
            raise ValueError(f"search_type must be one of {valid_types}")
        return v


class CardGenerationRequest(BaseModel):
    """Model for card generation requests."""
    pokemon_ids: List[int]
    language: str = 'en'
    include_shiny: bool = False
    card_format: str = 'standard'
    output_format: str = 'pdf'
    custom_settings: Optional[Dict[str, Any]] = None

    @validator('language')
    def validate_language(cls, v):
        valid_languages = ['en', 'zh-Hant', 'ja']
        if v not in valid_languages:
            raise ValueError(f"language must be one of {valid_languages}")
        return v

    @validator('pokemon_ids')
    def validate_pokemon_ids(cls, v):
        if not v:
            raise ValueError("At least one Pokemon ID is required")
        for pid in v:
            if pid < 1 or pid > 1025:  # Current max Pokemon ID
                raise ValueError(f"Pokemon ID {pid} is out of valid range (1-1025)")
        return v


class CardData(BaseModel):
    """Model for individual card data."""
    pokemon: PokemonData
    image_path: Optional[str] = None
    card_settings: Optional[Dict[str, Any]] = None
    generated_at: datetime = Field(default_factory=datetime.now)


class PDFGenerationResult(BaseModel):
    """Model for PDF generation results."""
    file_path: str
    total_cards: int
    total_pages: int
    cards_per_page: int
    file_size_mb: float
    generation_time_seconds: float
    generated_at: datetime = Field(default_factory=datetime.now)


class CacheEntry(BaseModel):
    """Model for cache entries."""
    key: str
    data: Union[dict, list, str, int, float]
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def mark_accessed(self) -> None:
        """Mark the entry as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class APIResponse(BaseModel):
    """Generic model for API responses."""
    success: bool
    data: Optional[Union[dict, list]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    cached: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)

    @classmethod
    def success_response(cls, data: Union[dict, list], cached: bool = False) -> "APIResponse":
        """Create a successful response."""
        return cls(success=True, data=data, cached=cached)

    @classmethod
    def error_response(cls, error: str, status_code: Optional[int] = None) -> "APIResponse":
        """Create an error response."""
        return cls(success=False, error=error, status_code=status_code)