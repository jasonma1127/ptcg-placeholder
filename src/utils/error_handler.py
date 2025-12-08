"""
Error handling framework for the Pokemon card generator.
"""

import logging
import sys
from functools import wraps
from typing import Any, Callable, Optional, Type
from rich.console import Console
from rich.traceback import install

# Install rich traceback handler for better error display
install(show_locals=True)

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pokemon_card_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class PokemonCardGeneratorError(Exception):
    """Base exception for all Pokemon card generator errors."""

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class APIError(PokemonCardGeneratorError):
    """Raised when there's an error with API requests."""

    def __init__(self, message: str, status_code: Optional[int] = None, url: Optional[str] = None):
        super().__init__(message, "API_ERROR")
        self.status_code = status_code
        self.url = url
        if status_code:
            self.details["status_code"] = status_code
        if url:
            self.details["url"] = url


class PokemonNotFoundError(PokemonCardGeneratorError):
    """Raised when a Pokemon is not found."""

    def __init__(self, pokemon_id: int):
        message = f"Pokemon with ID {pokemon_id} not found"
        super().__init__(message, "POKEMON_NOT_FOUND")
        self.pokemon_id = pokemon_id
        self.details["pokemon_id"] = pokemon_id


class InvalidGenerationError(PokemonCardGeneratorError):
    """Raised when an invalid generation is specified."""

    def __init__(self, generation: int, max_generation: int = 9):
        message = f"Invalid generation {generation}. Must be between 1 and {max_generation}"
        super().__init__(message, "INVALID_GENERATION")
        self.generation = generation
        self.max_generation = max_generation
        self.details.update({"generation": generation, "max_generation": max_generation})


class ImageDownloadError(PokemonCardGeneratorError):
    """Raised when image download fails."""

    def __init__(self, pokemon_id: int, url: str, reason: str):
        message = f"Failed to download image for Pokemon {pokemon_id}: {reason}"
        super().__init__(message, "IMAGE_DOWNLOAD_ERROR")
        self.pokemon_id = pokemon_id
        self.url = url
        self.reason = reason
        self.details.update({
            "pokemon_id": pokemon_id,
            "url": url,
            "reason": reason
        })


class CacheError(PokemonCardGeneratorError):
    """Raised when cache operations fail."""

    def __init__(self, operation: str, key: str, reason: str):
        message = f"Cache {operation} failed for key '{key}': {reason}"
        super().__init__(message, "CACHE_ERROR")
        self.operation = operation
        self.key = key
        self.reason = reason
        self.details.update({
            "operation": operation,
            "key": key,
            "reason": reason
        })


class PDFGenerationError(PokemonCardGeneratorError):
    """Raised when PDF generation fails."""

    def __init__(self, reason: str, file_path: Optional[str] = None):
        message = f"PDF generation failed: {reason}"
        super().__init__(message, "PDF_GENERATION_ERROR")
        self.reason = reason
        self.file_path = file_path
        self.details["reason"] = reason
        if file_path:
            self.details["file_path"] = file_path


class FontNotFoundError(PokemonCardGeneratorError):
    """Raised when a required font is not found."""

    def __init__(self, language: str, font_path: str):
        message = f"Font not found for language '{language}' at path: {font_path}"
        super().__init__(message, "FONT_NOT_FOUND")
        self.language = language
        self.font_path = font_path
        self.details.update({
            "language": language,
            "font_path": font_path
        })


class ValidationError(PokemonCardGeneratorError):
    """Raised when input validation fails."""

    def __init__(self, field: str, value: Any, reason: str):
        message = f"Validation failed for {field} = '{value}': {reason}"
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value
        self.reason = reason
        self.details.update({
            "field": field,
            "value": value,
            "reason": reason
        })


def handle_errors(
    default_return: Any = None,
    reraise: bool = False,
    log_level: str = "ERROR"
) -> Callable:
    """
    Decorator to handle errors in functions.

    Args:
        default_return: Value to return if an error occurs
        reraise: Whether to reraise the exception after handling
        log_level: Log level for error messages
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PokemonCardGeneratorError as e:
                log_error(e, log_level)
                if reraise:
                    raise
                return default_return
            except Exception as e:
                error = PokemonCardGeneratorError(
                    f"Unexpected error in {func.__name__}: {str(e)}",
                    "UNEXPECTED_ERROR"
                )
                log_error(error, log_level)
                if reraise:
                    raise error
                return default_return
        return wrapper
    return decorator


def log_error(error: Exception, level: str = "ERROR") -> None:
    """Log an error with appropriate level and formatting."""
    if isinstance(error, PokemonCardGeneratorError):
        details_str = ", ".join([f"{k}={v}" for k, v in error.details.items()])
        log_message = f"{error.message}"
        if details_str:
            log_message += f" (Details: {details_str})"
    else:
        log_message = str(error)

    if level.upper() == "DEBUG":
        logger.debug(log_message, exc_info=True)
    elif level.upper() == "INFO":
        logger.info(log_message)
    elif level.upper() == "WARNING":
        logger.warning(log_message)
    elif level.upper() == "ERROR":
        logger.error(log_message, exc_info=True)
    elif level.upper() == "CRITICAL":
        logger.critical(log_message, exc_info=True)


def display_error(error: Exception, show_details: bool = True) -> None:
    """Display an error using rich console formatting."""
    if isinstance(error, PokemonCardGeneratorError):
        console.print(f"[red]Error: {error.message}[/red]")
        if show_details and error.details:
            console.print(f"[yellow]Details: {error.details}[/yellow]")
    else:
        console.print(f"[red]Unexpected error: {str(error)}[/red]")


def create_error_context(
    operation: str,
    error_class: Type[PokemonCardGeneratorError] = PokemonCardGeneratorError
) -> Callable:
    """
    Context manager decorator for error handling.

    Args:
        operation: Description of the operation being performed
        error_class: Custom error class to use
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PokemonCardGeneratorError:
                raise  # Re-raise our custom errors as-is
            except Exception as e:
                # Wrap other exceptions in our custom error type
                raise error_class(
                    f"Failed to {operation}: {str(e)}",
                    f"{operation.upper()}_FAILED"
                )
        return wrapper
    return decorator


def safe_operation(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
    """
    Safely execute an operation and return success status with result.

    Returns:
        Tuple of (success: bool, result: Any)
    """
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        log_error(e, "WARNING")
        return False, None


def validate_pokemon_id(pokemon_id: int, max_id: int = 1025) -> None:
    """Validate a Pokemon ID."""
    if not isinstance(pokemon_id, int):
        raise ValidationError("pokemon_id", pokemon_id, "Must be an integer")
    if pokemon_id < 1 or pokemon_id > max_id:
        raise ValidationError("pokemon_id", pokemon_id, f"Must be between 1 and {max_id}")


def validate_generation(generation: int, max_generation: int = 9) -> None:
    """Validate a Pokemon generation."""
    if not isinstance(generation, int):
        raise ValidationError("generation", generation, "Must be an integer")
    if generation < 1 or generation > max_generation:
        raise InvalidGenerationError(generation, max_generation)


def validate_language(language: str, supported_languages: list = None) -> None:
    """Validate a language code."""
    if supported_languages is None:
        supported_languages = ['en', 'zh-Hant', 'ja']

    if not isinstance(language, str):
        raise ValidationError("language", language, "Must be a string")
    if language not in supported_languages:
        raise ValidationError("language", language, f"Must be one of: {supported_languages}")