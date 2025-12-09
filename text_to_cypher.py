import google.generativeai as genai
from config import load_config

class TextToCypher:
    def __init__(self, schema: str):
        self._schema = schema
        
        # Load Gemini API key from config
        config = load_config()
        api_key = config.get_gemini_api_key()
        if not api_key or api_key == "YOUR_GEMINI_API_KEY":
            raise ValueError("Please set your Gemini API key in config.toml")
        
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel('gemini-2.5-flash')

    def __call__(self, question: str):
        # Prompt template
        prompt = f"""
        You are an expert Neo4j developer converting natural language questions into Cypher queries.

        ### DATABASE SCHEMA INSTRUCTIONS:
        Strictly use ONLY the node labels, relationship types, and properties defined in the schema below. Do not invent new relationships or properties.

        {self._schema}

        ### SYNTAX RULES:
        1. **Directionality:** Pay attention to relationship directions (->, <-, or -).
        2. **Case Sensitivity:** Ensure string matching is case-insensitive if needed (e.g., `toLower(n.name) = 'layla'`).
        3. **Data Types:** Treat numbers as integers/floats and names as strings.
        4. **Clean Output:** Output ONLY the Cypher query string. No markdown, no explanations.

        ### EXAMPLES OF LOGIC MAPPING:
        - "Find X": MATCH (n:Label {{prop: 'X'}}) RETURN n
        - "List all X": MATCH (n:Label) RETURN n
        - "Count X": MATCH (n:Label) RETURN count(n)
        - "X related to Y": MATCH (a:Label {{name: 'X'}})-[:RELATIONSHIP]->(b:Label) RETURN b

        ### FEW-SHOT EXAMPLES:
        Question: Who are the marksman heroes?
        Cypher: MATCH (h:Hero)-[:HAS_ROLE]->(r:Role {{name: 'marksman'}}) RETURN h.name

        Question: Find heroes that counter Miya.
        Cypher: MATCH (h:Hero {{name: 'miya'}})<-[:COUNTERS]-(counter:Hero) RETURN counter.name

        Question: Which hero has the highest physical attack?
        Cypher: MATCH (h:Hero) RETURN h.name, h.physical_attack ORDER BY h.physical_attack DESC LIMIT 1

        Question: How many heroes are in the database?
        Cypher: MATCH (h:Hero) RETURN count(h) as total_heroes

        ### YOUR TASK:
        Question: {question}
        Cypher:
        """
        
        response = self._model.generate_content(prompt)
        generated_text = response.text.strip()
        
        # Clean up markdown code blocks if present
        if '```' in generated_text:
            # Extract code from markdown
            lines = generated_text.split('\n')
            code_lines = []
            in_code = False
            for line in lines:
                if line.strip().startswith('```'):
                    in_code = not in_code
                    continue
                if in_code or (not line.strip().startswith('```') and 'MATCH' in line):
                    code_lines.append(line)
            generated_text = '\n'.join(code_lines).strip()
        
        return generated_text

if __name__ == "__main__":
    with open("schema_example.txt") as fp:
        schema = fp.read().strip()

    print("Preparing pipeline ....")
    ttc = TextToCypher(schema)

    print("Generating ...")
    cypher = ttc("Find all players that submit a comment \"GG!\".")
    print(cypher)
