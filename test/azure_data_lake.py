from pymongo import MongoClient
from azure.storage.filedatalake import DataLakeServiceClient
import traceback

DATALAKE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=smklake;AccountKey=VkP1gNKzPSupXUF8P6LkFcYF61/uaPpUG8LY5m4ovuEyguV7AVS9bcaFBD321RNZh1ITTdO7butq+AStHx//uw==;EndpointSuffix=core.windows.net"
DATALAKE_KEY="VkP1gNKzPSupXUF8P6LkFcYF61/uaPpUG8LY5m4ovuEyguV7AVS9bcaFBD321RNZh1ITTdO7butq+AStHx//uw=="
FILE_SYSTEM_NAME="govforms"





def create_file(filesystem, dir_name, document_name):

    try:
        # Connect to the Data Lake service
        service_client = DataLakeServiceClient.from_connection_string(DATALAKE_CONNECTION_STRING)

        # Create a file system (container)
        file_system_client = service_client.get_file_system_client(filesystem)
            
        # Create a directory for the user if it doesn't exist
        directory_client = file_system_client.get_directory_client(dir_name)

        file_client = directory_client.get_file_client(document_name)

        document_content = """
            This my first file into the Azure data lake. This will help me to simplify my problems.
            """

        file_client.upload_data(document_content, overwrite=True)

    except Exception as e:
        traceback.print_stack()
        print(f"Directory already exists: {e}")
    finally:
        service_client.close()



def create_directory(filesystem, new_dir):
    # Connect to the Data Lake service
    service_client = DataLakeServiceClient.from_connection_string(DATALAKE_CONNECTION_STRING)

    # Create a file system (container)
    file_system_client = service_client.get_file_system_client(filesystem)
        
    # Create a directory for the user if it doesn't exist
    directory_client = file_system_client.get_directory_client(new_dir)

    try:
        directory_client.create_directory()
        print("\nDirectory created on Azure Lake:")
    except Exception as e:
        print(f"Directory already exists: {e}")
    finally:
        service_client.close()




def create_file_system(filesystem):
    try:
        # Connect to the Data Lake service
        service_client = DataLakeServiceClient.from_connection_string(DATALAKE_CONNECTION_STRING)

        # Create a file system (container)
        file_system_client = service_client.get_file_system_client(filesystem)
        file_system_client.create_file_system()
        print(f"File system '{filesystem}' created successfully.")
            
    except Exception as e:
        print(f"Failed to create file system: {e}")

    finally :
        service_client.close()






# Call the function
# create_file_system("bingo786")
# create_directory("bingo786","mytwin/user123/documents")
create_file("bingo786","mytwin/user123/documents","abc.txt")

