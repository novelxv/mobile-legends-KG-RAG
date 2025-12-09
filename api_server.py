from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from database import GraphDatabaseDriver
from response_generator import ResponseGenerator
from text_to_cypher import TextToCypher
import traceback

# Global variables
schema = ""
ttc = None
generator = None
driver = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown"""
    global schema, ttc, generator, driver
    
    # Startup
    print("🚀 Initializing RAG system...")
    
    # Load schema
    with open("schema_example.txt") as fp:
        schema = fp.read().strip()
    print("✅ Schema loaded")
    
    # Initialize Text-to-Cypher
    print("⏳ Loading Text-to-Cypher model...")
    ttc = TextToCypher(schema)
    print("✅ Text-to-Cypher ready")
    
    # Initialize Response Generator
    print("⏳ Loading Response Generator model (ini mungkin lama ~3-5 menit)...")
    generator = ResponseGenerator(schema)
    print("✅ Response Generator ready")
    
    # Initialize database connection
    driver = GraphDatabaseDriver()
    driver.__enter__()
    print("✅ Database connected")
    
    print("🎉 RAG system ready!")
    
    yield
    
    # Shutdown
    if driver:
        driver.__exit__(None, None, None)
    print("👋 Server shutdown")

app = FastAPI(title="Mobile Legends RAG API", lifespan=lifespan)

# CORS middleware untuk Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    question: str
    cypher_query: str
    results: list
    answer: str
    success: bool
    error: str = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Mobile Legends RAG API",
        "endpoints": {
            "POST /chat": "Send a question and get AI response",
            "GET /stats": "Get database statistics"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    """
    try:
        question = request.question.strip()
        
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Generate Cypher query
        print(f"\n💬 Question: {question}")
        query = ttc(question)
        print(f"🔍 Generated query: {query}")
        
        # Execute query
        try:
            results = driver.execute_query(query)
            print(f"✅ Query executed: {len(results)} results")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
        
        # Limit results untuk response
        display_limit = 20
        if len(results) > display_limit:
            query_result_str = "\n".join([str(x) for x in results[:display_limit]])
            query_result_str += f"\n... and {len(results) - display_limit} more"
        else:
            query_result_str = "\n".join([str(x) for x in results]) if results else "(no results)"
        
        # Generate response
        print("🤖 Generating response...")
        answer = generator(question, query, query_result_str)
        print(f"✅ Answer: {answer}")
        
        return ChatResponse(
            question=question,
            cypher_query=query,
            results=results[:display_limit] if results else [],
            answer=answer,
            success=True
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        # Count total heroes
        hero_count = driver.execute_query("MATCH (h:Hero) RETURN count(h) AS count")[0]['count']
        
        # Count by role
        roles = driver.execute_query("""
            MATCH (h:Hero)-[:HAS_ROLE]->(r:Role)
            RETURN r.name AS role, count(h) AS count
            ORDER BY count DESC
        """)
        
        # Count relationships
        rel_count = driver.execute_query("MATCH ()-[r]->() RETURN count(r) AS count")[0]['count']
        
        return {
            "total_heroes": hero_count,
            "total_relationships": rel_count,
            "heroes_by_role": roles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting Mobile Legends RAG API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
