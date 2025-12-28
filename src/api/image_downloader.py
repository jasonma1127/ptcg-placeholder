"""
Image downloader for Pokemon artwork and sprites.
"""

import asyncio
import os
from pathlib import Path
from typing import List, Optional, Dict, Union
import requests
import aiohttp
from PIL import Image
import io

from src.models import PokemonData, APIResponse
from src.utils.cache_manager import cache_manager
from src.utils.error_handler import (
    ImageDownloadError, ValidationError,
    handle_errors, log_error, create_error_context
)
from config.settings import settings
from config.constants import IMAGE_URL_PATTERNS, SUPPORTED_IMAGE_FORMATS


class ImageDownloader:
    """Downloader for Pokemon images with caching support."""

    def __init__(self):
        self.timeout = settings.api.timeout_seconds
        self.max_retries = settings.api.max_retries
        self.session: Optional[requests.Session] = None

    def __enter__(self):
        """Context manager entry."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Pokemon-Card-Generator/1.0'
        })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            self.session.close()

    @handle_errors(reraise=True)
    def download_image(self, url: str, pokemon_id: int, retries: int = 0) -> bytes:
        """Download image from URL."""
        try:
            if self.session:
                response = self.session.get(url, timeout=self.timeout, stream=True)
            else:
                response = requests.get(url, timeout=self.timeout, stream=True)

            response.raise_for_status()

            # Validate content type
            content_type = response.headers.get('content-type', '')
            if not any(ct in content_type for ct in SUPPORTED_IMAGE_FORMATS.values()):
                raise ImageDownloadError(
                    pokemon_id, url,
                    f"Unsupported content type: {content_type}"
                )

            # Read and validate image data
            image_data = response.content
            if len(image_data) == 0:
                raise ImageDownloadError(pokemon_id, url, "Empty image data")

            # Validate image can be opened
            try:
                with Image.open(io.BytesIO(image_data)) as img:
                    img.verify()
            except Exception as e:
                raise ImageDownloadError(pokemon_id, url, f"Invalid image data: {e}")

            return image_data

        except requests.exceptions.RequestException as e:
            if retries < self.max_retries:
                return self.download_image(url, pokemon_id, retries + 1)
            else:
                raise ImageDownloadError(pokemon_id, url, str(e))

    @create_error_context("download Pokemon image")
    def get_pokemon_image(self, pokemon_id: int, force_download: bool = False) -> Optional[Path]:
        """Get Pokemon official artwork image, downloading if necessary."""
        # Check if image already exists in cache
        if not force_download:
            cached_path = cache_manager.get_pokemon_image_path(pokemon_id)
            if cached_path and cached_path.exists():
                return cached_path

        # Get image URL
        url = IMAGE_URL_PATTERNS['official_artwork'].format(id=pokemon_id)

        try:
            # Download image
            image_data = self.download_image(url, pokemon_id)

            # Store in cache
            image_path = cache_manager.store_pokemon_image(pokemon_id, image_data)

            return image_path

        except ImageDownloadError as e:
            log_error(e, "WARNING")
            return None

    def get_pokemon_images_batch(self, pokemon_ids: List[int], force_download: bool = False) -> Dict[int, Optional[Path]]:
        """Download multiple Pokemon images."""
        results = {}

        for pokemon_id in pokemon_ids:
            try:
                image_path = self.get_pokemon_image(pokemon_id, force_download)
                results[pokemon_id] = image_path
            except Exception as e:
                log_error(ImageDownloadError(pokemon_id, "unknown", str(e)), "WARNING")
                results[pokemon_id] = None

        return results

    def get_image_info(self, image_path: Path) -> Dict[str, Union[int, str]]:
        """Get information about an image file."""
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_bytes': image_path.stat().st_size
                }
        except Exception as e:
            log_error(ImageDownloadError(0, str(image_path), f"Could not read image info: {e}"), "WARNING")
            return {}

    def validate_image(self, image_path: Path) -> bool:
        """Validate that an image file is valid and usable."""
        try:
            if not image_path.exists():
                return False

            with Image.open(image_path) as img:
                img.verify()

            # Re-open for additional checks (verify() closes the image)
            with Image.open(image_path) as img:
                # Check minimum size requirements (optional)
                if img.width < 50 or img.height < 50:
                    return False

                # Check if image has reasonable aspect ratio
                aspect_ratio = img.width / img.height
                if aspect_ratio < 0.1 or aspect_ratio > 10:
                    return False

            return True

        except Exception:
            return False

    def resize_image_for_card(self, image_path: Path, max_width: int, max_height: int) -> Path:
        """Resize image to fit card dimensions while maintaining aspect ratio."""
        try:
            with Image.open(image_path) as img:
                # Calculate new size maintaining aspect ratio
                img_ratio = img.width / img.height
                card_ratio = max_width / max_height

                if img_ratio > card_ratio:
                    # Image is wider than card ratio
                    new_width = max_width
                    new_height = int(max_width / img_ratio)
                else:
                    # Image is taller than card ratio
                    new_height = max_height
                    new_width = int(max_height * img_ratio)

                # Resize image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Create resized image path
                resized_path = image_path.parent / f"{image_path.stem}_resized{image_path.suffix}"

                # Save resized image
                resized_img.save(resized_path, format='PNG', optimize=True)

                return resized_path

        except Exception as e:
            log_error(ImageDownloadError(0, str(image_path), f"Could not resize image: {e}"), "WARNING")
            return image_path


class AsyncImageDownloader:
    """Async image downloader for batch operations."""

    def __init__(self, max_concurrent: int = 20, progress_callback=None):
        self.timeout = settings.api.timeout_seconds
        self.max_retries = settings.api.max_retries
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self.progress_callback = progress_callback
        self._completed = 0
        self._total = 0

    async def download_image_async(self, session: aiohttp.ClientSession, url: str, pokemon_id: int, retries: int = 0) -> bytes:
        """Download image asynchronously."""
        async with self._semaphore:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    response.raise_for_status()

                    # Validate content type
                    content_type = response.headers.get('content-type', '')
                    if not any(ct in content_type for ct in SUPPORTED_IMAGE_FORMATS.values()):
                        raise ImageDownloadError(
                            pokemon_id, url,
                            f"Unsupported content type: {content_type}"
                        )

                    image_data = await response.read()

                    if len(image_data) == 0:
                        raise ImageDownloadError(pokemon_id, url, "Empty image data")

                    # Validate image data
                    try:
                        with Image.open(io.BytesIO(image_data)) as img:
                            img.verify()
                    except Exception as e:
                        raise ImageDownloadError(pokemon_id, url, f"Invalid image data: {e}")

                    return image_data

            except aiohttp.ClientError as e:
                if retries < self.max_retries:
                    await asyncio.sleep(2 ** retries)
                    return await self.download_image_async(session, url, pokemon_id, retries + 1)
                else:
                    raise ImageDownloadError(pokemon_id, url, str(e))

    async def get_pokemon_images_batch_async(self, pokemon_ids: List[int], force_download: bool = False) -> Dict[int, Optional[Path]]:
        """Download multiple Pokemon images concurrently."""
        self._total = len(pokemon_ids)
        self._completed = 0

        # Create SSL context with proper certificate verification
        import ssl
        try:
            # Try to use certifi's CA bundle for PyInstaller compatibility
            import certifi
            ssl_context = ssl.create_default_context(cafile=certifi.where())
        except (ImportError, Exception):
            # Fallback: try system certificates
            try:
                ssl_context = ssl.create_default_context()
            except Exception:
                # Last resort: disable verification (not recommended but ensures compatibility)
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []

            for pokemon_id in pokemon_ids:
                # Check cache first unless force download
                if not force_download and cache_manager.has_pokemon_image(pokemon_id):
                    cached_path = cache_manager.get_pokemon_image_path(pokemon_id)
                    if cached_path and cached_path.exists():
                        tasks.append(asyncio.create_task(self._return_cached_path(pokemon_id, cached_path)))
                        continue

                # Create download task
                task = asyncio.create_task(self._download_pokemon_image_async(session, pokemon_id))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            pokemon_images = {}
            for i, result in enumerate(results):
                pokemon_id = pokemon_ids[i] if i < len(pokemon_ids) else 0

                if isinstance(result, Exception):
                    log_error(result, "WARNING")
                    pokemon_images[pokemon_id] = None
                elif isinstance(result, tuple):
                    pid, path = result
                    pokemon_images[pid] = path
                else:
                    pokemon_images[pokemon_id] = result

            return pokemon_images

    async def _return_cached_path(self, pokemon_id: int, path: Path) -> tuple[int, Path]:
        """Return cached image path."""
        self._completed += 1
        if self.progress_callback:
            self.progress_callback(self._completed, self._total, pokemon_id)
        return pokemon_id, path

    async def _download_pokemon_image_async(self, session: aiohttp.ClientSession, pokemon_id: int) -> tuple[int, Optional[Path]]:
        """Download single Pokemon image asynchronously."""
        try:
            url = IMAGE_URL_PATTERNS['official_artwork'].format(id=pokemon_id)
            image_data = await self.download_image_async(session, url, pokemon_id)

            # Store in cache
            image_path = cache_manager.store_pokemon_image(pokemon_id, image_data)

            self._completed += 1
            if self.progress_callback:
                self.progress_callback(self._completed, self._total, pokemon_id)

            return pokemon_id, image_path

        except ImageDownloadError as e:
            log_error(e, "WARNING")
            self._completed += 1
            if self.progress_callback:
                self.progress_callback(self._completed, self._total, pokemon_id)
            return pokemon_id, None


class ImageProcessor:
    """Image processing utilities for card generation."""

    @staticmethod
    def create_card_image(pokemon_image_path: Path, card_width: int, card_height: int) -> Image.Image:
        """Create a card-ready image with proper sizing and positioning."""
        try:
            # Load Pokemon image
            with Image.open(pokemon_image_path) as pokemon_img:
                # Convert to RGBA if not already
                if pokemon_img.mode != 'RGBA':
                    pokemon_img = pokemon_img.convert('RGBA')

                # Calculate card image area (leaving space for text)
                image_area_height = int(card_height * 0.7)  # 70% for image
                image_area_width = card_width - (settings.card.image_padding_pixels * 2)

                # Resize Pokemon image to fit in image area
                pokemon_img = ImageProcessor._resize_with_aspect_ratio(
                    pokemon_img, image_area_width, image_area_height
                )

                # Create card background
                card_image = Image.new('RGBA', (card_width, card_height), (255, 255, 255, 255))

                # Center Pokemon image in card
                x_offset = (card_width - pokemon_img.width) // 2
                y_offset = settings.card.image_padding_pixels

                card_image.paste(pokemon_img, (x_offset, y_offset), pokemon_img)

                return card_image

        except Exception as e:
            log_error(ImageDownloadError(0, str(pokemon_image_path), f"Could not create card image: {e}"), "ERROR")
            raise

    @staticmethod
    def _resize_with_aspect_ratio(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Resize image maintaining aspect ratio to fit within specified dimensions."""
        img_ratio = image.width / image.height
        box_ratio = max_width / max_height

        if img_ratio > box_ratio:
            # Image is wider than target ratio
            new_width = max_width
            new_height = int(max_width / img_ratio)
        else:
            # Image is taller than target ratio
            new_height = max_height
            new_width = int(max_height * img_ratio)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    @staticmethod
    def optimize_image_for_print(image: Image.Image, dpi: int = 300) -> Image.Image:
        """Optimize image for print quality."""
        # Ensure image is in RGB mode for printing
        if image.mode == 'RGBA':
            # Create white background for transparent areas
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        return image


# Factory functions
def get_image_downloader() -> ImageDownloader:
    """Get synchronous image downloader."""
    return ImageDownloader()


def get_async_image_downloader(max_concurrent: int = 20, progress_callback=None) -> AsyncImageDownloader:
    """Get asynchronous image downloader."""
    return AsyncImageDownloader(max_concurrent, progress_callback)


# Convenience functions
def download_pokemon_image(pokemon_id: int, force_download: bool = False) -> Optional[Path]:
    """Download single Pokemon image."""
    with get_image_downloader() as downloader:
        return downloader.get_pokemon_image(pokemon_id, force_download)


async def download_pokemon_images_async(pokemon_ids: List[int], force_download: bool = False, progress_callback=None, max_concurrent: int = 20) -> Dict[int, Optional[Path]]:
    """Download multiple Pokemon images asynchronously."""
    downloader = get_async_image_downloader(max_concurrent, progress_callback)
    return await downloader.get_pokemon_images_batch_async(pokemon_ids, force_download)