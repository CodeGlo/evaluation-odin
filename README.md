# Aim
This repository contains code for evaluating and establishing baseline metrics for our Chat AI Agent. The evaluation framework focuses on three key aspects of the agent's responses:

1. Answer Similarity - Uses embedding-based comparison to measure semantic similarity between generated answers and ground truth
2. Answer Correctness - Employs LLM to verify factual accuracy of generated responses
3. Answer Relevancy - Uses LLM to assess if the response appropriately addresses the query

The metrics help quantify the performance and reliability of the Chat AI Agent across different types of questions and use cases. This data serves as a foundation for measuring improvements and optimizing the agent's capabilities.


## Datasets
The datasets directory contains the test data and evaluation results in a compressed tar.gz archive. This includes files/knowledge base 
on which these metrics are generated.

## QnA
The QnA directory contains the 

- Question and answer pairs for testing
- Ground truth reference answers 
- Generated AI responses
- Evaluation metrics and scores

`test_qna_*.json` contains the Question, context and ground pair.
`file_ans_*.json` contains the Question, along with their ai reponses.
`file_eval_*.json` conains the metrics for QnA pairs

## Code Files

### uploader.py
This script handles downloading files from the knowledge base using the Odin API. It includes functionality to:
- Download individual files using file paths
- List available files in the knowledge base
- Handle authentication using access tokens

### chats.py 
Contains code for interacting with the chat API to:
- Submit questions to the chat agent
- Retrieve AI responses 
- Handle retries and error cases
- Process batches of questions from JSON files

### evaluation.py
Implements the evaluation framework using the Ragas library to calculate:
- Answer similarity scores using embeddings
- Answer correctness using LLM verification 
- Answer relevancy by comparing to queries
- Processes evaluation results and saves metrics to JSON files

The evaluation uses GPT-4 as the LLM evaluator and runs the metrics on question-answer pairs stored in the QnA directory.




