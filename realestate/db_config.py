#db-config.py

from azure.cosmos import CosmosClient

# Cosmos DB Configuration
class CosmosDBConfig:
    def __init__(self, endpoint, key, database_name):
        self.client = CosmosClient(endpoint, key)
        self.database_name = database_name
        self.database = self.client.create_database_if_not_exists(id=self.database_name)

    def create_container(self, container_name, partition_key):
        return self.database.create_container_if_not_exists(
            id=container_name,
            partition_key=partition_key
        )

# Define Containers and Schemas
CONTAINERS = {
    "customer_queries": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "queryId": "string",
            "businessId": "string",
            "userId": "string",
            "queryText": "string",
            "timestamp": "date"
        }
    },
    "chat_sessions": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "sessionId": "string",
            "businessId": "string",
            "userId": "string",
            "messages": [
                {
                    "messageId": "string",
                    "content": "string",
                    "timestamp": "date"
                }
            ]
        }
    },
    "chatbot_responses": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "responseId": "string",
            "businessId": "string",
            "queryId": "string",
            "responseText": "string",
            "timestamp": "date"
        }
    },
    "message_logs": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "logId": "string",
            "businessId": "string",
            "sessionId": "string",
            "messageDetails": [
                {
                    "messageId": "string",
                    "content": "string",
                    "timestamp": "date"
                }
            ]
        }
    },
    "contact_info": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "userId": "string",
            "businessId": "string",
            "name": "string",
            "email": "string",
            "phone": "string"
        }
    },
    "filter_criteria": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "criteriaId": "string",
            "businessId": "string",
            "key": "string",
            "value": "string"
        }
    },
    "user_preferences": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "preferenceId": "string",
            "businessId": "string",
            "userId": "string",
            "budget": "number",
            "location": "string",
            "propertyType": "string"
        }
    },
    "basic_property_info": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "propertyId": "string",
            "businessId": "string",
            "address": "string",
            "price": "number",
            "type": "string"
        }
    },
    "registration_details": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "userId": "string",
            "businessId": "string",
            "username": "string",
            "passwordHash": "string",
            "dateCreated": "date"
        }
    },
    "agent_profiles": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "agentId": "string",
            "businessId": "string",
            "name": "string",
            "email": "string",
            "role": "string"
        }
    },
    "feedback_entries": {
        "partition_key": {"path": "/businessId"},
        "schema": {
            "feedbackId": "string",
            "businessId": "string",
            "userId": "string",
            "content": "string",
            "timestamp": "date"
        }
    }
}

# Example usage
# Example usage
if __name__ == "__main__":
    endpoint = "<COSMOS_DB_ENDPOINT>"
    key = "<COSMOS_DB_KEY>"
    database_name = "real_estate_db"

    config = CosmosDBConfig(endpoint, key, database_name)

    for container_name, container_info in CONTAINERS.items():
        config.create_container(container_name, container_info["partition_key"])
        print(f"Created or validated container: {container_name}")
