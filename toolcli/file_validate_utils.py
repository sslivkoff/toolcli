from __future__ import annotations


def is_valid_file_path(path: str) -> bool:
    return isinstance(path, str) and path[0] not in ['/', '\\', '.']


def is_valid_directory_path(path: str) -> bool:
    return isinstance(path, str)

