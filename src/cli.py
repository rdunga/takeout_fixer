from .parsers import JSONParser, TakeoutParser
from typing import Tuple, List, Dict
from pathlib import Path
from models import MediaFileCollection, Metadata, MediaFile

def main(takeout_path : str, debug_mode : bool = False) -> bool:
    # Connect all the pieces here.
    
    p = Path(takeout_path)
    parser = TakeoutParser(p)
    print("Start reading the takeout package")
    print("\n" + "=" * 70)

    mediafileCollection, stats =  parser.parse()
   
    if debug_mode:
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
           
        print("\n" + "=" * 70)
            
 
    print("Start parsing the json side cars and get metadata")
    print("=" * 70)

    jp = JSONParser()
    
    for mfile in mediafileCollection.files:
        if mfile.has_json_metadata():
            metadataObj = jp.parse(mfile.json_path)
            mfile.metadata = metadataObj
            print(metadataObj)


if __name__  == "__main__":
    # call the main method
    takeout_path = input("\nEnter path to your Takeout folder: ").strip()
    debug_mode = True
    main(takeout_path, debug_mode)