from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-0.5B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

prompt = """
Node properties:
- **Player**
- accountId: INTEGER
- username: STRING Example: "Nicki1202"
- **Level**
- id: INTEGER
- name: STRING Example: "OuterSpace"
- **Comment**
- id: INTEGER
- content: STRING Example: "GG! Nice level:)"
Relationship properties:

The relationships:
(:Player)-[:SHARES]->(:Level)
(:Player)-[:SUBMITS]->(:Comment)
(:Level)-[:HAS]->(:Comment)

Question:
List all players and their levels.

Query:
MATCH (p:Player)-[:SHARES]->(l:Level)
RETURN p.username AS username, l.name AS level_name

Query result:
{'username': 'Galactic71', 'level_name': 'Lanterns Preview'}
{'username': 'Demonmaster197', 'level_name': 'fun adventure'}
{'username': 'Demonmaster197', 'level_name': 'moonlight'}
{'username': 'usnsrDEMON', 'level_name': 'memories'}

Answer:
""".strip()
messages = [
    {"role": "system", "content": "Answer the user question using the provided Neo4j context. Only response the query result in natural language."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)
