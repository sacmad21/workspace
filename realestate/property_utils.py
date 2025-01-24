# Utility Functions for Property Management

from db_config import CosmosDBConfig

# Initialize Cosmos DB configuration
endpoint = "<COSMOS_DB_ENDPOINT>"
key = "<COSMOS_DB_KEY>"
database_name = "real_estate_db"
db_config = CosmosDBConfig(endpoint, key, database_name)

def fetch_property_availability(criteria):
    """
    Fetch property availability based on user-defined criteria.
    Parameters:
        criteria (dict): A dictionary containing filters like location, budget, property type, etc.
    Returns:
        list: A list of matching properties.
    """
    container = db_config.create_container("basic_property_info", {"path": "/businessId"})
    query = "SELECT * FROM c WHERE c.businessId = @businessId"
    for key, value in criteria.items():
        query += f" AND c.{key} = @{key}"
    parameters = [{"name": "@businessId", "value": criteria.get("businessId", "")}]
    for key, value in criteria.items():
        parameters.append({"name": f"@{key}", "value": value})
    items = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    return items

def fetch_similar_properties(criteria):
    """
    Suggest similar properties if no exact match is found.
    Parameters:
        criteria (dict): A dictionary containing filters like location, budget, property type, etc.
    Returns:
        list: A list of similar properties.
    """
    container = db_config.create_container("basic_property_info", {"path": "/businessId"})
    query = "SELECT * FROM c WHERE c.businessId = @businessId AND c.type = @type"
    parameters = [
        {"name": "@businessId", "value": criteria.get("businessId", "")},
        {"name": "@type", "value": criteria.get("propertyType", "")}
    ]
    items = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    return items

def suggest_trending_properties(region, budget):
    """
    Proactively recommend trending properties based on user preferences and region.
    Parameters:
        region (str): The region specified by the user.
        budget (float): The budget specified by the user.
    Returns:
        list: A list of trending properties.
    """
    container = db_config.create_container("basic_property_info", {"path": "/businessId"})
    query = "SELECT * FROM c WHERE c.region = @region AND c.price <= @budget ORDER BY c.price DESC"
    parameters = [
        {"name": "@region", "value": region},
        {"name": "@budget", "value": budget}
    ]
    items = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    return items
