"""
Color value type for Sass.
"""

import math
from typing import Optional, Union, Tuple, List
from .base import Value


class SassColor(Value):
    """
    A Sass color value.
    
    Colors can be represented in various formats (RGB, HSL, HWB, LAB, LCH, XYZ) 
    and support multiple color spaces like the Node.js implementation.
    """
    
    def __init__(
        self,
        red: Optional[float] = None,
        green: Optional[float] = None, 
        blue: Optional[float] = None,
        alpha: Optional[float] = None,
        hue: Optional[float] = None,
        saturation: Optional[float] = None,
        lightness: Optional[float] = None,
        whiteness: Optional[float] = None,
        blackness: Optional[float] = None,
        # Lab/LCH parameters
        a: Optional[float] = None,
        b: Optional[float] = None,
        chroma: Optional[float] = None,
        # XYZ parameters  
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
        space: str = 'rgb'
    ):
        """
        Initialize a SassColor.
        
        Can be initialized with RGB, HSL, HWB, LAB, LCH, or XYZ values.
        """
        self._space = space.lower()
        self._alpha = alpha
        
        # Store channels based on color space (like Node.js)
        if red is not None and green is not None and blue is not None:
            # RGB-like spaces
            self._channel1 = red
            self._channel2 = green  
            self._channel3 = blue
        elif hue is not None and saturation is not None and lightness is not None:
            # HSL space
            self._channel1 = hue
            self._channel2 = saturation
            self._channel3 = lightness
        elif hue is not None and whiteness is not None and blackness is not None:
            # HWB space
            self._channel1 = hue
            self._channel2 = whiteness
            self._channel3 = blackness
        elif lightness is not None and a is not None and b is not None:
            # LAB space
            self._channel1 = lightness
            self._channel2 = a
            self._channel3 = b
        elif lightness is not None and chroma is not None and hue is not None:
            # LCH space
            self._channel1 = lightness
            self._channel2 = chroma
            self._channel3 = hue
        elif x is not None and y is not None and z is not None:
            # XYZ space
            self._channel1 = x
            self._channel2 = y
            self._channel3 = z
        else:
            # Default to black in RGB
            self._channel1 = 0.0
            self._channel2 = 0.0
            self._channel3 = 0.0
    
    @property
    def space(self) -> str:
        """The color space (matches Node.js space property)."""
        return self._space
    
    @property
    def channels_or_null(self) -> List[Optional[float]]:
        """
        The color channels, with None for missing channels.
        (matches Node.js channelsOrNull property)
        """
        return [self._channel1, self._channel2, self._channel3]
    
    def is_channel_missing(self, channel: str) -> bool:
        """
        Check if a channel is missing (matches Node.js isChannelMissing method).
        
        Args:
            channel: The channel name ('alpha', 'red', 'green', 'blue', etc.)
            
        Returns:
            True if the channel is missing (None)
        """
        match channel.lower():
            case 'alpha':
                return self._alpha is None
            case 'red' | 'hue' | 'lightness' | 'x' | 'channel1':
                return self._channel1 is None
            case 'green' | 'saturation' | 'whiteness' | 'a' | 'chroma' | 'y' | 'channel2':
                return self._channel2 is None
            case 'blue' | 'lightness' | 'blackness' | 'b' | 'z' | 'channel3':
                return self._channel3 is None
            case _:
                return True
    
    # RGB properties (for backward compatibility and common usage)
    @property
    def red(self) -> Optional[float]:
        """Red channel (0-255) if in RGB space."""
        if self._space in ['rgb', 'srgb']:
            return self._channel1
        return None
    
    @property
    def green(self) -> Optional[float]:
        """Green channel (0-255) if in RGB space."""
        if self._space in ['rgb', 'srgb']:
            return self._channel2
        return None
    
    @property
    def blue(self) -> Optional[float]:
        """Blue channel (0-255) if in RGB space."""
        if self._space in ['rgb', 'srgb']:
            return self._channel3
        return None
    
    @property
    def alpha(self) -> Optional[float]:
        """Alpha channel (0-1)."""
        return self._alpha
    
    # HSL properties
    @property
    def hue(self) -> Optional[float]:
        """Hue channel if in HSL/HWB/LCH space."""
        if self._space in ['hsl', 'hwb', 'lch', 'oklch']:
            return self._channel1 if self._space in ['hwb', 'lch', 'oklch'] else self._channel1
        return None
    
    @property
    def saturation(self) -> Optional[float]:
        """Saturation channel if in HSL space."""
        if self._space == 'hsl':
            return self._channel2
        return None
    
    @property
    def lightness(self) -> Optional[float]:
        """Lightness channel if in HSL/LAB/LCH space."""
        if self._space in ['hsl', 'lab', 'oklab', 'lch', 'oklch']:
            return self._channel1 if self._space in ['lab', 'oklab', 'lch', 'oklch'] else self._channel3
        return None
    
    @property
    def is_truthy(self) -> bool:
        """Colors are always truthy in Sass."""
        return True
    
    @property
    def separator(self) -> Optional[str]:
        """Colors don't have separators."""
        return None
    
    @property
    def has_brackets(self) -> bool:
        """Colors don't have brackets."""
        return False
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, SassColor):
            return False
        return (
            abs((self._channel1 or 0) - (other._channel1 or 0)) < 1e-10 and
            abs((self._channel2 or 0) - (other._channel2 or 0)) < 1e-10 and
            abs((self._channel3 or 0) - (other._channel3 or 0)) < 1e-10 and
            abs((self._alpha or 1) - (other._alpha or 1)) < 1e-10 and
            self._space == other._space
        )
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash((
            round(self._channel1 or 0, 10),
            round(self._channel2 or 0, 10),
            round(self._channel3 or 0, 10),
            round(self._alpha or 1, 10),
            self._space
        ))
    
    def __str__(self) -> str:
        """String representation matching Sass output."""
        if self._space == 'rgb':
            r = int(self._channel1 or 0)
            g = int(self._channel2 or 0)
            b = int(self._channel3 or 0)
            a = self._alpha or 1
            
            if a == 1:
                return f"rgb({r}, {g}, {b})"
            else:
                return f"rgba({r}, {g}, {b}, {a})"
        else:
            # For other color spaces, use functional notation
            c1 = self._channel1 or 0
            c2 = self._channel2 or 0
            c3 = self._channel3 or 0
            a = self._alpha or 1
            
            if a == 1:
                return f"{self._space}({c1}, {c2}, {c3})"
            else:
                return f"{self._space}({c1}, {c2}, {c3}, {a})"
    
    def __repr__(self) -> str:
        """Python representation."""
        return f"SassColor(space='{self._space}', channels=[{self._channel1}, {self._channel2}, {self._channel3}], alpha={self._alpha})"
