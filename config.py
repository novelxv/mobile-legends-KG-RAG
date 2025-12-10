import tomllib
import os

class Config:
    def __init__(self, data: dict[str]):
        self._data = data
    
    def get_neo4j_driver_kwargs(self):
        # Try environment variables first (for deployment), fallback to config file
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_username = os.getenv("NEO4J_USERNAME")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        
        if neo4j_uri and neo4j_username and neo4j_password:
            return {
                "uri": neo4j_uri,
                "auth": (neo4j_username, neo4j_password)
            }
        
        # Fallback to config file
        neo4j_data = self._data["neo4j"]
        return {
            "uri": neo4j_data["database_uri"],
            "auth": (neo4j_data["username"], neo4j_data["password"])
        }
    
    def get_neo4j_database_name(self):
        # Try environment variable first
        database_name = os.getenv("NEO4J_DATABASE")
        if database_name:
            return database_name
        
        # Fallback to config file
        neo4j_data = self._data["neo4j"]
        return neo4j_data["database_name"]
    
    def get_gemini_api_key(self):
        # Try environment variable first
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            return api_key
        
        # Fallback to config file
        gemini_data = self._data.get("gemini", {})
        return gemini_data.get("api_key")

def load_config(toml_path: str = "config.toml"):
    # Allow running without config file if all env vars are set
    if not os.path.exists(toml_path):
        return Config({})
    
    with open(toml_path, mode="rb") as fp:
        return Config(tomllib.load(fp))

