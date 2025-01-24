# Utility Functions for Search Options

def fetch_suggested_search_options():
    """
    Fetch common search options like budget, location, or property type.
    Returns:
        list: A list of suggested search options.
    """
    return [
        {"key": "budget", "description": "Search by budget range"},
        {"key": "location", "description": "Search by location"},
        {"key": "propertyType", "description": "Search by property type (e.g., apartment, house)"}
    ]
