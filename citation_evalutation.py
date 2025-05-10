import json
from chats import submit_question, get_answer
from dotenv import load_dotenv
import os

load_dotenv()

project_id = "a6b6387a63c0481ca0373d"
chat_id = "d039ac53ef1343d0861d11"


def evaluate_citations(citations, relevant_chunks):
    total_chunks = len(relevant_chunks)
    filtered_chunks = list(filter(lambda x: x in relevant_chunks, citations))
    missing_chunks = list(filter(lambda x: x not in relevant_chunks, citations))

    return {
        "precision_score": len(filtered_chunks) / total_chunks,
        "redundancy_score": len(missing_chunks) / total_chunks,
    }


def get_citations_from_chat(chat_response):
    return [x['match_string'] for x in chat_response["citation_source"]["source_mapping"]]

if __name__ == "__main__":
    with open('questions_bank.json', 'r') as f:
        questions_bank = json.load(f)

    failed_to_submit_qeuestion = 0
    for question in questions_bank:
        print(question)
        if  submit_question(question["question"], project_id, chat_id):
            print("Question submitted successfully")
        else:
            print("Question submission failed")
            failed_to_submit_qeuestion += 1
            continue
        answer = get_answer(question["question"], project_id, chat_id, extended_response=True)
        print(answer)
        citations = get_citations_from_chat(answer)
        print(citations)
        evaluation = evaluate_citations(citations, question["relevant_chunks"])
        
        print(evaluation)
        question.update(evaluation)
        
    with open('RetriverEval/citation_eval.json', 'w') as f:
        json.dump(questions_bank, f, indent=4)
