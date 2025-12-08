"""
Type icon manager for Pokemon cards.
Downloads and caches Pokemon type icons from PokeAPI.
"""

import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Optional, List
from PIL import Image
import requests

from src.utils.error_handler import ImageDownloadError, log_error


class TypeIconManager:
    """Manager for Pokemon type icons from PokeAPI."""

    def __init__(self):
        self.cache_dir = Path("data/cache/type_icons")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # PokeAPI type ID mapping
        self.type_to_id = {
            'normal': 1, 'fighting': 2, 'flying': 3, 'poison': 4, 'ground': 5,
            'rock': 6, 'bug': 7, 'ghost': 8, 'steel': 9, 'fire': 10,
            'water': 11, 'grass': 12, 'electric': 13, 'psychic': 14,
            'ice': 15, 'dragon': 16, 'dark': 17, 'fairy': 18
        }

        # Use latest generation (Gen IX - Scarlet/Violet)
        self.base_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/types/generation-ix/scarlet-violet"

    def get_type_icon_path(self, type_name: str) -> Optional[Path]:
        """Get path to cached type icon."""
        if type_name.lower() not in self.type_to_id:
            return None

        icon_path = self.cache_dir / f"{type_name.lower()}.png"
        return icon_path if icon_path.exists() else None

    def get_type_icon_url(self, type_name: str) -> Optional[str]:
        """Get PokeAPI URL for type icon."""
        type_id = self.type_to_id.get(type_name.lower())
        if not type_id:
            return None

        return f"{self.base_url}/{type_id}.png"

    async def download_type_icon(self, type_name: str) -> Optional[Path]:
        """Download a single type icon."""
        url = self.get_type_icon_url(type_name)
        if not url:
            log_error(ImageDownloadError(0, type_name, f"Unknown type: {type_name}"), "WARNING")
            return None

        icon_path = self.cache_dir / f"{type_name.lower()}.png"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        icon_data = await response.read()

                        # Save original icon
                        with open(icon_path, 'wb') as f:
                            f.write(icon_data)

                        # Resize to fit within 140x140 pixels while maintaining aspect ratio
                        self._resize_icon(icon_path, 140)

                        return icon_path
                    else:
                        log_error(ImageDownloadError(0, type_name, f"HTTP {response.status}"), "WARNING")
                        return None

        except Exception as e:
            log_error(ImageDownloadError(0, type_name, str(e)), "WARNING")
            return None

    def _resize_icon(self, icon_path: Path, max_size: int):
        """Resize icon proportionally to fit within max_size while maintaining aspect ratio."""
        try:
            with Image.open(icon_path) as img:
                # Convert to RGBA for transparency support
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                # Calculate proportional resize to fit within max_size x max_size
                original_width, original_height = img.size

                # Calculate scale factor to fit within max_size while maintaining aspect ratio
                scale_factor = min(max_size / original_width, max_size / original_height)

                # Calculate new dimensions
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)

                # Resize with high-quality resampling maintaining aspect ratio
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Save back to file
                resized_img.save(icon_path, 'PNG', optimize=True)

        except Exception as e:
            log_error(ImageDownloadError(0, str(icon_path), f"Resize failed: {str(e)}"), "WARNING")

    async def download_all_type_icons(self) -> Dict[str, Optional[Path]]:
        """Download all type icons concurrently."""
        print("📥 Downloading Pokemon type icons...")

        # Create tasks for all type downloads
        tasks = []
        for type_name in self.type_to_id.keys():
            task = asyncio.create_task(self.download_type_icon(type_name))
            tasks.append((type_name, task))

        # Execute downloads concurrently
        results = {}
        for type_name, task in tasks:
            try:
                result = await task
                results[type_name] = result
                if result:
                    print(f"✅ {type_name}: Downloaded")
                else:
                    print(f"❌ {type_name}: Failed")
            except Exception as e:
                print(f"❌ {type_name}: Error - {str(e)}")
                results[type_name] = None

        return results

    def ensure_type_icons_cached(self) -> bool:
        """Ensure all type icons are cached. Download if missing."""
        missing_types = []

        for type_name in self.type_to_id.keys():
            if not self.get_type_icon_path(type_name):
                missing_types.append(type_name)

        if missing_types:
            print(f"📥 Missing {len(missing_types)} type icons, downloading...")

            # Use sync requests for simplicity in sync context
            for type_name in missing_types:
                self._download_type_icon_sync(type_name)

            return True

        return False

    def _download_type_icon_sync(self, type_name: str) -> Optional[Path]:
        """Synchronous version of type icon download."""
        url = self.get_type_icon_url(type_name)
        if not url:
            return None

        icon_path = self.cache_dir / f"{type_name.lower()}.png"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Save original icon
                with open(icon_path, 'wb') as f:
                    f.write(response.content)

                # Resize to fit within 140x140 pixels while maintaining aspect ratio
                self._resize_icon(icon_path, 140)

                print(f"✅ Downloaded: {type_name}")
                return icon_path
            else:
                print(f"❌ Failed: {type_name} (HTTP {response.status_code})")
                return None

        except Exception as e:
            print(f"❌ Error downloading {type_name}: {str(e)}")
            return None

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        total_types = len(self.type_to_id)
        cached_types = sum(1 for type_name in self.type_to_id.keys()
                          if self.get_type_icon_path(type_name))

        return {
            'total_types': total_types,
            'cached_types': cached_types,
            'missing_types': total_types - cached_types
        }

    def clear_cache(self):
        """Clear all cached type icons."""
        for icon_file in self.cache_dir.glob("*.png"):
            icon_file.unlink()

    def load_type_icon(self, type_name: str) -> Optional[Image.Image]:
        """Load type icon as PIL Image."""
        icon_path = self.get_type_icon_path(type_name)
        if not icon_path:
            return None

        try:
            return Image.open(icon_path)
        except Exception as e:
            log_error(ImageDownloadError(0, type_name, f"Failed to load icon: {str(e)}"), "WARNING")
            return None


# Global type icon manager instance
type_icon_manager = TypeIconManager()