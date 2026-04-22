# Knowledge Gate – KG + RAG Hybrid (Experimental / Stopped)

** Project status: Stopped – Not scalable to larger documents**  
This project implements a hybrid retrieval pipeline combining a Knowledge Graph (Neo4j) with semantic vector search (FAISS + sentence-transformers). Initial results on small documents were promising, but performance degraded significantly with larger document sets.

## Architecture

The pipeline follows this flow:


        User Query
            ↓
     Entity Extraction
            ↓
     Semantic Matching
            ↓
      KG Traversal
            ↓
      Path Ranking
            ↓
  Path Relevance Filtering
            ↓
     Query Generation
            ↓
  Weighted Retrieval (Vector + KG)
            ↓
     LLM Answer 



## Why results were poor on larger documents

- **Entity extraction** failed on ambiguous terms in long texts  
- **KG traversal** became exponentially slower with >1000 triples  
- **Path ranking** introduced noise – many irrelevant connections  
- **Weighted retrieval** did not generalise across different document domains  
- **LLM context window** overflowed when merging KG paths + vector chunks  

## Tech stack

- **Backend**: FastAPI  
- **Graph DB**: Neo4j  
- **Vector search**: FAISS + sentence-transformers (all‑MiniLM‑L6‑v2)  
- **LLM**: Groq (Mixtral / Llama)  
- **Frontend**: React + JavaScript (separate folder `/frontend`)  

## How to run (if you want to experiment)

### 1. Clone & setup backend
```bash
git clone https://github.com/your-username/knowledge-gate-rag.git
cd knowledge-gate-rag
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt ```



2. Set environment variables
Create a .env file:

    GROQ_API_KEY=your_key
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=your_password


3. Run Neo4j (Docker recommended)

    docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest


4. Start backend
    ```bash
        uvicorn main:app --reload
    ```

5. Run frontend (separate terminal)
    ```bash
        cd frontend
        npm install
        npm start
    ```

6. Upload a PDF via API
    ```bash
        curl -X POST -F "file=@your_document.pdf" http://localhost:8000/upload_pdf
    ```

7. Ask a question

    ```bash
        curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question":"What is X?"}'
    ```


What needs improvement (if someone forks this)

1. Replace naive entity extraction with a fine‑tuned NER model (e.g., SpaCy, GLiNER)

2. Implement batch KG traversal and path pruning

3. Add hybrid search with re‑ranking (e.g., Cohere or cross‑encoder)

4. Use smaller chunk + KG subgraph retrieval to fit LLM context

5. Evaluate on a benchmark like MultiHopQA or HotpotQA



Folder structure

.
├── app/
│   ├── kg/               # Neo4j helpers, triple extraction
│   ├── rag/              # Vector store, PDF loader, final pipeline
│   └── frontend/         # React frontend (separate)
├── data/                 # Uploaded PDFs (ignored by git)
├── requirements.txt
├── .env                  # API keys (ignored)
├── .gitignore
└── README.md


License

MIT – feel free to fork and improve.

    
**Action items for you:**

1. Create the `README.md` file with the content above.  
2. Replace `your-username` and `your-repo-name` with your actual GitHub username and repository name.  
3. If you don't use Docker for Neo4j, update the instructions accordingly.

When done, reply: **"Step 3 done"**

Then we'll move to **Step 4: Upload to GitHub** (commands and avoiding common mistakes).

