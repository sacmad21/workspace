import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import OperationFailure
from functools import wraps
import time


def retry_connection(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Connection attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            raise Exception("Failed to connect after multiple attempts")

        return wrapper

    return decorator


class OptimizedMongoClient:
    def __init__(
        self,
        host=None,
        port=27017,
        username="admin",
        password="password",
        auth_source="admin",
        max_pool_size=100,
        min_pool_size=0,
        max_idle_time_ms=None,
    ):
        self.host = host or self._get_default_host()
        self.port = port
        self.username = username
        self.password = password
        self.auth_source = auth_source
        self.client = None
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
        self.max_idle_time_ms = max_idle_time_ms

    def _get_default_host(self):
        # Check if we're running inside a Docker container
        if os.path.exists("/.dockerenv"):
            return "mongodb"  # Use the service name defined in Docker network
        return "localhost"  # Default for local development

    @retry_connection()
    def connect(self):
        connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.auth_source}"

        self.client = MongoClient(
            connection_string,
            server_api=ServerApi("1"),
            maxPoolSize=self.max_pool_size,
            minPoolSize=self.min_pool_size,
            maxIdleTimeMS=self.max_idle_time_ms,
        )

        try:
            self.client.admin.command("ismaster")
            print(f"Connected to MongoDB successfully at {self.host}:{self.port}")
        except OperationFailure as e:
            if e.code == 13:
                print("Authentication failed. Please check your credentials.")
            else:
                print(f"An error occurred: {str(e)}")
            raise

    def get_database(self, db_name):
        if not self.client:
            self.connect()
        return self.client[db_name]

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")


class OptimizedMongoClientUpdated:
    def __init__(
        self,
        host="localhost",
        port=27017,
        username="admin",
        password="password",
        auth_source="admin",
        max_pool_size=100,
        min_pool_size=0,
        max_idle_time_ms=None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth_source = auth_source
        self.client = None
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
        self.max_idle_time_ms = max_idle_time_ms

    @retry_connection()
    def connect(self):
        self.client = MongoClient(
            host=self.host,
            port=self.port,
            authSource=self.auth_source,
            maxPoolSize=self.max_pool_size,
            minPoolSize=self.min_pool_size,
            maxIdleTimeMS=self.max_idle_time_ms,
            server_api=ServerApi("1"),
        )

        try:
            self.client.admin.command("ismaster")
            print(f"Connected to MongoDB successfully at {self.host}:{self.port}")
        except OperationFailure as e:
            if e.code == 13:
                print("Authentication failed. Please check your credentials.")
            else:
                print(f"An error occurred: {str(e)}")
            raise

    def get_database(self, db_name):
        if not self.client:
            self.connect()
        return self.client[db_name]

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")
