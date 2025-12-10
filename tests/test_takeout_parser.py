#!/usr/bin/env python3
"""
Test script for TakeoutParser
Run this to verify the parser works with your Takeout data
"""

import sys
from pathlib import Path
import logging

# Add src directory to path so we can import our modules
# project_root = Path(__file__).parent
# sys.path.insert(0, str(project_root / 'src'))

from src.parsers.takeout_parser import TakeoutParser
from src.parsers.json_parser import JSONParser

# Setup nice logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

def main():
    print("=" * 70)
    print("TAKEOUT PARSER - Test Script")
    print("=" * 70)

    test_json_path = None
    
    # TODO: Change this to your actual Takeout path!
    takeout_path = input("\nEnter path to your Takeout folder: ").strip()
    
    # Remove quotes if user copy-pasted with quotes
    takeout_path = takeout_path.strip('"').strip("'")
    
    try:
        print("\n1. Creating parser...")
        parser = TakeoutParser(takeout_path)
        print("   ✓ Parser created successfully!")
        
        print("\n2. Getting summary...")
        print("-" * 70)
        print(parser.get_summary())
        
        print("\n3. Parsing all files (this may take a moment)...")
        print("-" * 70)
        media_collection, stats = parser.parse()
        
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        
        print(f"\nTotal albums scanned: {stats['albums_scanned']}")
        print(f"Total media files found: {stats['total_files']}")
        print(f"  ✓ With JSON metadata: {stats['files_with_json']}")
        print(f"  ⚠ Without JSON metadata: {stats['files_without_json']}")
        
        # Show breakdown by album
        print("\nBreakdown by album:")
        for album_name, album_stats in stats['albums'].items():
            print(f"\n  📁 {album_name}:")
            print(f"     Total: {album_stats['total_files']} files")
            print(f"     Photos: {album_stats['photos']}")
            print(f"     Videos: {album_stats['videos']}")
            print(f"     With JSON: {album_stats['with_json']}")
            print(f"     Without JSON: {album_stats['without_json']}")
        
        # Show sample files
        print("\n" + "=" * 70)
        print("SAMPLE FILES (first 10)")
        print("=" * 70)
        
        for i, media in enumerate(media_collection.files[:10]):
            print(f"\n{i+1}. {media.filename}")
            print(f"   Type: {media.media_type.value}")
            print(f"   Size: {media.size_mb:.2f} MB")
            print(f"   Path: {media.path.parent.name}/{media.filename}")
            if media.has_json_metadata():
                print(f"   ✓ JSON: {media.json_path.name}")
                test_json_path = media.json_path
            else:
                print(f"   ⚠ No JSON metadata found")
        
        if len(media_collection) > 10:
            print(f"\n... and {len(media_collection) - 10} more files")

        print(f"\n" + "=" * 70)
        print(f"Files without JSON:")
        
        for i, mdata in enumerate(media_collection.get_without_json()[:10]):
            print(f"\n{i+1}. {mdata.filename}")
            print(f"   Path: {mdata.path.parent.name}/{mdata.filename}")

        

        print("\n" + "=" * 70)
        print("✅ TEST COMPLETE!")
        print("=" * 70)
        print("\nThe parser is working correctly with your Takeout data.")
        print("Next step: Build the JSON parser to extract metadata from those JSON files.")

        print("\n" + "=" * 70)
        print("JSON PARSER TEST STARTED")
        print("\n" + "=" * 70)
        jp = JSONParser()
        print(test_json_path)
        m = jp.parse(test_json_path)
        print(m)


        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the path is correct and the Takeout folder exists.")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nCheck that your Takeout folder has the expected structure.")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()