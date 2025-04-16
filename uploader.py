import mimetypes
import requests
from typing import Dict, Optional, BinaryIO
import json
import os
import time

upload_endpoint = "http://localhost:8001/v3/project/knowledge/add/file?sync=true"

X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
project_id = os.environ.get("PROJECT_ID", "89d232ad59764da2b6118e")

def get_chunks_of_file(filename, headers):
    chunks_endpoint =   f"http://localhost:8001/project/{project_id}/document/chunks"
    response = requests.post(chunks_endpoint, headers=headers, json={"content_key":filename, "page":1, "page_size":20}  )

    return response

def delete_file(filename, headers):
    delete_endpoint = "http://localhost:8001/project/knowledge/delete"
    key_name = filename.replace(".", "_") 
    key_name = key_name.replace("-", "_") 
    json = {"project_id": project_id, "resources":[{"name":filename ,"key":f"_{project_id}_{key_name}"}]}
    response = requests.delete(delete_endpoint, headers=headers, json=json)
    if response.status_code == 200:
        print(f"Deleted file: {filename}")
        time.sleep(0.5)
    else:
        print(f"Failed to delete file: {filename} with status code {response.status_code}")

def should_upload_file(filename, headers):
    resp = get_chunks_of_file(filename, headers)
    if resp.status_code != 200:
        print(f"Failed to get chunks of file: {filename} with status code {resp.status_code}, file might not exists")
        return True
    data = resp.json()
    if len(data['chunks']) == 0 or any("Error extracting data from image" in chunk for chunk in data['chunks']):
        print(f"File {filename} has no chunks or error extracting data from image")
        delete_file(filename, headers)
        return True
    else:
        print(f"File {filename} has {len(data['chunks'])} chunks")
        return False

def upload_file(
    api_url: str,
    file_path: str,
    project_id: str,
    metadata: Dict = {}, 
    remote_path: str = "",
    is_quick_upload: bool = False,
    headers: Optional[Dict] = None
) -> Dict:
    """
    Upload a file using multipart/form-data with the specified payload structure.
    
    Args:
        file_path (str): Path to the file to upload
        project_id (str): Project identifier
        metadata (Dict): Dictionary containing metadata
        path (str): Destination path for the file
        is_quick_upload (bool): Whether to use quick upload
        api_url (str): API endpoint URL
        headers (Optional[Dict]): Additional headers to include in the request
        
    Returns:
        Dict: Response from the server
    """
    # Get the filename from the path
    filename = os.path.basename(file_path)
    
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'  # Default to binary if type unknown
    
    # Prepare the multipart form data with explicit content type
    files = {
        'file': (filename, open(file_path, 'rb'), content_type)
    }
    # Prepare the form data fields
    data = {
        'project_id': project_id,
        'metadata': json.dumps(metadata),  # Convert dict to JSON string
        'path': remote_path,
        'is_quick_upload': str(is_quick_upload).lower()  # Convert bool to string
    }
    
    # Set default headers if none provided
    if headers is None:
        headers = {
            'Accept': 'application/json',
        }
    
    try:
        # Make the POST request with multipart/form-data
        response = requests.post(
            api_url,
            files=files,
            data=data,
            headers=headers
        )
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        return response.status_code
        
    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e}")
        return {"error": str(e)}
        
    finally:
        # Ensure the file is closed
        files['file'][1].close()


def upload_files():
    api_url = "http://localhost:8001/v3/project/knowledge/add/file?sync=true"
    project_id = "89d232ad59764da2b6118e"
    headers = {"X-API-KEY": X_API_KEY, "X-API-SECRET": X_API_KEY}

    list_of_files = os.listdir("/Users/rohitjindal/del/files/datasets")
    with open("deleted_files.txt", "r") as f:
        # Read already uploaded files
        deleted_files = set()
        try:
            deleted_files = set(f.read().splitlines())
        except:
            # File is empty or doesn't exist yet
            pass
    uploaded_count = 0   
    with open("uploaded_files.txt", "a") as f:
        # Open in append mode to add newly uploaded files
        for file in list_of_files:
            if file in deleted_files:
                print(f"Skipping file: {file} because it is deleted")
                continue
            if not should_upload_file(file, headers):
                print(f"Skipping file: {file}")
                continue

            uploaded_count += 1
            print(f"Uploading count: {uploaded_count}")
            file_path = os.path.join("/Users/rohitjindal/del/files/datasets", file)
            if upload_file(
                api_url,
                file_path,
                project_id,
                headers= headers
            ) == 200:   
                print(f"Uploaded file: {file}")
                f.write(file + "\n")
            else:
                print(f"Failed to upload file: {file}")
            time.sleep(1)  # Reduced sleep time to 2 seconds






if __name__ == "__main__":
    upload_files()