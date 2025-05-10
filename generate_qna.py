from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json
import os
import requests
from dotenv import load_dotenv

X_API_KEY = "d31fc0b9-95fb-465d-a08b-e2cd53500503"
X_API_SECRET="XDarrFdrMedvjtc9CB/3aKEteW3mNtavsJYoPyFziic="

# Define the prompt template for question generation
QUESTION_GENERATION_TEMPLATE = """
You are an expert at creating diverse and challenging questions from given list of chunks. Your task is to generate insightful questions based on the provided text.

Context: 
{chunks}

Please generate questions that:
1. Test different levels of understanding (factual, conceptual, analytical)
2. Cover different aspects of the content.
3. Are clear and unambiguous
4. Have specific, verifiable answers from the context

Generate exactly {num_questions} questions in the following JSON format:
[
    {{
        "question": "The actual question text",
        "relevant_chunks": "List of relevant chunks ids which is integer (i.e 1 is id in Chunk 1, 2 is id in Chunk 2, etc)  from the context that support the question in decreasing order of relevance"
    }}
]

Ensure each question is:
- Self-contained and meaningful
- Directly answerable from the given context
- May be answerable from the multiple chunks
- Free of any external knowledge requirements

IMPORTANT: Return ONLY the JSON array, no additional text or explanation.
"""

def generate_questions(chunks=[], num_questions=2):
    """
    Generate questions from text content using LangChain.
    
    Args:
        chunks (str): Input text content to generate questions from
        num_questions (int): Number of questions to generate per chunk
        
    Returns:
        list: List of dictionaries containing questions and metadata
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize LLM
    llm = ChatOpenAI(
        temperature=0.7,
        model_name="gpt-4o-mini"
    )
    
    # Create prompt template
    prompt = PromptTemplate(
        input_variables=["chunks", "num_questions"],
        template=QUESTION_GENERATION_TEMPLATE
    )
    
    # Create the runnable chain using pipe syntax
    chain = prompt | llm
    
    # Format chunks as a string with newlines
    chunks_text = "\n--------End of Chunk--------\n".join(chunks)
    
    try:
        # Generate questions using the new pipe syntax
        result = chain.invoke({
            "chunks": chunks_text,
            "num_questions": num_questions
        })
        
        # Get the raw text from the message
        response_text = result.content
        print("Raw response:", response_text)
        
        # Clean the response text to ensure it's valid JSON
        # Remove any leading/trailing whitespace and non-JSON text
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]  # Remove ```json
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]  # Remove ```
        cleaned_text = cleaned_text.strip()
        
        # Parse the JSON result
        questions = json.loads(cleaned_text)
        print("\nParsed questions:", json.dumps(questions, indent=2))
        return questions
                
    except json.JSONDecodeError as e:
        print(f"Error parsing questions: {e}")
        print(f"Raw result: {response_text}")
        print(f"Cleaned text attempted to parse: {cleaned_text}")
        return []
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def get_total_pages(project_id, doc):
    url = f"http://localhost:8001/project/{project_id}/document/chunks"  
    data = {
        "content_key": doc['content_key'],
        'page': 1,
        'page_size': 40
    }
    headers = {
        "X-API-Key": X_API_KEY,
        "X-API-Secret": X_API_SECRET
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['total_pages']

def get_list_of_chunks(project_id, doc, page_number=1):
    """
    Get a list of chunks for a given document
    total_pages
    total_chunks
    """
    documents = get_list_of_documents(project_id)
    page_size = 40
    url = f"http://localhost:8001/project/{project_id}/document/chunks"
    headers = {
        "X-API-Key": X_API_KEY,
        "X-API-Secret": X_API_SECRET
    }
    data = {
        "content_key": doc['content_key'],
        'page': page_number,
        'page_size': page_size
    }
    response = requests.post(url, headers=headers, json=data)
    return [X['content'] for X in response.json()['chunks']]


def get_list_of_documents(project_id):
    url = f"http://localhost:8001/v3/project/{project_id}/knowledgebase"
    headers = {
        "X-API-Key": X_API_KEY,
        "X-API-Secret": X_API_SECRET,
    }
    data = {
        "page": 1,
        "page_size": 100,
        "project_id": project_id
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['docs']


if __name__ == "__main__":
    project_id = "a6b6387a63c0481ca0373d"
    docs = get_list_of_documents(project_id)
    questions_bank = []
    for doc in docs:
        pages = get_total_pages(project_id, doc)
        for page in range(1, pages + 1):
            chunks = get_list_of_chunks(project_id, doc, page)
            chunks_with_ids = [f"Chunk {i}: {chunk}" for i, chunk in enumerate(chunks, 1)]
            questions = generate_questions(chunks_with_ids, 2)
            for question in questions:
                print(chunks_with_ids)
                print(question)
                try:
                    if isinstance(question['relevant_chunks'], str):
                        question['relevant_chunks'] = [chunks[int(chunk) - 1] for chunk in question['relevant_chunks'].split(',')]
                    else:
                        question['relevant_chunks'] = [chunks[i - 1] for i in question['relevant_chunks']]
                    questions_bank.append(question)
                except Exception as e:
                    print(e)
    with open('questions_bank.json', 'w') as f:
        json.dump(questions_bank, f) 