"""
Pokemon API client for interacting with PokeAPI.
"""

import asyncio
import time
from typing import Dict, List, Optional, Set, Union
import requests
import aiohttp
from pydantic import ValidationError

from src.models import (
    PokemonBasicData, PokemonSpeciesData, PokemonData,
    GenerationData, SearchResult, APIResponse
)
from src.utils.cache_manager import cache_manager
from src.utils.error_handler import (
    APIError, PokemonNotFoundError, InvalidGenerationError,
    handle_errors, log_error, validate_pokemon_id, validate_generation,
    create_error_context
)
from config.settings import settings
from config.constants import (
    GENERATION_RANGES, LANGUAGE_MAP, API_ENDPOINTS,
    IMAGE_URL_PATTERNS, ERROR_MESSAGES, SUCCESS_MESSAGES
)


class PokemonAPIClient:
    """Client for interacting with PokeAPI."""

    def __init__(self):
        self.base_url = settings.api.base_url
        self.timeout = settings.api.timeout_seconds
        self.max_retries = settings.api.max_retries
        self.rate_limit_delay = settings.api.rate_limit_delay
        self.session: Optional[requests.Session] = None
        self._last_request_time = 0.0

    def __enter__(self):
        """Context manager entry."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Pokemon-Card-Generator/1.0 (https://github.com/user/pokemon-card-generator)'
        })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            self.session.close()

    def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self._last_request_time = time.time()

    @handle_errors(reraise=True)
    def _make_request(self, endpoint: str, retries: int = 0) -> Dict:
        """Make HTTP request to PokeAPI with retries."""
        self._rate_limit()

        url = f"{self.base_url}{endpoint}"

        try:
            if self.session:
                response = self.session.get(url, timeout=self.timeout)
            else:
                response = requests.get(url, timeout=self.timeout)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise PokemonNotFoundError(0)  # Will be updated by caller
            else:
                raise APIError(f"HTTP error: {e}", response.status_code, url)

        except requests.exceptions.RequestException as e:
            if retries < self.max_retries:
                time.sleep(2 ** retries)  # Exponential backoff
                return self._make_request(endpoint, retries + 1)
            else:
                raise APIError(f"Request failed after {self.max_retries} retries: {e}", url=url)

    @create_error_context("fetch Pokemon data")
    def get_pokemon_by_id(self, pokemon_id: int) -> PokemonData:
        """Get Pokemon data by ID."""
        validate_pokemon_id(pokemon_id)

        # Check cache first
        cached_data = cache_manager.get_pokemon_data(pokemon_id)
        if cached_data:
            try:
                return PokemonData(**cached_data)
            except ValidationError:
                # Cache data is corrupted, continue to fetch fresh data
                pass

        # Fetch from API
        endpoint = API_ENDPOINTS['pokemon'].format(id=pokemon_id)
        try:
            basic_data = self._make_request(endpoint)
            pokemon_basic = PokemonBasicData(**basic_data)
        except PokemonNotFoundError:
            raise PokemonNotFoundError(pokemon_id)

        # Get species data for names and additional info
        species_data = self.get_pokemon_species(pokemon_id)

        # Get official artwork URL
        official_artwork_url = self.get_official_artwork_url(pokemon_id)

        # Create complete Pokemon data
        pokemon_data = PokemonData(
            basic=pokemon_basic,
            species=species_data,
            official_artwork_url=official_artwork_url
        )

        # Cache the result
        cache_manager.set_pokemon_data(pokemon_id, pokemon_data.model_dump(),
                                     settings.api.cache_duration_hours)

        return pokemon_data

    @create_error_context("fetch Pokemon species data")
    def get_pokemon_species(self, pokemon_id: int) -> Optional[PokemonSpeciesData]:
        """Get Pokemon species data by ID."""
        validate_pokemon_id(pokemon_id)

        # Check cache first
        cached_data = cache_manager.get_species_data(pokemon_id)
        if cached_data:
            try:
                return PokemonSpeciesData(**cached_data)
            except ValidationError:
                pass

        # Fetch from API
        endpoint = API_ENDPOINTS['pokemon_species'].format(id=pokemon_id)
        try:
            species_data = self._make_request(endpoint)
            species = PokemonSpeciesData(**species_data)

            # Cache the result
            cache_manager.set_species_data(pokemon_id, species.model_dump(),
                                         settings.api.cache_duration_hours)
            return species

        except PokemonNotFoundError:
            # Species data might not exist for some Pokemon
            return None

    @create_error_context("fetch Pokemon by generation")
    def get_pokemon_by_generation(self, generation: int) -> List[PokemonData]:
        """Get all Pokemon from a specific generation."""
        validate_generation(generation)

        # Check cache first
        cached_data = cache_manager.get_generation_data(generation)
        if cached_data:
            pokemon_ids = cached_data.get('pokemon_ids', [])
            if pokemon_ids:
                return [self.get_pokemon_by_id(pid) for pid in pokemon_ids]

        # Get Pokemon IDs for this generation
        start_id, end_id = GENERATION_RANGES[generation]
        pokemon_ids = list(range(start_id, end_id + 1))

        # Cache the generation data
        generation_data = {
            'generation': generation,
            'pokemon_ids': pokemon_ids,
            'count': len(pokemon_ids)
        }
        cache_manager.set_generation_data(generation, generation_data, 48)  # Cache for 2 days

        # Fetch all Pokemon data
        pokemon_list = []
        for pokemon_id in pokemon_ids:
            try:
                pokemon_data = self.get_pokemon_by_id(pokemon_id)
                pokemon_list.append(pokemon_data)
            except PokemonNotFoundError:
                # Some Pokemon IDs might not exist, skip them
                log_error(PokemonNotFoundError(pokemon_id), "WARNING")
                continue

        return pokemon_list

    @create_error_context("fetch Pokemon by ID list")
    def get_pokemon_by_ids(self, pokemon_ids: List[int]) -> List[PokemonData]:
        """Get Pokemon data for a list of IDs."""
        pokemon_list = []

        for pokemon_id in pokemon_ids:
            try:
                pokemon_data = self.get_pokemon_by_id(pokemon_id)
                pokemon_list.append(pokemon_data)
            except PokemonNotFoundError:
                log_error(PokemonNotFoundError(pokemon_id), "WARNING")
                continue

        return pokemon_list

    @create_error_context("fetch Pokemon names")
    def get_pokemon_names(self, pokemon_id: int, languages: List[str] = None) -> Dict[str, str]:
        """Get Pokemon names in multiple languages."""
        if languages is None:
            languages = ['en', 'zh-Hant', 'ja']

        validate_pokemon_id(pokemon_id)

        names = {}
        species_data = self.get_pokemon_species(pokemon_id)

        if species_data:
            for language in languages:
                # Map language code to PokeAPI language format
                api_language = LANGUAGE_MAP.get(language, language)
                name = species_data.get_name_by_language(api_language)
                if name:
                    names[language] = name

        return names

    def get_official_artwork_url(self, pokemon_id: int) -> Optional[str]:
        """Get the official artwork URL for a Pokemon."""
        validate_pokemon_id(pokemon_id)

        # Use the pattern from constants
        url = IMAGE_URL_PATTERNS['official_artwork'].format(id=pokemon_id)

        # Verify URL exists by making a HEAD request
        try:
            if self.session:
                response = self.session.head(url, timeout=5)
            else:
                response = requests.head(url, timeout=5)

            if response.status_code == 200:
                return url
        except requests.RequestException:
            pass

        return None

    def search_pokemon_by_name(self, name: str, fuzzy: bool = True) -> List[int]:
        """Search Pokemon by name (placeholder implementation)."""
        # This would require a more complex implementation
        # For now, return empty list
        return []

    @create_error_context("fetch generation data")
    def get_generation_info(self, generation: int) -> GenerationData:
        """Get detailed generation information."""
        validate_generation(generation)

        endpoint = API_ENDPOINTS['generation'].format(id=generation)
        generation_data = self._make_request(endpoint)

        return GenerationData(**generation_data)


class AsyncPokemonAPIClient:
    """Async version of Pokemon API client for batch operations."""

    def __init__(self, max_concurrent: int = 10):
        self.base_url = settings.api.base_url
        self.timeout = settings.api.timeout_seconds
        self.max_retries = settings.api.max_retries
        self.rate_limit_delay = settings.api.rate_limit_delay
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._last_request_time = 0.0

    async def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self._last_request_time = time.time()

    async def _make_request(self, session: aiohttp.ClientSession, endpoint: str, retries: int = 0) -> Dict:
        """Make async HTTP request with retries."""
        async with self._semaphore:
            await self._rate_limit()

            url = f"{self.base_url}{endpoint}"

            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status == 404:
                        raise PokemonNotFoundError(0)
                    response.raise_for_status()
                    return await response.json()

            except aiohttp.ClientError as e:
                if retries < self.max_retries:
                    await asyncio.sleep(2 ** retries)
                    return await self._make_request(session, endpoint, retries + 1)
                else:
                    raise APIError(f"Request failed after {self.max_retries} retries: {e}", url=url)

    async def get_pokemon_batch(self, pokemon_ids: List[int]) -> List[PokemonData]:
        """Get multiple Pokemon data concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = []

            for pokemon_id in pokemon_ids:
                # Check cache first
                cached_data = cache_manager.get_pokemon_data(pokemon_id)
                if cached_data:
                    try:
                        tasks.append(asyncio.create_task(self._return_cached_pokemon(cached_data)))
                        continue
                    except ValidationError:
                        pass

                # Create task for API request
                task = asyncio.create_task(self._get_pokemon_async(session, pokemon_id))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            pokemon_list = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    log_error(result, "WARNING")
                elif result:
                    pokemon_list.append(result)

            return pokemon_list

    async def _return_cached_pokemon(self, cached_data: Dict) -> PokemonData:
        """Return cached Pokemon data."""
        return PokemonData(**cached_data)

    async def _get_pokemon_async(self, session: aiohttp.ClientSession, pokemon_id: int) -> Optional[PokemonData]:
        """Get single Pokemon data asynchronously."""
        try:
            validate_pokemon_id(pokemon_id)

            # Fetch basic data
            endpoint = API_ENDPOINTS['pokemon'].format(id=pokemon_id)
            basic_data = await self._make_request(session, endpoint)
            pokemon_basic = PokemonBasicData(**basic_data)

            # Fetch species data
            species_endpoint = API_ENDPOINTS['pokemon_species'].format(id=pokemon_id)
            try:
                species_data = await self._make_request(session, species_endpoint)
                species = PokemonSpeciesData(**species_data)
            except PokemonNotFoundError:
                species = None

            # Get official artwork URL
            official_artwork_url = IMAGE_URL_PATTERNS['official_artwork'].format(id=pokemon_id)

            pokemon_data = PokemonData(
                basic=pokemon_basic,
                species=species,
                official_artwork_url=official_artwork_url
            )

            # Cache the result
            cache_manager.set_pokemon_data(pokemon_id, pokemon_data.model_dump(),
                                         settings.api.cache_duration_hours)

            return pokemon_data

        except (PokemonNotFoundError, ValidationError, APIError) as e:
            log_error(e, "WARNING")
            return None


# Factory function to get the appropriate client
def get_pokemon_api_client(async_mode: bool = False) -> Union[PokemonAPIClient, AsyncPokemonAPIClient]:
    """Get Pokemon API client instance."""
    if async_mode:
        return AsyncPokemonAPIClient()
    else:
        return PokemonAPIClient()


# Convenience functions
def get_pokemon_by_id(pokemon_id: int) -> PokemonData:
    """Convenience function to get Pokemon by ID."""
    with get_pokemon_api_client() as client:
        return client.get_pokemon_by_id(pokemon_id)


def get_pokemon_by_generation(generation: int) -> List[PokemonData]:
    """Convenience function to get Pokemon by generation."""
    with get_pokemon_api_client() as client:
        return client.get_pokemon_by_generation(generation)


async def get_pokemon_batch_async(pokemon_ids: List[int]) -> List[PokemonData]:
    """Convenience function to get Pokemon batch asynchronously."""
    client = get_pokemon_api_client(async_mode=True)
    return await client.get_pokemon_batch(pokemon_ids)