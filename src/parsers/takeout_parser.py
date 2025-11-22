"""
TakeoutParser - Scans Google Takeout directory and finds media files with metadata

Structure we're handling:
Takeout/
└── Google Photos/
    ├── Album1/
    │   ├── photo.jpg
    │   └── photo.jpg.json (or .supplemental-metadata.json.json)
    ├── Album2/
    └── ...
"""

from pathlib import Path
from typing import List, Tuple, Optional
import logging

# Import our models
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import MediaFile, MediaFileCollection

logger = logging.getLogger(__name__)


class TakeoutParser:
    """
    Parses Google Takeout directory structure and finds media files with their JSON metadata
    
    Attributes:
        takeout_dir: Path to the Takeout directory
        google_photos_dir: Path to Google Photos folder inside Takeout
    """
    
    # JSON file suffixes that Google uses
    JSON_SUFFIXES = [
        '.json',                        # Standard format
        '.supplemental-metadata.json',     # Supplemental metadata (your format!)
        '.jpg.json',                    # Sometimes duplicated extension
        '.png.json',
        '.mp4.json',
        '.supplemental-met.json',
        '.supplemental-metad.json'
    ]
    
    # Files to ignore (album-level metadata, not photo metadata)
    IGNORED_FILES = {
        'metadata.json',                # Album metadata
        'Metadata.json',                # Case variation
        'print-subscriptions.json',     # Other Google metadata
        'shared_album_comments.json',
    }
    
    def __init__(self, takeout_dir: str | Path):
        """
        Initialize the parser
        
        Args:
            takeout_dir: Path to the Takeout directory
            
        Raises:
            FileNotFoundError: If takeout directory doesn't exist
            ValueError: If Google Photos folder not found
        """
        self.takeout_dir = Path(takeout_dir)
        
        # Validate takeout directory exists
        if not self.takeout_dir.exists():
            raise FileNotFoundError(f"Takeout directory not found: {self.takeout_dir}")
        
        if not self.takeout_dir.is_dir():
            raise ValueError(f"Path is not a directory: {self.takeout_dir}")
        
        # Find Google Photos folder
        self.google_photos_dir = self._find_google_photos_dir()
        
        logger.info(f"TakeoutParser initialized for: {self.takeout_dir}")
        logger.info(f"Google Photos directory: {self.google_photos_dir}")
    
    def _find_google_photos_dir(self) -> Path:
        """
        Find the Google Photos directory inside Takeout
        
        Returns:
            Path to Google Photos directory
            
        Raises:
            ValueError: If Google Photos directory not found
        """
        # Try common names
        possible_names = [
            'Google Photos',
            'Google Foto',  # Non-English versions
            'Photos',
        ]
        
        for name in possible_names:
            photos_dir = self.takeout_dir / name
            if photos_dir.exists() and photos_dir.is_dir():
                return photos_dir
        
        # If not found, list what we have
        available = [d.name for d in self.takeout_dir.iterdir() if d.is_dir()]
        raise ValueError(
            f"Google Photos directory not found in {self.takeout_dir}\n"
            f"Available directories: {available}"
        )
    
    def _find_json_for_media(self, media_path: Path) -> Optional[Path]:
        """
        Find JSON metadata file for a given media file
        
        Tries multiple naming patterns:
        - photo.jpg.json
        - photo.jpg.supplemental-metadata.json.json
        - photo.json
        
        Args:
            media_path: Path to media file
            
        Returns:
            Path to JSON file if found, None otherwise
        """
        # Pattern 1: media_path + suffix (e.g., photo.jpg.json)
        for suffix in self.JSON_SUFFIXES:
            json_path = media_path.parent / f"{media_path.name}{suffix}"
            if json_path.exists():
                return json_path
        
        # Pattern 2: Replace extension with .json (e.g., photo.json)
        json_path = media_path.with_suffix('.json')
        if json_path.exists():
            return json_path
        
        # Pattern 3: Stem + .json (e.g., for photo.jpg -> photo.json)
        json_path = media_path.parent / f"{media_path.stem}.json"
        if json_path.exists():
            return json_path
        
        return None
    
    def get_album_folders(self) -> List[Path]:
        """
        Get all album folders under Google Photos directory
        
        Returns:
            List of Path objects for each album folder
        """
        album_folders = []
        
        for item in self.google_photos_dir.iterdir():
            if item.is_dir():
                album_folders.append(item)
        
        logger.info(f"Found {len(album_folders)} album folders")
        return album_folders
    
    def scan_album(self, album_path: Path) -> MediaFileCollection:
        """
        Scan a single album folder for media files
        
        Args:
            album_path: Path to album folder
            
        Returns:
            MediaFileCollection with files from this album
        """
        collection = MediaFileCollection()
        
        logger.info(f"Scanning album: {album_path.name}")
        
        # Get all files in album (not recursive - files are directly in album)
        for file_path in album_path.iterdir():
            if not file_path.is_file():
                continue
            
            # Skip album-level metadata files
            if file_path.name in self.IGNORED_FILES:
                logger.debug(f"  ⊝ Skipping album metadata: {file_path.name}")
                continue
            
            # Skip JSON files (we'll find them when processing media files)
            if any(str(file_path).endswith(suffix) for suffix in self.JSON_SUFFIXES):
                continue
            
            # Try to create MediaFile (validates it's a supported media type)
            try:
                media_file = MediaFile(file_path)
                
                # Try to find JSON metadata
                json_path = self._find_json_for_media(file_path)
                if json_path:
                    media_file.json_path = json_path
                    logger.debug(f"  ✓ {file_path.name} (has JSON)")
                else:
                    logger.debug(f"  ⚠ {file_path.name} (no JSON)")
                
                collection.add(media_file)
                
            except ValueError as e:
                # Not a supported media file, skip it
                logger.debug(f"  ✗ Skipping {file_path.name}: {e}")
                continue
        
        return collection
    
    def parse(self) -> Tuple[MediaFileCollection, dict]:
        """
        Parse the entire Takeout directory
        
        Returns:
            Tuple of:
            - MediaFileCollection with all media files found
            - Dictionary with statistics
        """
        logger.info("Starting Takeout parsing...")
        
        all_media = MediaFileCollection()
        stats = {
            'albums_scanned': 0,
            'files_with_json': 0,
            'files_without_json': 0,
            'total_files': 0,
            'albums': {}
        }
        
        # Get all album folders
        album_folders = self.get_album_folders()
        
        # Scan each album
        for album_path in album_folders:
            album_name = album_path.name
            logger.info(f"\nScanning album: {album_name}")
            
            album_collection = self.scan_album(album_path)
            
            # Add to overall collection
            all_media.extend(album_collection.files)
            
            # Update stats
            stats['albums_scanned'] += 1
            stats['albums'][album_name] = {
                'total_files': len(album_collection),
                'with_json': len(album_collection.get_with_json()),
                'without_json': len(album_collection.get_without_json()),
                'photos': len(album_collection.get_photos()),
                'videos': len(album_collection.get_videos()),
            }
            
            logger.info(f"  Found {len(album_collection)} files "
                       f"({len(album_collection.get_with_json())} with JSON)")
        
        # Calculate overall stats
        stats['total_files'] = len(all_media)
        stats['files_with_json'] = len(all_media.get_with_json())
        stats['files_without_json'] = len(all_media.get_without_json())
        
        logger.info("\n" + "=" * 60)
        logger.info("PARSING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total albums: {stats['albums_scanned']}")
        logger.info(f"Total files: {stats['total_files']}")
        logger.info(f"  With JSON: {stats['files_with_json']}")
        logger.info(f"  Without JSON: {stats['files_without_json']}")
        
        return all_media, stats
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the Takeout structure
        
        Returns:
            Formatted string with summary
        """
        album_folders = self.get_album_folders()
        
        summary = []
        summary.append(f"Takeout Directory: {self.takeout_dir}")
        summary.append(f"Google Photos: {self.google_photos_dir}")
        summary.append(f"\nAlbums found ({len(album_folders)}):")
        
        for album in album_folders:
            # Count files in album
            files = [f for f in album.iterdir() if f.is_file()]
            media_count = sum(1 for f in files if not any(str(f).endswith(s) for s in self.JSON_SUFFIXES))
            json_count = sum(1 for f in files if any(str(f).endswith(s) for s in self.JSON_SUFFIXES))
            
            summary.append(f"  📁 {album.name}")
            summary.append(f"     Media files: {media_count}")
            summary.append(f"     JSON files: {json_count}")
        
        return "\n".join(summary)


# ============================================================================
# Example Usage / Testing
# ============================================================================

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("TAKEOUT PARSER - Test Run")
    print("=" * 70)
    
    # You'll need to change this path!
    takeout_path = "/path/to/your/Takeout"
    
    try:
        # Create parser
        parser = TakeoutParser(takeout_path)
        
        # Show summary
        print("\n" + parser.get_summary())
        
        # Parse all files
        print("\n\nParsing all files...")
        media_collection, stats = parser.parse()
        
        # Show some examples
        print("\n" + "=" * 70)
        print("SAMPLE FILES:")
        print("=" * 70)
        
        for i, media in enumerate(media_collection.files[:5]):
            print(f"\n{i+1}. {media.filename}")
            print(f"   Type: {media.media_type.value}")
            print(f"   Size: {media.size_mb:.2f} MB")
            print(f"   Has JSON: {media.has_json_metadata()}")
            if media.has_json_metadata():
                print(f"   JSON: {media.json_path.name}")
        
        if len(media_collection) > 5:
            print(f"\n... and {len(media_collection) - 5} more files")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()