from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from database import GraphDatabaseDriver
from response_generator import ResponseGenerator
from text_to_cypher import TextToCypher
from draft_system import DraftSystem
from typing import List, Optional
import traceback

# Global variables
schema = ""
ttc = None
generator = None
driver = None
draft_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown"""
    global schema, ttc, generator, driver, draft_system
    
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
    
    # Initialize Draft System
    print("⏳ Loading Draft System...")
    draft_system = DraftSystem()
    print("✅ Draft System ready")
    
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

class DraftRequest(BaseModel):
    banned: List[str] = []
    enemy: List[str] = []
    team: List[str] = []
    user_lane: str

class DraftResponse(BaseModel):
    recommendations: List[dict]
    team_analysis: Optional[dict] = None
    enemy_threats: Optional[List[dict]] = None
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
            "GET /stats": "Get database statistics",
            "POST /draft": "Get hero draft recommendations",
            "GET /draft/heroes": "Get all available heroes"
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

@app.post("/draft", response_model=DraftResponse)
async def get_draft_recommendations(request: DraftRequest):
    """
    Get hero draft recommendations based on current draft state
    
    Parameters:
    - banned: List of banned heroes
    - enemy: List of enemy picked heroes
    - team: List of team picked heroes (format: "hero-lane" or "hero")
    - user_lane: Lane position user wants to fill (gold/jungle/roam/mid/exp)
    """
    try:
        if not draft_system:
            raise HTTPException(status_code=503, detail="Draft system not initialized")
        
        # Validate user_lane
        valid_lanes = ["gold", "jungle", "roam", "mid", "exp"]
        if request.user_lane not in valid_lanes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid lane. Must be one of: {', '.join(valid_lanes)}"
            )
        
        # Get recommendations
        print(f"\n🎮 Draft Request:")
        print(f"   Banned: {request.banned}")
        print(f"   Enemy: {request.enemy}")
        print(f"   Team: {request.team}")
        print(f"   Lane: {request.user_lane}")
        
        result = draft_system.get_draft_recommendation(
            banned=request.banned,
            enemy=request.enemy,
            team=request.team,
            user_lane=request.user_lane
        )
        
        # Convert to response format
        recommendations = []
        for rec in result.recommendations:
            recommendations.append({
                "hero": rec.hero,
                "priority": rec.priority,
                "reasons": rec.reasons
            })
        
        team_analysis = None
        if result.team_analysis:
            team_analysis = {
                "role_counts": result.team_analysis.role_counts,
                "lane_counts": result.team_analysis.lane_counts,
                "role_diversity": result.team_analysis.role_diversity,
                "missing_lanes": result.team_analysis.missing_lanes,
                "damage_balance": result.team_analysis.damage_balance,
                "jungle_roam_valid": result.team_analysis.jungle_roam_valid,
                "lane_validation": result.team_analysis.lane_validation
            }
        
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        return DraftResponse(
            recommendations=recommendations,
            team_analysis=team_analysis,
            enemy_threats=result.enemy_threats,
            success=True
        )
        
    except Exception as e:
        print(f"❌ Draft Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/draft/heroes")
async def get_all_heroes():
    """Get list of all available heroes with their attributes"""
    try:
        if not draft_system:
            raise HTTPException(status_code=503, detail="Draft system not initialized")
        
        heroes_data = []
        for hero in sorted(draft_system.heroes):
            heroes_data.append({
                "name": hero,
                "roles": draft_system.hero_roles.get(hero, []),
                "lanes": draft_system.hero_lanes.get(hero, []),
                "damage_types": draft_system.hero_damage_types.get(hero, [])
            })
        
        return {
            "total": len(heroes_data),
            "heroes": heroes_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting Mobile Legends RAG API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
