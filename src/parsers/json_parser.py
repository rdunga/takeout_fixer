from pathlib import Path

class JSONParser:

    def Parse(self, json_path: str | Path ) :

        # Take the jsonpath for the metadata file.
        # Parse the file and convert it into a metadata object.
        # Make sure to log if files cannot be converted to metadata object.
        # Use a debug mode, that gives out the stats of what can be converted.

        #. Check if the file exists
        #. Read the Json file using the input path
        #. 