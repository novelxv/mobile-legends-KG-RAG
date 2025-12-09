# Mobile Legends Knowledge Graph RAG System

AI-powered Mobile Legends hero information system using Knowledge Graph + RAG (Retrieval-Augmented Generation).

## 🎮 Features

- **Knowledge Graph**: Neo4j database dengan 130+ heroes dan relationships antar hero
- **RAG Pipeline**: 
  - 🧠 **Text-to-Cypher**: Natural language → Neo4j Cypher query (Gemini 2.5 Flash)
  - 🔍 **Query Execution**: Real-time graph database queries
  - 💬 **Response Generation**: Query results → Natural language (Gemini 2.5 Flash)
- **Two Interfaces**:
  - 💻 CLI version (`rag.py`) - Terminal-based interaction
  - 🌐 **Web UI** dengan Mobile Legends theme (Next.js + FastAPI)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Question                             │
│          "Who are the best marksman heroes?"                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Text-to-Cypher (Gemini 2.5)                     │
│  Question → Cypher Query                                     │
│  MATCH (h:Hero)-[:HAS_ROLE]->(r:Role {name: 'marksman'})   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Neo4j Graph Database                       │
│  Execute query & retrieve hero data                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Response Generator (Gemini 2.5)                    │
│  Query Results → Natural Language Response                   │
│  "Here are the top marksman heroes: Layla, Miya..."         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: Web UI (Recommended)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database:
```bash
# Copy template
copy config_template.toml config.toml

# Edit config.toml dengan Neo4j credentials Anda
```

3. Ingest data (jika belum):
```bash
python ingest_prolog.py
```

4. Start web UI:
```bash
# Automatic (Windows)
start_web_ui.bat

# Manual
# Terminal 1: Backend
python api_server.py

# Terminal 2: Frontend
cd web-ui
npm install
npm run dev
```

5. Open browser: `http://localhost:3000`

📖 **Detailed guide**: See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md)

### Option 2: CLI Version

```bash
python rag.py
```

## 📁 Project Structure

```
├── api_server.py          # FastAPI backend server
├── rag.py                 # CLI interface untuk testing
├── text_to_cypher.py      # AI model: Natural Language → Cypher Query
├── response_generator.py  # AI model: Query Results → Natural Response
├── database.py            # Neo4j driver & connection handler
├── ingest_prolog.py       # Data ingestion dari Prolog ke Neo4j
├── config.py              # Configuration loader
├── config.toml            # Database & API credentials
├── schema_example.txt     # Neo4j schema untuk AI models
├── web-ui/                # Next.js frontend
│   ├── app/
│   │   ├── page.tsx      # Main chat interface
│   │   ├── layout.tsx    # Layout dengan ML theme
│   │   └── globals.css   # Custom styling
│   ├── package.json
│   └── next.config.js
└── prolog_facts/          # Hero data dalam format Prolog
    ├── hero.pl           # Hero attributes
    ├── role.pl           # Hero roles
    ├── lane.pl           # Lane preferences
    ├── counter.pl        # Counter relationships
    └── ...
```

## 🔄 RAG Pipeline Details

### 1. Text-to-Cypher (`text_to_cypher.py`)
- **Model**: Google Gemini 2.5 Flash
- **Input**: Natural language question (e.g., "Who counters Miya?")
- **Output**: Neo4j Cypher query
- **Features**:
  - Schema-aware query generation
  - Few-shot learning examples
  - Case-insensitive matching
  - Fallback query handling

### 2. Query Execution (`database.py`)
- **Database**: Neo4j Graph Database
- **Connection**: Neo4j driver with connection pooling
- **Operations**:
  - Execute Cypher queries
  - Retrieve hero nodes and relationships
  - Statistics aggregation

### 3. Response Generator (`response_generator.py`)
- **Model**: Google Gemini 2.5 Flash
- **Input**: Question + Query + Query Results
- **Output**: Natural language response
- **Features**:
  - Context-aware responses
  - Mobile Legends terminology
  - Concise and accurate answers
  - No hallucination (only uses query results)

## 🌐 Web UI Features

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS + Custom ML theme
- **Components**:
  - Real-time chat interface
  - Message history display
  - Sample questions quick access
  - Query inspector (shows generated Cypher)
  - Live database statistics
  - Responsive design for mobile & desktop

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Endpoints**:
  - `POST /chat` - Process user questions
  - `GET /stats` - Database statistics
  - `GET /` - Health check
- **Features**:
  - CORS enabled for frontend
  - Global model initialization (on startup)
  - Error handling & fallback queries
  - Rate limit handling with delays

## 📁 Project Structure

## 🎨 Mobile Legends Theme

Web UI menggunakan official Mobile Legends color palette:
- **Primary**: Deep Blue (#2B4C7E)
- **Accent**: Gold (#FDB933)
- **Dark**: (#0F1419)
- **Background**: Dark gradients dengan blue accents
- **Typography**: Custom fonts untuk gaming aesthetic

## 🔧 Configuration

### Setup `config.toml`
```toml
[neo4j]
uri = "bolt://localhost:7687"
username = "neo4j"
password = "your-password"

[gemini]
api_key = "your-gemini-api-key"
```

### Required Environment
- Python 3.8+
- Node.js 18+ (untuk Web UI)
- Neo4j Database (local atau cloud)
- Google Gemini API key

## 💡 Example Questions

- "Who are the best marksman heroes?"
- "Which heroes counter Miya?"
- "Show me all assassin heroes"
- "What heroes can play in the jungle lane?"
- "List heroes with high physical attack"
- "Who has burst damage specialty?"

## 🛠️ Troubleshooting

### Backend Issues
- **Models not loading**: Tunggu 3-5 menit untuk Response Generator
- **API key error**: Periksa `config.toml` dan Gemini API key
- **Database connection**: Pastikan Neo4j running dan credentials benar

### Frontend Issues
- **Cannot connect**: Pastikan backend running di port 8000
- **CORS errors**: Check FastAPI CORS middleware settings
- **Stats not showing**: Tunggu backend fully initialized

## 📖 Documentation

- **Web UI Guide**: [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) - Detailed setup dan features
- **API Documentation**: FastAPI docs di `http://localhost:8000/docs`
- **Graph Schema**: Lihat `schema_example.txt` untuk struktur database

## 🎓 Academic Context

This repository is prepared for **Project Task II**, IF4070 Knowledge Representation and Reasoning course (2025-1), STEI-ITB.

### Key Concepts Implemented:
- **Knowledge Graph**: Representasi pengetahuan menggunakan graph database
- **Semantic Relationships**: Hero relationships (counters, roles, lanes)
- **RAG (Retrieval-Augmented Generation)**: Kombinasi retrieval + generation
- **Reasoning**: Cypher query generation untuk complex reasoning

## 🤝 Contributing

Project ini adalah bagian dari tugas kuliah. Untuk development:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push dan create Pull Request

---

# Original CLI Usage Guide

## How to use (CLI)
1. (Optional) Make a virtual environment. Command: `py -m venv ./venv`
2. Install required dependencies. Command: `pip install -r requirements.txt`
3. Copy `config_template.toml` to `config.toml`.
4. Modify `config.toml` based on your database configuration.
5. Run RAG system for testing. Command: `py rag.py`
6. Test with one sample question, such as "How many players?".

## Additional configuration
- You may need to change the schema path.
- You may need to set `HF_HOME` environment variable to determine the location of model cache.
  - More information: https://huggingface.co/docs/datasets/cache
- You may need to install other versions of PyTorch to support GPU (and possibly modify the code).
- You may need to change the models for better performance.
- You may need to handle Neo4j exceptions in case the generated Cypher is malformed.

## References
- https://neo4j.com/docs/python-manual/current/
