from utils.mongo_service import OptimizedMongoClient

# def insert_up_properties(collection):
#     properties = [
#         {
#             "property_id": "UP001",
#             "property_name": "Lok Bhavan",
#             "location": "Lucknow",
#             "address": "Vidhan Sabha Marg, Lucknow, Uttar Pradesh 226001",
#             "type": "Government Office",
#             "area_sqft": 400000,
#             "year_built": 2016,
#             "departments": ["Chief Minister's Office", "Various State Departments"]
#         },
#         {
#             "property_id": "UP002",
#             "property_name": "Vidhan Sabha",
#             "location": "Lucknow",
#             "address": "Vidhan Sabha Marg, Hazratganj, Lucknow, Uttar Pradesh 226001",
#             "type": "Legislative Building",
#             "area_sqft": 342000,
#             "year_built": 1928,
#             "capacity": 404
#         },
#         {
#             "property_id": "UP003",
#             "property_name": "Taj Mahal",
#             "location": "Agra",
#             "address": "Dharmapuri, Forest Colony, Tajganj, Agra, Uttar Pradesh 282001",
#             "type": "Historical Monument",
#             "area_acres": 42,
#             "year_built": 1653,
#             "unesco_world_heritage": True
#         },
#         {
#             "property_id": "UP004",
#             "property_name": "Banaras Hindu University",
#             "location": "Varanasi",
#             "address": "Banaras Hindu University Campus, Varanasi, Uttar Pradesh 221005",
#             "type": "Educational Institution",
#             "area_acres": 1300,
#             "year_established": 1916,
#             "student_capacity": 30000
#         },
#         {
#             "property_id": "UP005",
#             "property_name": "Uttar Pradesh Police Headquarters",
#             "location": "Lucknow",
#             "address": "Sapru Marg, Qaisar Bagh, Lucknow, Uttar Pradesh 226001",
#             "type": "Law Enforcement",
#             "area_sqft": 250000,
#             "year_built": 1990,
#             "departments": ["Criminal Investigation", "Traffic", "Cyber Crime"]
#         }
#     ]

#     result = collection.insert_many(properties)
#     print(f"Inserted {len(result.inserted_ids)} documents")
#     return result.inserted_ids


def insert_data(collection, data):
    """
    Insert one or multiple documents into a MongoDB collection.

    :param collection: MongoDB collection object
    :param data: A single document (dict) or a list of documents to insert
    :return: List of inserted document IDs
    """
    if isinstance(data, list):
        result = collection.insert_many(data)
        inserted_ids = result.inserted_ids
    else:
        result = collection.insert_one(data)
        inserted_ids = [result.inserted_id]

    print(f"Inserted {len(inserted_ids)} document(s)")
    return inserted_ids


def search_property_by_id(collection, property_id):
    """
    Search for a property in the collection based on its property ID.

    :param collection: MongoDB collection object
    :param property_id: String representing the property ID to search for
    :return: Dictionary containing the property details if found, None otherwise
    """
    result = collection.find_one({"property_id": property_id})
    return result


def get_conversation_history(collection, session_id: str) -> list:
    """
    Retrieve the conversation history for a given session ID.

    Args:
        session_id: The session ID to retrieve history for

    Returns:
        List of conversation documents
    """
    return list(
        collection.find(
            {"session_id": session_id}, {"_id": 0}  # Exclude MongoDB _id field
        ).sort("timestamp", 1)
    )  # Sort by timestamp ascending


def search_aadhar_number(collection, aadhaar_number):
    try:
        result = collection.find_one({"aadhaar_card_no": aadhaar_number})
        return result
    except Exception as e:
        print("Failed due to ", str(e))


# import os
# # Usage example
# if __name__ == "__main__":
#     # Usage example
#     client = OptimizedMongoClient(
#     host=os.environ.get('MONGO_HOST'),  # Will use the default if not set
#     port=int(os.environ.get('MONGO_PORT', 27017)),
#     username=os.environ.get('MONGO_USERNAME', 'admin'),
#     password=os.environ.get('MONGO_PASSWORD', 'password'),
#     auth_source=os.environ.get('MONGO_AUTH_SOURCE', 'admin')
# )

#     try:
#         client.connect()
#         db = client.get_database("PWC")
#         print(db.list_collection_names())
#         collection = db["samagra_db"]
#         print(collection)
#         result = search_aadhar_number(collection=collection,aadhaar_number="123456789023")
#         print("The result is ", result)
#         # Perform database operations here

#     finally:
#         client.close()
