
x_api_key=1234567890
x_api_secret=1234567890

project_id = "010a2996332c4417990aaa"

access_token= """eyJhbGciOiJSUzI1NiIsImtpZCI6ImE5ZGRjYTc2YzEyMzMyNmI5ZTJlODJkOGFjNDg0MWU1MzMyMmI3NmEiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiUm9oaXQgSmluZGFsIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0l4Y3kxYjJwdFhtbF8tZ0pUMkFMenYwbl9HWXh6UjZDTmdMLWxrTVVtb0gxeDI4UT1zOTYtYyIsImlzcyI6Imh0dHBzOi8vc2VjdXJldG9rZW4uZ29vZ2xlLmNvbS9haS1jb250ZW50LXdyaXRlci1lMDgzOSIsImF1ZCI6ImFpLWNvbnRlbnQtd3JpdGVyLWUwODM5IiwiYXV0aF90aW1lIjoxNzQzMjUxNDkyLCJ1c2VyX2lkIjoiVFlvT280Y3FLY1pIT1pESmh5R3pmWW1vVHRHMyIsInN1YiI6IlRZb09vNGNxS2NaSE9aREpoeUd6Zlltb1R0RzMiLCJpYXQiOjE3NDM4MjgyMjUsImV4cCI6MTc0MzgzMTgyNSwiZW1haWwiOiJyb2hpdC5qaW5kYWxAZ2V0b2Rpbi5haSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7Imdvb2dsZS5jb20iOlsiMTE2MjUwNzgzMTEyMTQ5ODkzMzY0Il0sImVtYWlsIjpbInJvaGl0LmppbmRhbEBnZXRvZGluLmFpIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.eco6_K7m3_52uIUmzl2wBiKghpM5zdwWod5WFAkRHJ4SV2scdhyfh0BjBgK4ggtC4nJqYka_iqKdXQ9GKk1_X9_VxA8YYwheD3-JMoI-zOoDjKb1dDswpSNg8qvoChDUd5B9LcSQsAcA7d6KUszAdySjkKDUo0rJYzb1aCtLp84NwLPEdl31tHfbDqgSBvjMWlRhjJQqkw3Dbkc69rd1w1wuPzx3QK5IhiYZVxWPGNKg4xUfvjLnHKvAzOVjxMCHo9TNIH_ikM6XRNrkyCUoY3vGSsNZ5oqm8TNZNyl5GKx8iOubfjTfWxlUtJ3hrcYsmtmZcGeNOADHCcrgD6LfPQ"""

payload =  [{"path":"010a2996332c4417990aaa/emails/jnpr_10-k_1707264000.pdf","isDir":False}]

import requests

request_payload = {"project_id":"010a2996332c4417990aaa","items_per_page":20,"page":1,"filters":{},"name_search":"","path":"emails/"}


list_api_url = f"https://ecs-api.getodin.ai/v3/project/{project_id}/knowledgebase"



url = f"https://ecs-api.getodin.ai/v3/project/{project_id}/knowledgebase/fetch-files"



def get_list_of_files():
    response = requests.get(list_api_url, headers=headers, json=request_payload)
    return response.json()


from tqdm import tqdm

def download_file(file_path):
    response = requests.post(url, headers={"access-token": access_token}, json=[{"path":file_path, "isDir": True}])
    with open(file_path.split("/")[-1], 'wb') as f:
        # You can iterate over the response data in chunks
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # Filter out keep-alive chunks
                f.write(chunk)
 


if __name__ == "__main__":
    download_file("010a2996332c4417990aaa/emails/jnpr_10-k_1707264000.pdf")