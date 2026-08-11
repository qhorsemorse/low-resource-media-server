"""
Domain Layer - Custom Exceptions.
Python 3.11.2 Compatible.
"""

class MediaNotFoundException(Exception):
    """Raised when a media item or file does not exist."""
    def __init__(self, item_id: str):
        self.item_id = item_id
        super().__init__(f"Media item '{item_id}' not found.")


class InvalidRangeHeaderException(Exception):
    """Raised when an HTTP Range request header cannot be satisfied."""
    def __init__(self, file_size: int):
        self.file_size = file_size
        super().__init__(f"Range Not Satisfiable for file size {file_size}.")
