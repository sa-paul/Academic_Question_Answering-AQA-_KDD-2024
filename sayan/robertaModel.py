from transformers import RobertaTokenizer, RobertaModel
import torch
import json

# Load the tokenizer and model from the Hugging Face library
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
model = RobertaModel.from_pretrained('roberta-base')

# Function to convert text to embeddings
def get_embeddings(text):
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

# Load the data
with open('pid_to_title_abs_new.json') as f:
    paper_data = json.load(f)

# Convert paper titles and abstracts to embeddings
paper_embeddings = {}
for pid, info in paper_data.items():
    paper_embeddings[pid] = get_embeddings(info['title'] + ' ' + info['abstract'])

# Load the questions
with open('qa_train.txt') as f:
    questions = json.load(f)

# Convert questions to embeddings and find the most relevant papers
for question in questions:
    question_embedding = get_embeddings(question['question'] + ' ' + question['body'])
    similarities = {}
    for pid, embedding in paper_embeddings.items():
        cos_sim = torch.nn.functional.cosine_similarity(question_embedding, embedding, dim=0)
        similarities[pid] = cos_sim.item()
    
    # Sort by similarity
    relevant_pids = sorted(similarities, key=similarities.get, reverse=True)[:20]
    print(f"Question: {question['question']}")
    print(f"Top 20 relevant paper IDs: {relevant_pids}")