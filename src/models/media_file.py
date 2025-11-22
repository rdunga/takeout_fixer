"""
MediaFile model for representing a photo or video file with its associated metadata
"""
from pathlib import Path
from datetime import datetime
from typing import Optional, Set
from enum import Enum
import os

from .metadata import Metadata


class MediaType(Enum):
    """Enum for different media types"""
    PHOTO = "photo"
    VIDEO = "video"
    UNKNOWN = "unknown"


class MediaFile:
    """
    Represents a media file (photo or video) with its associated metadata
    
    Attributes:
        path: Path to the media file
        json_path: Optional path to associated JSON metadata file
        metadata: Metadata object containing extracted information
    """
    
    # Supported file extensions
    PHOTO_EXTENSIONS: Set[str] = {'.jpg', '.jpeg', '.png', '.gif', '.heic', '.heif', '.webp', '.bmp', '.tiff'}
    VIDEO_EXTENSIONS: Set[str] = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.3gp', '.wmv'}
    
    def __init__(self, path: Path, json_path: Optional[Path] = None):
        """
        Initialize a MediaFile
        
        Args:
            path: Path to the media file
            json_path: Optional path to JSON metadata file
        
        Raises:
            FileNotFoundError: If the media file doesn't exist
            ValueError: If the file is not a supported media type
        """
        self._path = Path(path)
        self._json_path = Path(json_path) if json_path else None
        self._metadata: Optional[Metadata] = None
        
        # Validate file exists
        if not self._path.exists():
            raise FileNotFoundError(f"Media file not found: {self._path}")
        
        # Validate it's a file, not a directory
        if not self._path.is_file():
            raise ValueError(f"Path is not a file: {self._path}")
        
        # Validate supported media type
        if not self.is_supported_media():
            raise ValueError(f"Unsupported file type: {self._path.suffix}")
    
    # Properties
    @property
    def path(self) -> Path:
        """Get the file path"""
        return self._path
    
    @property
    def json_path(self) -> Optional[Path]:
        """Get the JSON metadata file path"""
        return self._json_path
    
    @json_path.setter
    def json_path(self, value: Optional[Path]):
        """Set the JSON metadata file path"""
        if value is not None:
            value = Path(value)
            if not value.exists():
                raise FileNotFoundError(f"JSON file not found: {value}")
        self._json_path = value
    
    @property
    def metadata(self) -> Optional[Metadata]:
        """Get the metadata object"""
        return self._metadata
    
    @metadata.setter
    def metadata(self, value: Optional[Metadata]):
        """Set the metadata object"""
        if value is not None and not isinstance(value, Metadata):
            raise TypeError("metadata must be a Metadata object")
        self._metadata = value
    
    @property
    def filename(self) -> str:
        """Get the filename without path"""
        return self._path.name
    
    @property
    def extension(self) -> str:
        """Get the file extension (lowercase)"""
        return self._path.suffix.lower()
    
    @property
    def stem(self) -> str:
        """Get the filename without extension"""
        return self._path.stem
    
    @property
    def size_bytes(self) -> int:
        """Get file size in bytes"""
        return self._path.stat().st_size
    
    @property
    def size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.size_bytes / (1024 * 1024)
    
    @property
    def file_modified_time(self) -> datetime:
        """Get file modification time"""
        return datetime.fromtimestamp(self._path.stat().st_mtime)
    
    @property
    def file_created_time(self) -> datetime:
        """Get file creation time"""
        return datetime.fromtimestamp(self._path.stat().st_ctime)
    
    # Type checking methods
    @property
    def media_type(self) -> MediaType:
        """Determine if this is a photo, video, or unknown"""
        ext = self.extension
        if ext in self.PHOTO_EXTENSIONS:
            return MediaType.PHOTO
        elif ext in self.VIDEO_EXTENSIONS:
            return MediaType.VIDEO
        else:
            return MediaType.UNKNOWN
    
    def is_photo(self) -> bool:
        """Check if this is a photo"""
        return self.media_type == MediaType.PHOTO
    
    def is_video(self) -> bool:
        """Check if this is a video"""
        return self.media_type == MediaType.VIDEO
    
    def is_supported_media(self) -> bool:
        """Check if this file type is supported"""
        return self.extension in (self.PHOTO_EXTENSIONS | self.VIDEO_EXTENSIONS)
    
    # Metadata methods
    def has_metadata(self) -> bool:
        """Check if metadata has been loaded and is valid"""
        return self._metadata is not None and self._metadata.is_valid()
    
    def has_json_metadata(self) -> bool:
        """Check if there's an associated JSON file"""
        return self._json_path is not None and self._json_path.exists()
    
    # Date/time helpers
    def get_effective_datetime(self) -> datetime:
        """
        Get the most appropriate datetime for this file
        Priority: metadata datetime > file modified time
        """
        if self._metadata and self._metadata.datetime_original:
            return self._metadata.datetime_original
        return self.file_modified_time
    
    def get_year(self) -> int:
        """Get the year from effective datetime"""
        return self.get_effective_datetime().year
    
    def get_month(self) -> int:
        """Get the month from effective datetime"""
        return self.get_effective_datetime().month
    
    def get_year_month_str(self) -> str:
        """Get year/month as string (e.g., '2023/03')"""
        dt = self.get_effective_datetime()
        return f"{dt.year}/{dt.month:02d}"
    
    # File operations
    def generate_unique_filename(self, target_dir: Path) -> Path:
        """
        Generate a unique filename in the target directory
        Adds _1, _2, etc. if file already exists
        
        Args:
            target_dir: Directory where file will be placed
        
        Returns:
            Unique Path object for the target file
        """
        target_file = target_dir / self.filename
        
        if not target_file.exists():
            return target_file
        
        # File exists, add counter
        counter = 1
        while True:
            new_filename = f"{self.stem}_{counter}{self.extension}"
            target_file = target_dir / new_filename
            if not target_file.exists():
                return target_file
            counter += 1
    
    # String representations
    def __str__(self) -> str:
        """Human-readable string representation"""
        info = [
            f"File: {self.filename}",
            f"Type: {self.media_type.value}",
            f"Size: {self.size_mb:.2f} MB"
        ]
        
        if self.has_json_metadata():
            info.append("Has JSON")
        
        if self.has_metadata():
            info.append(f"Metadata: {self._metadata}")
        
        return " | ".join(info)
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (f"MediaFile(path={self._path!r}, "
                f"json_path={self._json_path!r}, "
                f"has_metadata={self.has_metadata()})")
    
    # Comparison methods (for sorting)
    def __lt__(self, other: 'MediaFile') -> bool:
        """Compare by effective datetime for sorting"""
        if not isinstance(other, MediaFile):
            return NotImplemented
        return self.get_effective_datetime() < other.get_effective_datetime()
    
    def __eq__(self, other: object) -> bool:
        """Compare by file path"""
        if not isinstance(other, MediaFile):
            return NotImplemented
        return self._path == other._path
    
    def __hash__(self) -> int:
        """Hash by file path"""
        return hash(self._path)


class MediaFileCollection:
    """
    Collection of MediaFile objects with useful operations
    Useful for batch operations and statistics
    """
    
    def __init__(self):
        self._files: list[MediaFile] = []
    
    def add(self, media_file: MediaFile) -> None:
        """Add a media file to the collection"""
        if not isinstance(media_file, MediaFile):
            raise TypeError("Can only add MediaFile objects")
        self._files.append(media_file)
    
    def extend(self, media_files: list[MediaFile]) -> None:
        """Add multiple media files"""
        for mf in media_files:
            self.add(mf)
    
    @property
    def files(self) -> list[MediaFile]:
        """Get all files"""
        return self._files
    
    def __len__(self) -> int:
        """Get count of files"""
        return len(self._files)
    
    def __iter__(self):
        """Make collection iterable"""
        return iter(self._files)
    
    # Filter methods
    def get_photos(self) -> list[MediaFile]:
        """Get only photo files"""
        return [f for f in self._files if f.is_photo()]
    
    def get_videos(self) -> list[MediaFile]:
        """Get only video files"""
        return [f for f in self._files if f.is_video()]
    
    def get_with_metadata(self) -> list[MediaFile]:
        """Get files that have metadata"""
        return [f for f in self._files if f.has_metadata()]
    
    def get_without_metadata(self) -> list[MediaFile]:
        """Get files without metadata"""
        return [f for f in self._files if not f.has_metadata()]
    
    def get_with_json(self) -> list[MediaFile]:
        """Get files that have JSON sidecar files"""
        return [f for f in self._files if f.has_json_metadata()]
    
    def get_without_json(self) -> list[MediaFile]:
        """Get files without JSON sidecar files"""
        return [f for f in self._files if not f.has_json_metadata()]
    
    # Statistics
    def total_size_mb(self) -> float:
        """Get total size of all files in MB"""
        return sum(f.size_mb for f in self._files)
    
    def count_by_type(self) -> dict[str, int]:
        """Count files by media type"""
        return {
            'photos': len(self.get_photos()),
            'videos': len(self.get_videos()),
            'total': len(self._files)
        }
    
    def count_by_year(self) -> dict[int, int]:
        """Count files by year"""
        year_counts = {}
        for f in self._files:
            year = f.get_year()
            year_counts[year] = year_counts.get(year, 0) + 1
        return dict(sorted(year_counts.items()))
    
    # Sorting
    def sort_by_date(self, reverse: bool = False) -> None:
        """Sort files by effective datetime"""
        self._files.sort(reverse=reverse)
    
    def sort_by_size(self, reverse: bool = True) -> None:
        """Sort files by size (largest first by default)"""
        self._files.sort(key=lambda f: f.size_bytes, reverse=reverse)
    
    def __str__(self) -> str:
        """Human-readable summary"""
        counts = self.count_by_type()
        return (f"MediaFileCollection: {counts['total']} files "
                f"({counts['photos']} photos, {counts['videos']} videos), "
                f"Total size: {self.total_size_mb():.2f} MB")