import google.generativeai as genai
from config import load_config

PROMPT_TEMPLATE = """
<SCHEMA>

Question:
<QUESTION>

Query:
<QUERY>

Query result:
<QUERY-RESULT-STR>

Answer:
""".strip()

class ResponseGenerator:
    def __init__(self, schema: str):
        self._schema = schema
        
        config = load_config()
        api_key = config.get_gemini_api_key()

        if not api_key or api_key == "YOUR_GEMINI_API_KEY":
            raise ValueError("Please set your Gemini API key in config.toml")
        
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel('gemini-2.5-flash')

    def __call__(self, question: str, query: str, query_result_str: str):
        prompt = PROMPT_TEMPLATE
        prompt = prompt.replace("<SCHEMA>", self._schema)
        prompt = prompt.replace("<QUESTION>", question)
        prompt = prompt.replace("<QUERY>", query)
        prompt = prompt.replace("<QUERY-RESULT-STR>", query_result_str)

        system_instruction = "You are a Mobile Legends knowledge assistant. Answer the user question ONLY using the provided Neo4j query results. Do not make up hero names or information. If the query returned no results, say so clearly. Keep answers concise and accurate."
        
        full_prompt = f"{system_instruction}\n\n{prompt}"
        
        response = self._model.generate_content(full_prompt)
        return response.text.strip()

if __name__ == "__main__":
    with open("schema_example.txt") as fp:
        schema = fp.read().strip()

    print("Preparing pipeline ....")
    generator = ResponseGenerator(schema)

    question = "List all players and their levels."
    query = """
MATCH (p:Player)-[:SHARES]->(l:Level)
RETURN p.username AS username, l.name AS level_name
    """.strip()
    query_result_str = """
{'username': 'Galactic71', 'level_name': 'Lanterns Preview'}
{'username': 'Demonmaster197', 'level_name': 'fun adventure'}
{'username': 'Demonmaster197', 'level_name': 'moonlight'}
{'username': 'usnsrDEMON', 'level_name': 'memories'}
    """.strip()

    print("Generating ...")
    response = generator(question, query, query_result_str)
    print(response)
