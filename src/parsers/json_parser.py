"""
JSONParser - Extracts metadata from Google Takeout JSON files
"""

from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
import json
import logging

# Import our models
from models import Metadata, GPSCoordinates

logger = logging.getLogger(__name__)


class JSONParser:
    """Parse Google Takeout JSON files and extract metadata"""
    
    def parse(self, json_path: str | Path) -> Optional[Metadata]:
        """
        Parse a Google Takeout JSON file
        
        Args:
            json_path: Path to the JSON file
            
        Returns:
            Metadata object or None if parsing fails
        """
        p = Path(json_path)
        metadata_obj = None
        # Check if file exists
        if p.exists() and p.is_file():
            # Read and parse JSON
            try:
                with open(p, 'r') as f:
                    jsreader = json.load(f)

                    title = jsreader.get("title",None)

                    #default values for date and gps info
                    datetime_original = gps = None

                    phototakenTime_str = jsreader.get("photoTakenTime",{}).get("timestamp",None)
                    if phototakenTime_str:
                        datetime_original = datetime.fromtimestamp(int(phototakenTime_str), timezone.utc)

                    gdata = jsreader.get("geoData",{})
                    lat = gdata.get("latitude", None)
                    longitude = gdata.get("longitude",None)
                    if lat != 0.0 and longitude != 0.0:
                        gps = GPSCoordinates(gdata.get("latitude",None)
                                            ,gdata.get("longitude",None)
                                            ,gdata.get("altitude",None)
                                            )
                        
                    #TODO - what is latitude span in g takeout side car jsons.
                    desc = jsreader.get("description",None)

                    metadata_obj = Metadata(datetime_original,gps,desc,title,None,None)

            except Exception as e:
                print("Exception in json parser loading the json file." + e)
        
        return metadata_obj