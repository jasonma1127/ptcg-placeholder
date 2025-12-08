"""
Cache management system for the Pokemon card generator.
Implements three-layer caching: memory, file, and images.
"""

import json
import pickle
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from src.models import CacheEntry, APIResponse
from src.utils.error_handler import CacheError, handle_errors, log_error
from config.constants import CACHE_KEYS, MAX_VALUES


class MemoryCache:
    """In-memory cache with TTL support."""

    def __init__(self, max_size: int = 1000, default_ttl_hours: int = 1):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl_hours = default_ttl_hours

    def get(self, key: str) -> Optional[Any]:
        """Get item from memory cache."""
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if entry.is_expired():
            del self._cache[key]
            return None

        entry.mark_accessed()
        return entry.data

    def set(self, key: str, data: Any, ttl_hours: Optional[int] = None) -> None:
        """Set item in memory cache."""
        if len(self._cache) >= self.max_size:
            self._evict_lru()

        ttl = ttl_hours or self.default_ttl_hours
        expires_at = datetime.now() + timedelta(hours=ttl)

        entry = CacheEntry(
            key=key,
            data=data,
            expires_at=expires_at
        )
        self._cache[key] = entry

    def delete(self, key: str) -> bool:
        """Delete item from memory cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all items from memory cache."""
        self._cache.clear()

    def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self._cache:
            return

        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed or self._cache[k].created_at
        )
        del self._cache[lru_key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())

        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'max_size': self.max_size,
            'memory_usage_mb': self._estimate_memory_usage()
        }

    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        try:
            import sys
            total_size = sum(sys.getsizeof(entry) for entry in self._cache.values())
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0


class FileCache:
    """File-based cache for persistent storage."""

    def __init__(self, cache_dir: str = "data/cache", max_size_mb: int = 100):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_mb = max_size_mb
        self.api_cache_dir = self.cache_dir / "api_cache"
        self.api_cache_dir.mkdir(exist_ok=True)

    @handle_errors(reraise=True)
    def get(self, key: str) -> Optional[Any]:
        """Get item from file cache."""
        file_path = self._get_cache_file_path(key)
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check if expired
            if 'expires_at' in data and data['expires_at']:
                expires_at = datetime.fromisoformat(data['expires_at'])
                if datetime.now() > expires_at:
                    file_path.unlink()  # Delete expired file
                    return None

            # Update access time
            data['last_accessed'] = datetime.now().isoformat()
            data['access_count'] = data.get('access_count', 0) + 1

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return data['data']

        except Exception as e:
            log_error(CacheError('get', key, str(e)))
            return None

    @handle_errors(reraise=True)
    def set(self, key: str, data: Any, ttl_hours: Optional[int] = None) -> None:
        """Set item in file cache."""
        self._cleanup_if_needed()

        file_path = self._get_cache_file_path(key)
        expires_at = None
        if ttl_hours:
            expires_at = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()

        cache_data = {
            'key': key,
            'data': data,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at,
            'access_count': 0,
            'last_accessed': None
        }

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            raise CacheError('set', key, str(e))

    def delete(self, key: str) -> bool:
        """Delete item from file cache."""
        file_path = self._get_cache_file_path(key)
        try:
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            log_error(CacheError('delete', key, str(e)))
        return False

    def clear(self) -> None:
        """Clear all items from file cache."""
        try:
            for file_path in self.api_cache_dir.glob("*.json"):
                file_path.unlink()
        except Exception as e:
            log_error(CacheError('clear', 'all', str(e)))

    def _get_cache_file_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        # Create safe filename from key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.api_cache_dir / f"{safe_key}.json"

    def _cleanup_if_needed(self) -> None:
        """Clean up old cache files if size limit exceeded."""
        try:
            total_size = sum(f.stat().st_size for f in self.api_cache_dir.glob("*.json"))
            max_size_bytes = self.max_size_mb * 1024 * 1024

            if total_size > max_size_bytes:
                # Remove oldest files first
                files = sorted(
                    self.api_cache_dir.glob("*.json"),
                    key=lambda f: f.stat().st_mtime
                )

                for file_path in files[:len(files)//4]:  # Remove 25% of files
                    file_path.unlink()

        except Exception as e:
            log_error(CacheError('cleanup', 'size_limit', str(e)))

    def get_stats(self) -> Dict[str, Any]:
        """Get file cache statistics."""
        try:
            files = list(self.api_cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in files)

            return {
                'total_files': len(files),
                'total_size_mb': total_size / (1024 * 1024),
                'max_size_mb': self.max_size_mb,
                'usage_percentage': (total_size / (self.max_size_mb * 1024 * 1024)) * 100
            }
        except Exception:
            return {'error': 'Could not get file cache stats'}


class ImageCache:
    """Cache for downloaded Pokemon images."""

    def __init__(self, image_dir: str = "data/pokemon_images"):
        self.image_dir = Path(image_dir)
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.official_artwork_dir = self.image_dir / "official_artwork"
        self.official_artwork_dir.mkdir(exist_ok=True)

    def get_image_path(self, pokemon_id: int, image_type: str = "official_artwork") -> Optional[Path]:
        """Get the local path for a Pokemon image."""
        if image_type == "official_artwork":
            image_path = self.official_artwork_dir / f"{pokemon_id}.png"
        else:
            image_path = self.image_dir / image_type / f"{pokemon_id}.png"

        return image_path if image_path.exists() else None

    def has_image(self, pokemon_id: int, image_type: str = "official_artwork") -> bool:
        """Check if image exists in cache."""
        return self.get_image_path(pokemon_id, image_type) is not None

    def store_image(self, pokemon_id: int, image_data: bytes, image_type: str = "official_artwork") -> Path:
        """Store image in cache."""
        if image_type == "official_artwork":
            image_dir = self.official_artwork_dir
        else:
            image_dir = self.image_dir / image_type
            image_dir.mkdir(exist_ok=True)

        image_path = image_dir / f"{pokemon_id}.png"

        try:
            with open(image_path, 'wb') as f:
                f.write(image_data)
            return image_path
        except Exception as e:
            raise CacheError('store_image', str(pokemon_id), str(e))

    def delete_image(self, pokemon_id: int, image_type: str = "official_artwork") -> bool:
        """Delete image from cache."""
        image_path = self.get_image_path(pokemon_id, image_type)
        if image_path:
            try:
                image_path.unlink()
                return True
            except Exception as e:
                log_error(CacheError('delete_image', str(pokemon_id), str(e)))
        return False

    def clear_images(self, image_type: Optional[str] = None) -> None:
        """Clear all images or specific type."""
        try:
            if image_type:
                if image_type == "official_artwork":
                    target_dir = self.official_artwork_dir
                else:
                    target_dir = self.image_dir / image_type

                for image_file in target_dir.glob("*.png"):
                    image_file.unlink()
            else:
                # Clear all images
                for image_file in self.image_dir.rglob("*.png"):
                    image_file.unlink()
        except Exception as e:
            log_error(CacheError('clear_images', image_type or 'all', str(e)))

    def get_stats(self) -> Dict[str, Any]:
        """Get image cache statistics."""
        try:
            all_images = list(self.image_dir.rglob("*.png"))
            total_size = sum(f.stat().st_size for f in all_images)

            return {
                'total_images': len(all_images),
                'total_size_mb': total_size / (1024 * 1024),
                'official_artwork_count': len(list(self.official_artwork_dir.glob("*.png")))
            }
        except Exception:
            return {'error': 'Could not get image cache stats'}


class CacheManager:
    """Main cache manager coordinating all cache layers."""

    def __init__(self, cache_dir: str = "data/cache", memory_size: int = 1000, file_size_mb: int = 100):
        self.memory_cache = MemoryCache(max_size=memory_size)
        self.file_cache = FileCache(cache_dir=cache_dir, max_size_mb=file_size_mb)
        self.image_cache = ImageCache()

    def get_pokemon_data(self, pokemon_id: int) -> Optional[Any]:
        """Get Pokemon data from cache (memory -> file)."""
        key = CACHE_KEYS['pokemon'].format(id=pokemon_id)

        # Try memory cache first
        data = self.memory_cache.get(key)
        if data is not None:
            return data

        # Try file cache
        data = self.file_cache.get(key)
        if data is not None:
            # Store back in memory cache
            self.memory_cache.set(key, data)
            return data

        return None

    def set_pokemon_data(self, pokemon_id: int, data: Any, ttl_hours: int = 24) -> None:
        """Store Pokemon data in both memory and file cache."""
        key = CACHE_KEYS['pokemon'].format(id=pokemon_id)
        self.memory_cache.set(key, data, ttl_hours)
        self.file_cache.set(key, data, ttl_hours)

    def get_species_data(self, pokemon_id: int) -> Optional[Any]:
        """Get Pokemon species data from cache."""
        key = CACHE_KEYS['species'].format(id=pokemon_id)
        return self.memory_cache.get(key) or self.file_cache.get(key)

    def set_species_data(self, pokemon_id: int, data: Any, ttl_hours: int = 24) -> None:
        """Store Pokemon species data in cache."""
        key = CACHE_KEYS['species'].format(id=pokemon_id)
        self.memory_cache.set(key, data, ttl_hours)
        self.file_cache.set(key, data, ttl_hours)

    def get_generation_data(self, generation: int) -> Optional[Any]:
        """Get generation data from cache."""
        key = CACHE_KEYS['generation'].format(id=generation)
        return self.memory_cache.get(key) or self.file_cache.get(key)

    def set_generation_data(self, generation: int, data: Any, ttl_hours: int = 48) -> None:
        """Store generation data in cache."""
        key = CACHE_KEYS['generation'].format(id=generation)
        self.memory_cache.set(key, data, ttl_hours)
        self.file_cache.set(key, data, ttl_hours)

    def has_pokemon_image(self, pokemon_id: int) -> bool:
        """Check if Pokemon image exists in cache."""
        return self.image_cache.has_image(pokemon_id)

    def get_pokemon_image_path(self, pokemon_id: int) -> Optional[Path]:
        """Get Pokemon image path from cache."""
        return self.image_cache.get_image_path(pokemon_id)

    def store_pokemon_image(self, pokemon_id: int, image_data: bytes) -> Path:
        """Store Pokemon image in cache."""
        return self.image_cache.store_image(pokemon_id, image_data)

    def clear_all(self) -> None:
        """Clear all caches."""
        self.memory_cache.clear()
        self.file_cache.clear()
        self.image_cache.clear_images()

    def clear_expired(self) -> Dict[str, int]:
        """Clear expired entries from all caches."""
        # Memory cache automatically removes expired items on access
        # File cache expired items are removed when accessed

        stats = {
            'memory_cleared': 0,
            'files_cleared': 0
        }

        # For file cache, manually check and remove expired files
        try:
            for file_path in self.file_cache.api_cache_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)

                    if 'expires_at' in data and data['expires_at']:
                        expires_at = datetime.fromisoformat(data['expires_at'])
                        if datetime.now() > expires_at:
                            file_path.unlink()
                            stats['files_cleared'] += 1
                except Exception:
                    # If we can't read the file, consider it corrupted and remove it
                    file_path.unlink()
                    stats['files_cleared'] += 1
        except Exception as e:
            log_error(CacheError('clear_expired', 'files', str(e)))

        return stats

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all cache layers."""
        return {
            'memory_cache': self.memory_cache.get_stats(),
            'file_cache': self.file_cache.get_stats(),
            'image_cache': self.image_cache.get_stats(),
            'timestamp': datetime.now().isoformat()
        }


# Global cache manager instance
cache_manager = CacheManager()