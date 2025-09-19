"""
Deprecation handling for Sass embedded host.
"""

from typing import Any, List, Optional, Union, Dict

# Placeholder deprecation registry - will be expanded later
deprecations = {}
Deprecation = Any
DeprecationOrId = Any
DeprecationStatus = Any

# Active deprecation options (like Node.js activeDeprecationOptions)
active_deprecation_options: Dict[object, Dict[str, Any]] = {}


def get_deprecation_ids(deprecations_list: Optional[List[Union[str, int]]]) -> List[int]:
    """
    Convert deprecation names to IDs.
    
    This matches the Node.js getDeprecationIds() function.
    
    Args:
        deprecations_list: List of deprecation names or IDs
        
    Returns:
        List of deprecation IDs
    """
    if not deprecations_list:
        return []
    
    # For now, return the list as-is since we don't have a deprecations registry yet
    # TODO: Implement proper deprecation name to ID mapping when we have full deprecations
    return [int(dep) if isinstance(dep, (int, str)) and str(dep).isdigit() else hash(str(dep)) % 1000 
            for dep in deprecations_list]


def valid_deprecation_id(deprecation_id: Any) -> bool:
    """
    Type guard to check that ID is a valid deprecation ID.
    
    This matches the Node.js validDeprecationId() function.
    
    Args:
        deprecation_id: The deprecation ID to check
        
    Returns:
        True if it's a valid deprecation ID, False otherwise
    """
    # For now, accept any non-empty string or number
    # TODO: Implement proper deprecation ID validation when we have full deprecations
    return bool(deprecation_id and (isinstance(deprecation_id, (str, int))))
