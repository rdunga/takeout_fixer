"""
Demo script showing how to use the MediaFile and Metadata models
Run this to test the models before building the rest of the system
"""

from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path to import models
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models import MediaFile, Metadata, GPSCoordinates, MediaFileCollection


def demo_metadata():
    """Demonstrate Metadata class usage"""
    print("=" * 60)
    print("METADATA CLASS DEMO")
    print("=" * 60)
    
    # Create GPS coordinates
    gps = GPSCoordinates(
        latitude=37.7749,
        longitude=-122.4194,
        altitude=50.0
    )
    print(f"\n1. GPS Coordinates: {gps}")
    print(f"   Latitude Ref: {gps.latitude_ref}")
    print(f"   Longitude Ref: {gps.longitude_ref}")
    
    # Create metadata
    metadata = Metadata(
        datetime_original=datetime(2023, 6, 15, 14, 30, 0),
        gps_coordinates=gps,
        description="Beautiful sunset at Golden Gate Bridge",
        title="Sunset Photo",
        camera_make="Apple",
        camera_model="iPhone 14 Pro"
    )
    
    print(f"\n2. Metadata Object: {metadata}")
    print(f"   Is Valid: {metadata.is_valid()}")
    print(f"   Has DateTime: {metadata.has_datetime()}")
    print(f"   Has GPS: {metadata.has_gps()}")
    
    # Convert to EXIF format
    exif_dict = metadata.to_exif_dict()
    print(f"\n3. EXIF Dictionary:")
    for key, value in exif_dict.items():
        print(f"   {key}: {value}")
    
    # Merge metadata
    other_metadata = Metadata(
        description="Updated description",
        title="New Title"
    )
    merged = metadata.merge_with(other_metadata)
    print(f"\n4. Merged Metadata: {merged}")
    
    return metadata


def demo_media_file(sample_file_path: str):
    """Demonstrate MediaFile class usage"""
    print("\n" + "=" * 60)
    print("MEDIAFILE CLASS DEMO")
    print("=" * 60)
    
    try:
        # Create a MediaFile (this will fail if file doesn't exist)
        media = MediaFile(Path(sample_file_path))
        
        print(f"\n1. Basic Info:")
        print(f"   Filename: {media.filename}")
        print(f"   Extension: {media.extension}")
        print(f"   Type: {media.media_type.value}")
        print(f"   Is Photo: {media.is_photo()}")
        print(f"   Is Video: {media.is_video()}")
        print(f"   Size: {media.size_mb:.2f} MB")
        
        print(f"\n2. Timestamps:")
        print(f"   Modified: {media.file_modified_time}")
        print(f"   Created: {media.file_created_time}")
        print(f"   Year/Month: {media.get_year_month_str()}")
        
        # Add metadata
        metadata = demo_metadata()
        media.metadata = metadata
        
        print(f"\n3. With Metadata:")
        print(f"   Has Metadata: {media.has_metadata()}")
        print(f"   Effective DateTime: {media.get_effective_datetime()}")
        print(f"   {media}")
        
        return media
        
    except FileNotFoundError:
        print(f"\n⚠️  File not found: {sample_file_path}")
        print("   This is expected if you haven't created a sample file yet")
        return None
    except ValueError as e:
        print(f"\n⚠️  Error: {e}")
        return None


def demo_collection():
    """Demonstrate MediaFileCollection usage"""
    print("\n" + "=" * 60)
    print("MEDIAFILECOLLECTION CLASS DEMO")
    print("=" * 60)
    
    collection = MediaFileCollection()
    print(f"\n1. Empty Collection: {collection}")
    
    # You would normally add real MediaFile objects here
    print("\n2. Collection Operations Available:")
    print("   - add(media_file)")
    print("   - get_photos()")
    print("   - get_videos()")
    print("   - get_with_metadata()")
    print("   - count_by_type()")
    print("   - count_by_year()")
    print("   - sort_by_date()")
    print("   - total_size_mb()")
    
    return collection


def main():
    """Main demo function"""
    print("\n🎯 Google Takeout Fixer - Models Demo\n")
    
    # Demo metadata
    demo_metadata()
    
    # Demo media file (you'll need to provide a real file path)
    print("\n\n📸 To test MediaFile, provide a path to an image:")
    print("   python examples/test_models.py /path/to/your/photo.jpg")
    
    if len(sys.argv) > 1:
        sample_file = sys.argv[1]
        demo_media_file(sample_file)
    else:
        print("\n⚠️  No file path provided, skipping MediaFile demo")
    
    # Demo collection
    demo_collection()
    
    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Test with your own photos from Takeout")
    print("2. Create the parsers to scan Takeout directories")
    print("3. Create the processors to inject metadata")
    print("\n")


if __name__ == '__main__':
    main()