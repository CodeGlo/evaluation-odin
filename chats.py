import requests
import os
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")

PROJECT_ID = os.getenv("PROJECT_ID")
CHAT_ID = os.getenv("CHAT_ID")

def submit_question(question, project_id, chat_id):
    questions_url = f"http://localhost:8001/v3/chat/message"
    data = {
        'message': question,
        'project_id': project_id,
        'chat_id': chat_id,
        'is_test': 'false',
        'agent_type': 'chat_agent', 
        'agent_id': 'default_kb_agent',
        'ai_response': 'true',
        'is_regenerating': 'false',
        'request_metadata': json.dumps({"files_metadata":[],"time": datetime.now().isoformat()})
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "X-API-KEY": X_API_KEY, 
        "X-API-SECRET": X_API_SECRET
    }
    response = requests.post(questions_url, data=data, headers=headers)
    return True if response.status_code == 200 else False

def _get_answer(question, project_id, chat_id, extended_response=False):

    headers = {
        "X-API-KEY": X_API_KEY, 
        "X-API-SECRET": X_API_SECRET
    }
    questions_url = f"http://localhost:8001/project/{project_id}/chat/{chat_id}?prompt_debug=True"
    response = requests.get(questions_url,  headers=headers)
    if response.status_code == 200:
        for msg in response.json()['messages']:
            if msg['message'] == question:
                if extended_response:
                    return msg
                else:
                    return msg['response'] 
    else:
        print(f"Failed to get answer for question: {question}")
    return 'failed'


def get_answer(question, project_id, chat_id, extended_response=False):
    count = 5
    while count > 0:
        answer = _get_answer(question, project_id, chat_id, extended_response)
        if answer != 'failed':
            return answer
        count -= 1
        import time; time.sleep(1)
    return 'failed'


if __name__ == "__main__":
    count = 0
    for file in os.listdir('QnA'):
        if not file.endswith('.json'):
            continue

        with open(f'QnA/{file}', 'r') as f:    
            count += 1
            questions = f.read()
            q_n_a_s = json.loads(questions)
            for q_n_a in q_n_a_s:
                print(f"Submitting question: {q_n_a['question']}")
                submit_question(q_n_a['question'], PROJECT_ID, CHAT_ID)
                response = get_answer(q_n_a['question'], PROJECT_ID, CHAT_ID)
                print(f"Response: {response}")
                q_n_a['response'] = response

            with open(f'QnA/file_ans_{count}.json', 'w') as f2:
                json.dump(q_n_a_s, f2)
