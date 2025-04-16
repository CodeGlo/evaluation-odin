from langchain_core.documents import Document
import os
from ragas import EvaluationDataset
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import  answer_correctness, answer_relevancy, answer_similarity
from langchain_community.chat_models import ChatOpenAI
import json

"""
Metric	            Compares To 	Uses Embedding or LLM?	 What It Checks
answer_similarity	ground_truth	Embedding-based	         Are the answers semantically similar?
answer_correctness	ground_truth	LLM                      Is the generated answer factually correct?
answer_relevance	query	        LLM                    	 Does the generated answer respond to the query?
"""


llm = ChatOpenAI(model="gpt-4o-mini")


def evaluate_rags(question, ai_response, ground_truth, contextList=None):
    dataset = {
        "user_input": question,
       # "retrieved_contexts":  ["OpenAI is a company that makes AI models, its ceo is"] + ["Sam Altman"],
        "response": ai_response,
        "reference": ground_truth
    }
    evaluator_llm = LangchainLLMWrapper(llm)
    evaluationDataset = EvaluationDataset.from_list([dataset])
    result = evaluate(dataset=evaluationDataset, metrics=[answer_relevancy, answer_correctness, answer_similarity],llm=evaluator_llm)
    return result

if __name__ == "__main__":
    for file in os.listdir('QnA'):
        file2 = file.replace('ans', 'eval')
        if not file.endswith('.json') or not file.startswith('file_ans') or os.path.exists(f'QnA/{file2}'):
            continue

        print("Processing file: ", file)
        with open(f'QnA/{file}', 'r') as f:
            q_n_a_s = json.loads(f.read())
            for q_n_a in q_n_a_s:
                question = q_n_a.get('question', '')
                ai_response = q_n_a.get('response', '')
                ground_truth = q_n_a.get('ground_truth', '')
                result = evaluate_rags(question, ai_response, ground_truth)
                print(result)
                q_n_a['answer_relevancy'] = result['answer_relevancy']
                q_n_a['answer_correctness'] = result['answer_correctness']
                q_n_a['semantic_similarity'] = result['semantic_similarity']
            with open(f'QnA/{file2}', 'w') as f2:
                f2.write(json.dumps(q_n_a_s))