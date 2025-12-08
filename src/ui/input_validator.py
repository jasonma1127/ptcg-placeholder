"""
Input validation utilities for user interface.
"""

import re
from typing import List, Set, Optional
from src.utils.error_handler import ValidationError, validate_pokemon_id, validate_generation
from config.constants import GENERATION_RANGES, MAX_VALUES


class InputValidator:
    """Validator for user inputs in the menu system."""

    def __init__(self):
        self.max_pokemon_id = MAX_VALUES['POKEMON_ID']
        self.max_generation = MAX_VALUES['GENERATION']
        self.max_batch_size = MAX_VALUES['BATCH_SIZE']

    def parse_generation_input(self, input_str: str) -> List[int]:
        """
        Parse generation input string into list of generation numbers.

        Supports:
        - Single: "1"
        - Multiple: "1,2,3"
        - Range: "1-3"
        - Mixed: "1,3-5,7"
        """
        if not input_str or not input_str.strip():
            raise ValidationError("generation_input", input_str, "Input cannot be empty")

        generations = set()
        parts = input_str.strip().replace(' ', '').split(',')

        for part in parts:
            if not part:
                continue

            try:
                if '-' in part:
                    # Handle range (e.g., "1-3")
                    start_str, end_str = part.split('-', 1)
                    start = int(start_str)
                    end = int(end_str)

                    if start > end:
                        raise ValidationError(
                            "generation_range", part,
                            f"Invalid range: start ({start}) > end ({end})"
                        )

                    for gen in range(start, end + 1):
                        validate_generation(gen, self.max_generation)
                        generations.add(gen)
                else:
                    # Handle single number
                    gen = int(part)
                    validate_generation(gen, self.max_generation)
                    generations.add(gen)

            except ValueError:
                raise ValidationError("generation_input", part, f"'{part}' is not a valid number")

        return sorted(list(generations))

    def parse_pokemon_id_input(self, input_str: str) -> List[int]:
        """
        Parse Pokemon ID input string into list of Pokemon IDs.

        Supports:
        - Single: "25"
        - Multiple: "1,25,150"
        - Range: "1-10"
        - Mixed: "1,25,100-150"
        """
        if not input_str or not input_str.strip():
            raise ValidationError("pokemon_id_input", input_str, "Input cannot be empty")

        pokemon_ids = set()
        parts = input_str.strip().replace(' ', '').split(',')

        for part in parts:
            if not part:
                continue

            try:
                if '-' in part:
                    # Handle range (e.g., "1-10")
                    start_str, end_str = part.split('-', 1)
                    start = int(start_str)
                    end = int(end_str)

                    if start > end:
                        raise ValidationError(
                            "pokemon_id_range", part,
                            f"Invalid range: start ({start}) > end ({end})"
                        )

                    # Check for reasonable range size
                    range_size = end - start + 1
                    if range_size > self.max_batch_size:
                        raise ValidationError(
                            "pokemon_id_range", part,
                            f"Range too large ({range_size}). Maximum allowed: {self.max_batch_size}"
                        )

                    for pokemon_id in range(start, end + 1):
                        validate_pokemon_id(pokemon_id, self.max_pokemon_id)
                        pokemon_ids.add(pokemon_id)
                else:
                    # Handle single number
                    pokemon_id = int(part)
                    validate_pokemon_id(pokemon_id, self.max_pokemon_id)
                    pokemon_ids.add(pokemon_id)

            except ValueError:
                raise ValidationError("pokemon_id_input", part, f"'{part}' is not a valid number")

        # Check total count
        if len(pokemon_ids) > self.max_batch_size:
            raise ValidationError(
                "pokemon_id_batch", str(len(pokemon_ids)),
                f"Too many Pokemon IDs ({len(pokemon_ids)}). Maximum allowed: {self.max_batch_size}"
            )

        return sorted(list(pokemon_ids))

    def validate_language_code(self, language_code: str) -> bool:
        """Validate language code."""
        valid_languages = ['en', 'zh-Hant', 'ja']
        return language_code in valid_languages

    def validate_pokemon_name(self, name: str) -> bool:
        """Validate Pokemon name format."""
        if not name or not name.strip():
            return False

        # Basic validation - allow letters, numbers, spaces, hyphens
        pattern = r'^[A-Za-z0-9\s\-\'\.]{1,50}$'
        return bool(re.match(pattern, name.strip()))

    def parse_pokemon_name_input(self, input_str: str) -> List[str]:
        """Parse Pokemon name input (comma-separated)."""
        if not input_str or not input_str.strip():
            raise ValidationError("pokemon_name_input", input_str, "Input cannot be empty")

        names = []
        parts = [part.strip() for part in input_str.split(',')]

        for part in parts:
            if not part:
                continue

            if not self.validate_pokemon_name(part):
                raise ValidationError(
                    "pokemon_name", part,
                    "Name contains invalid characters or is too long"
                )

            names.append(part)

        if len(names) > self.max_batch_size:
            raise ValidationError(
                "pokemon_name_batch", str(len(names)),
                f"Too many names ({len(names)}). Maximum allowed: {self.max_batch_size}"
            )

        return names

    def validate_file_path(self, file_path: str, extension: str = None) -> bool:
        """Validate file path format."""
        if not file_path or not file_path.strip():
            return False

        # Basic path validation
        path_pattern = r'^[A-Za-z0-9\s\-_/\\\.]{1,255}$'
        if not re.match(path_pattern, file_path):
            return False

        if extension:
            return file_path.lower().endswith(extension.lower())

        return True

    def normalize_pokemon_name(self, name: str) -> str:
        """Normalize Pokemon name for search."""
        if not name:
            return ""

        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^\w\s-]', '', name.lower())

        # Replace multiple spaces/hyphens with single space
        normalized = re.sub(r'[\s\-]+', ' ', normalized)

        return normalized.strip()

    def validate_generation_list(self, generations: List[int]) -> bool:
        """Validate a list of generations."""
        if not generations:
            return False

        try:
            for gen in generations:
                validate_generation(gen, self.max_generation)
            return True
        except ValidationError:
            return False

    def validate_pokemon_id_list(self, pokemon_ids: List[int]) -> bool:
        """Validate a list of Pokemon IDs."""
        if not pokemon_ids:
            return False

        if len(pokemon_ids) > self.max_batch_size:
            return False

        try:
            for pokemon_id in pokemon_ids:
                validate_pokemon_id(pokemon_id, self.max_pokemon_id)
            return True
        except ValidationError:
            return False

    def get_generation_pokemon_count(self, generations: List[int]) -> int:
        """Calculate total Pokemon count for given generations."""
        total = 0
        for gen in generations:
            if gen in GENERATION_RANGES:
                start, end = GENERATION_RANGES[gen]
                total += end - start + 1
        return total

    def suggest_valid_generations(self, invalid_input: str) -> List[int]:
        """Suggest valid generations based on invalid input."""
        suggestions = []

        # Try to extract numbers from input
        numbers = re.findall(r'\d+', invalid_input)

        for num_str in numbers:
            try:
                num = int(num_str)
                if 1 <= num <= self.max_generation:
                    suggestions.append(num)
            except ValueError:
                continue

        return suggestions

    def suggest_valid_pokemon_ids(self, invalid_input: str) -> List[int]:
        """Suggest valid Pokemon IDs based on invalid input."""
        suggestions = []

        # Try to extract numbers from input
        numbers = re.findall(r'\d+', invalid_input)

        for num_str in numbers:
            try:
                num = int(num_str)
                if 1 <= num <= self.max_pokemon_id:
                    suggestions.append(num)
            except ValueError:
                continue

        return suggestions[:10]  # Limit suggestions

    def format_pokemon_id_list(self, pokemon_ids: List[int]) -> str:
        """Format Pokemon ID list for display."""
        if not pokemon_ids:
            return "None"

        if len(pokemon_ids) <= 10:
            return ", ".join(map(str, pokemon_ids))
        else:
            displayed = ", ".join(map(str, pokemon_ids[:10]))
            return f"{displayed} ... (and {len(pokemon_ids) - 10} more)"

    def format_generation_list(self, generations: List[int]) -> str:
        """Format generation list for display."""
        if not generations:
            return "None"

        # Group consecutive generations
        groups = []
        start = generations[0]
        end = start

        for i in range(1, len(generations)):
            if generations[i] == end + 1:
                end = generations[i]
            else:
                if start == end:
                    groups.append(str(start))
                else:
                    groups.append(f"{start}-{end}")
                start = generations[i]
                end = start

        # Add final group
        if start == end:
            groups.append(str(start))
        else:
            groups.append(f"{start}-{end}")

        return ", ".join(groups)

    def validate_card_settings(self, settings_dict: dict) -> List[str]:
        """Validate card generation settings."""
        errors = []

        # Check language
        language = settings_dict.get('language')
        if language and not self.validate_language_code(language):
            errors.append(f"Invalid language code: {language}")

        # Check Pokemon IDs
        pokemon_ids = settings_dict.get('pokemon_ids', [])
        if pokemon_ids and not self.validate_pokemon_id_list(pokemon_ids):
            errors.append("Invalid Pokemon ID list")

        # Check generations
        generations = settings_dict.get('generations', [])
        if generations and not self.validate_generation_list(generations):
            errors.append("Invalid generation list")

        return errors


# Global validator instance
input_validator = InputValidator()