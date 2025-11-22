"""
Metadata model for representing photo/video metadata
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class GPSCoordinates:
    """Represents GPS coordinates with latitude, longitude, and optional altitude"""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    
    def __post_init__(self):
        """Validate GPS coordinates"""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")
    
    @property
    def latitude_ref(self) -> str:
        """Return 'N' for North or 'S' for South"""
        return 'N' if self.latitude >= 0 else 'S'
    
    @property
    def longitude_ref(self) -> str:
        """Return 'E' for East or 'W' for West"""
        return 'E' if self.longitude >= 0 else 'W'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'latitude': abs(self.latitude),
            'longitude': abs(self.longitude),
            'latitude_ref': self.latitude_ref,
            'longitude_ref': self.longitude_ref,
            'altitude': self.altitude
        }
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        lat_dir = 'N' if self.latitude >= 0 else 'S'
        lon_dir = 'E' if self.longitude >= 0 else 'W'
        return f"{abs(self.latitude):.6f}°{lat_dir}, {abs(self.longitude):.6f}°{lon_dir}"


class Metadata:
    """Represents metadata extracted from Google Takeout JSON or EXIF data"""
    
    def __init__(
        self,
        datetime_original: Optional[datetime] = None,
        gps_coordinates: Optional[GPSCoordinates] = None,
        description: Optional[str] = None,
        title: Optional[str] = None,
        camera_make: Optional[str] = None,
        camera_model: Optional[str] = None
    ):
        self._datetime_original = datetime_original
        self._gps_coordinates = gps_coordinates
        self._description = description
        self._title = title
        self._camera_make = camera_make
        self._camera_model = camera_model
    
    # Properties with getters and setters
    @property
    def datetime_original(self) -> Optional[datetime]:
        """Get the original datetime when photo/video was taken"""
        return self._datetime_original
    
    @datetime_original.setter
    def datetime_original(self, value: Optional[datetime]):
        """Set the original datetime"""
        if value is not None and not isinstance(value, datetime):
            raise TypeError("datetime_original must be a datetime object")
        self._datetime_original = value
    
    @property
    def gps_coordinates(self) -> Optional[GPSCoordinates]:
        """Get GPS coordinates"""
        return self._gps_coordinates
    
    @gps_coordinates.setter
    def gps_coordinates(self, value: Optional[GPSCoordinates]):
        """Set GPS coordinates"""
        if value is not None and not isinstance(value, GPSCoordinates):
            raise TypeError("gps_coordinates must be a GPSCoordinates object")
        self._gps_coordinates = value
    
    @property
    def description(self) -> Optional[str]:
        """Get description/caption"""
        return self._description
    
    @description.setter
    def description(self, value: Optional[str]):
        """Set description/caption"""
        self._description = value
    
    @property
    def title(self) -> Optional[str]:
        """Get title"""
        return self._title
    
    @title.setter
    def title(self, value: Optional[str]):
        """Set title"""
        self._title = value
    
    @property
    def camera_make(self) -> Optional[str]:
        """Get camera manufacturer"""
        return self._camera_make
    
    @camera_make.setter
    def camera_make(self, value: Optional[str]):
        """Set camera manufacturer"""
        self._camera_make = value
    
    @property
    def camera_model(self) -> Optional[str]:
        """Get camera model"""
        return self._camera_model
    
    @camera_model.setter
    def camera_model(self, value: Optional[str]):
        """Set camera model"""
        self._camera_model = value
    
    # Validation methods
    def is_valid(self) -> bool:
        """Check if metadata has at least some useful information"""
        return any([
            self._datetime_original is not None,
            self._gps_coordinates is not None,
            self._description is not None,
            self._title is not None
        ])
    
    def has_datetime(self) -> bool:
        """Check if datetime information exists"""
        return self._datetime_original is not None
    
    def has_gps(self) -> bool:
        """Check if GPS information exists"""
        return self._gps_coordinates is not None
    
    def has_description(self) -> bool:
        """Check if description exists"""
        return self._description is not None and len(self._description.strip()) > 0
    
    # Conversion methods
    def to_exif_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to EXIF-compatible dictionary for exiftool
        Returns dict with EXIF tag names as keys
        """
        exif_dict = {}
        
        # DateTime fields
        if self._datetime_original:
            dt_str = self._datetime_original.strftime('%Y:%m:%d %H:%M:%S')
            exif_dict['DateTimeOriginal'] = dt_str
            exif_dict['CreateDate'] = dt_str
            exif_dict['ModifyDate'] = dt_str
        
        # GPS fields
        if self._gps_coordinates:
            gps_dict = self._gps_coordinates.to_dict()
            exif_dict['GPSLatitude'] = gps_dict['latitude']
            exif_dict['GPSLongitude'] = gps_dict['longitude']
            exif_dict['GPSLatitudeRef'] = gps_dict['latitude_ref']
            exif_dict['GPSLongitudeRef'] = gps_dict['longitude_ref']
            if gps_dict['altitude'] is not None:
                exif_dict['GPSAltitude'] = gps_dict['altitude']
        
        # Description fields
        if self._description:
            exif_dict['ImageDescription'] = self._description
            exif_dict['Caption-Abstract'] = self._description
            exif_dict['UserComment'] = self._description
        
        # Title
        if self._title:
            exif_dict['Title'] = self._title
        
        # Camera info
        if self._camera_make:
            exif_dict['Make'] = self._camera_make
        if self._camera_model:
            exif_dict['Model'] = self._camera_model
        
        return exif_dict
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dictionary for serialization/logging"""
        return {
            'datetime_original': self._datetime_original.isoformat() if self._datetime_original else None,
            'gps_coordinates': str(self._gps_coordinates) if self._gps_coordinates else None,
            'description': self._description,
            'title': self._title,
            'camera_make': self._camera_make,
            'camera_model': self._camera_model
        }
    
    # Merge method for combining metadata from multiple sources
    def merge_with(self, other: 'Metadata', prefer_other: bool = False) -> 'Metadata':
        """
        Merge this metadata with another Metadata object
        
        Args:
            other: Another Metadata object to merge with
            prefer_other: If True, prefer values from 'other' when both exist
        
        Returns:
            New Metadata object with merged values
        """
        if prefer_other:
            return Metadata(
                datetime_original=other._datetime_original or self._datetime_original,
                gps_coordinates=other._gps_coordinates or self._gps_coordinates,
                description=other._description or self._description,
                title=other._title or self._title,
                camera_make=other._camera_make or self._camera_make,
                camera_model=other._camera_model or self._camera_model
            )
        else:
            return Metadata(
                datetime_original=self._datetime_original or other._datetime_original,
                gps_coordinates=self._gps_coordinates or other._gps_coordinates,
                description=self._description or other._description,
                title=self._title or other._title,
                camera_make=self._camera_make or other._camera_make,
                camera_model=self._camera_model or other._camera_model
            )
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        parts = []
        if self._datetime_original:
            parts.append(f"Date: {self._datetime_original.strftime('%Y-%m-%d %H:%M:%S')}")
        if self._gps_coordinates:
            parts.append(f"GPS: {self._gps_coordinates}")
        if self._description:
            desc_preview = self._description[:50] + "..." if len(self._description) > 50 else self._description
            parts.append(f"Description: {desc_preview}")
        if self._title:
            parts.append(f"Title: {self._title}")
        
        return "Metadata(" + ", ".join(parts) + ")" if parts else "Metadata(empty)"
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (f"Metadata(datetime_original={self._datetime_original!r}, "
                f"gps_coordinates={self._gps_coordinates!r}, "
                f"description={self._description!r}, "
                f"title={self._title!r})")