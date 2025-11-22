"""
Models package for Google Takeout Fixer
Contains core data models for media files and metadata
"""

from .metadata import Metadata, GPSCoordinates
from .media_file import MediaFile, MediaType, MediaFileCollection

__all__ = [
    'Metadata',
    'GPSCoordinates',
    'MediaFile',
    'MediaType',
    'MediaFileCollection'
]