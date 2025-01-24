# Utility Functions for Chat and Query Handling

from db_config import CosmosDBConfig

# Initialize Cosmos DB configuration
endpoint = "<COSMOS_DB_ENDPOINT>"
key = "<COSMOS_DB_KEY>"
database_name = "real_estate_db"
db_config = CosmosDBConfig(endpoint, key, database_name)

def generate_greeting(user_id):
    """
    Create a personalized greeting based on user data.
    Parameters:
        user_id (str): The unique identifier for the user.
    Returns:
        str: A personalized greeting message.
    """
    container = db_config.create_container("contact_info", {"path": "/businessId"})
    query = "SELECT * FROM c WHERE c.userId = @userId"
    parameters = [{"name": "@userId", "value": user_id}]
    user_data = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    if user_data:
        user = user_data[0]
        return f"Hello {user.get('name', 'Guest')}! How can we assist you today?"
    return "Hello! How can we assist you today?"

def detect_query_error(query_text):
    """
    Identify potential issues in a user query.
    Parameters:
        query_text (str): The query text provided by the user.
    Returns:
        bool: True if an error is detected, False otherwise.
    """
    if not query_text or len(query_text.strip()) == 0:
        return True
    # Additional checks for malformed or unsupported queries can be added
    return False

def fetch_popular_questions():
    """
    Provide a list of clickable prompts for popular questions.
    Returns:
        list: A list of popular question prompts.
    """
    return [
        "What are the trending properties?",
        "What is the average price in my location?",
        "Are there any 2-bedroom apartments available?"
    ]

def analyze_query_patterns(user_id, business_id):
    """
    Identify repeated failed queries for unavailable properties.
    Parameters:
        user_id (str): The unique identifier for the user.
        business_id (str): The unique identifier for the business.
    Returns:
        dict: A summary of query patterns.
    """
    container = db_config.create_container("customer_queries", {"path": "/businessId"})
    query = "SELECT c.queryText, COUNT(c.queryText) as queryCount FROM c WHERE c.businessId = @businessId AND c.userId = @userId GROUP BY c.queryText"
    parameters = [
        {"name": "@businessId", "value": business_id},
        {"name": "@userId", "value": user_id}
    ]
    items = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    return items

def analyze_chat_history(user_id, business_id):
    """
    Extract patterns and trends from the user’s chat history.
    Parameters:
        user_id (str): The unique identifier for the user.
        business_id (str): The unique identifier for the business.
    Returns:
        dict: A summary of extracted patterns and trends.
    """
    container = db_config.create_container("message_logs", {"path": "/businessId"})
    query = "SELECT c.messageDetails FROM c WHERE c.businessId = @businessId AND c.sessionId IN (SELECT VALUE s.sessionId FROM s WHERE s.userId = @userId)"
    parameters = [
        {"name": "@businessId", "value": business_id},
        {"name": "@userId", "value": user_id}
    ]
    items = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    return items

def generate_report_from_chat_data(chat_data):
    """
    Create a report summarizing frequent keywords and unanswered questions.
    Parameters:
        chat_data (list): A list of chat messages.
    Returns:
        dict: A report containing the summary.
    """
    keywords = {}
    unanswered = 0
    for chat in chat_data:
        content = chat.get("content", "")
        if "?" in content:  # Example heuristic for unanswered questions
            unanswered += 1
        for word in content.split():
            keywords[word] = keywords.get(word, 0) + 1
    return {"frequentKeywords": keywords, "unansweredCount": unanswered}
