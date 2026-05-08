# RepoMentor AI Architecture

This document contains presentation-ready architecture diagrams for RepoMentor AI.

It includes:

1. Local / development architecture
2. Streamlit prototype architecture
3. Cloud / GCP architecture
4. Vertex AI retrieval architecture
5. CI/CD architecture
6. System evolution
7. Two "single comprehensive" architectures:
   - one for the full local system
   - one for the full cloud system

---

## 1. Local / Development Architecture

```mermaid
flowchart LR
    U["User"] --> F["Next.js / TypeScript Frontend (local)"]
    F --> B["FastAPI Backend (local)"]

    B --> CA["Course Assistant"]
    B --> AB["Assignment Builder"]
    B --> RR["Repo Reviewer"]
    B --> DT["Developer Tools / MCP Console"]

    CA --> RAG["Local RAG Layer"]
    AB --> RAG

    RAG --> DOCS["docs/syllabus.txt + docs/schedule.txt"]
    RAG --> CHUNK["Chunking"]
    CHUNK --> EMB["sentence-transformers embeddings"]
    EMB --> VDB["ChromaDB"]
    VDB --> RET["Similarity retrieval"]
    RET --> GROQ["Groq API"]

    RR --> CRA["Code Review Agent"]
    RR --> SA["Security Agent"]
    RR --> DA["Documentation Agent"]
    CRA --> GROQ
    SA --> BANDIT["Bandit scan"]
    SA --> GROQ
    DA --> GROQ

    DT --> MCP["MCP tool layer"]
```

### Notes
- Frontend is `Next.js / TypeScript`
- Backend is `FastAPI`
- `Course Assistant` and `Assignment Builder` use local RAG
- Local RAG uses:
  - `docs/syllabus.txt`
  - `docs/schedule.txt`
  - chunking
  - `sentence-transformers`
  - `ChromaDB`
- `Repo Reviewer` uses three review agents plus `Bandit`

---

## 2. Streamlit Prototype Architecture

```mermaid
flowchart LR
    U["User"] --> S["Streamlit Prototype UI"]
    S --> B["Python / FastAPI Services"]
    B --> RAG["Local RAG"]
    B --> RR["Repo Reviewer"]
    RAG --> CHROMA["ChromaDB + local embeddings"]
    RR --> AGENTS["Review agents"]
```

### Notes
- Streamlit was the earlier rapid prototype
- It was useful for validating workflows quickly
- The main product frontend later moved to `Next.js`

---

## 3. Cloud / GCP Architecture

```mermaid
flowchart LR
    GH["GitHub"] --> GHA["GitHub Actions CI/CD"]
    GHA --> WIF["Workload Identity Federation"]
    WIF --> GCP["Google Cloud Project"]

    GHA --> AR["Artifact Registry / Cloud Build"]
    AR --> CRF["Cloud Run Frontend"]
    AR --> CRB["Cloud Run Backend"]

    U["User"] --> CRF["Next.js Frontend on Cloud Run"]
    CRF --> CRB["FastAPI Backend on Cloud Run"]

    CRB --> CA["Course Assistant"]
    CRB --> AB["Assignment Builder"]
    CRB --> RR["Repo Reviewer"]
    CRB --> DT["Developer Tools / MCP Console"]

    CA --> VRAG["Cloud Retrieval Layer"]
    AB --> VRAG

    VRAG --> DOCS["Syllabus + Schedule chunks"]
    VRAG --> VERTEX["Vertex AI Embeddings (gemini-embedding-001)"]
    VERTEX --> INDEX["Lightweight local embedding index in backend"]
    INDEX --> RET["Cosine similarity retrieval"]
    RET --> GROQ["Groq API"]

    RR --> CRA["Code Review Agent"]
    RR --> SA["Security Agent"]
    RR --> DA["Documentation Agent"]
    CRA --> GROQ
    SA --> BANDIT["Bandit"]
    SA --> GROQ
    DA --> GROQ

    CRB --> SM["Secret Manager"]
    SM --> KEY["GROQ_API_KEY"]

    DT --> MCP["MCP tool layer"]
```

### Notes
- Frontend is deployed to `Cloud Run`
- Backend is deployed to `Cloud Run`
- CI/CD is done through `GitHub Actions`
- Authentication to GCP is done through `Workload Identity Federation`
- Vertex AI is used for embeddings in the cloud path
- Retrieval is still handled by the backend

---

## 4. Vertex AI Retrieval Path

```mermaid
flowchart LR
    Q["User question"] --> QE["Vertex query embedding"]
    D["Course document chunks"] --> DE["Vertex document embeddings"]
    DE --> IDX["Stored embedding index"]
    QE --> SIM["Cosine similarity search"]
    IDX --> SIM
    SIM --> TOPK["Top relevant chunks"]
    TOPK --> LLM["Groq answer generation"]
    LLM --> A["Final grounded answer"]
```

### Notes
- In cloud mode, Vertex AI generates embeddings
- The backend stores and retrieves vectors itself
- This is **not yet** a managed vector search deployment

---

## 5. CI/CD Flow

```mermaid
flowchart LR
    DEV["Developer pushes to GitHub main"] --> CI["GitHub Actions"]
    CI --> CHECKS["Validation / checks"]
    CI --> AUTH["Authenticate to GCP via Workload Identity Federation"]
    AUTH --> BUILD1["Build backend image"]
    BUILD1 --> DEPLOY1["Deploy backend to Cloud Run"]
    DEPLOY1 --> URL["Capture backend URL"]
    URL --> DEPLOY2["Deploy frontend to Cloud Run"]
    DEPLOY2 --> LIVE["Live app updated"]
```

### Notes
- CI validates code
- CD deploys backend and frontend
- Authentication uses temporary identity, not long-lived service account keys

---

## 6. System Evolution

```mermaid
flowchart LR
    P["Streamlit prototype"] --> M["Next.js product frontend"]
    M --> C["Cloud Run deployment on GCP"]
    C --> V["Vertex AI embedding integration"]
    V --> D["GitHub Actions CI/CD"]
```

### Notes
- Streamlit was the proof-of-concept
- Next.js became the polished product UI
- GCP hosting and Vertex AI made the system cloud-native
- CI/CD made deployment repeatable

---

## 7. Comprehensive Local Architecture

This is the "everything in one place" local architecture.

```mermaid
flowchart TB
    U["User"] --> FE["Next.js / TypeScript Frontend (local)"]
    U --> SP["Streamlit Prototype (legacy local prototype)"]

    FE --> BE["FastAPI Backend"]
    SP --> BE

    subgraph APP["Application Modules"]
        CA["Course Assistant"]
        AB["Assignment Builder"]
        RR["Repo Reviewer"]
        DT["Developer Tools / MCP Console"]
    end

    BE --> CA
    BE --> AB
    BE --> RR
    BE --> DT

    subgraph RAG["Local Retrieval / RAG"]
        DOCS["docs/syllabus.txt + docs/schedule.txt"]
        CHUNK["Chunking"]
        LEMB["sentence-transformers embeddings"]
        CHROMA["ChromaDB"]
        LRET["Cosine / similarity retrieval"]
    end

    DOCS --> CHUNK
    CHUNK --> LEMB
    LEMB --> CHROMA
    CHROMA --> LRET

    CA --> LRET
    AB --> LRET

    subgraph LLM["Generation Layer"]
        GROQ["Groq API / direct HTTP client"]
    end

    LRET --> GROQ
    CA --> GROQ
    AB --> GROQ

    subgraph REVIEW["Repo Reviewer Agent System"]
        CRA["Code Review Agent"]
        SA["Security Agent"]
        DA["Documentation Agent"]
        SYN["Synthesizer Agent"]
        BANDIT["Bandit security scan"]
    end

    RR --> CRA
    RR --> SA
    RR --> DA
    CRA --> GROQ
    SA --> BANDIT
    SA --> GROQ
    DA --> GROQ
    CRA --> SYN
    SA --> SYN
    DA --> SYN

    subgraph DEVTOOLS["Internal Tool Surface"]
        MCP["MCP tools:
analyze_repo
ask_course_assistant
get_review_history"]
    end

    DT --> MCP

    subgraph LOCALDATA["Local Support Data"]
        ENV[".env / local config"]
        SAMPLE["sample_repos/"]
        DB["Optional local Postgres / DB path"]
    end

    BE --> ENV
    RR --> SAMPLE
    MCP --> DB
```

### Local Architecture Summary
- Two local UI paths exist:
  - `Next.js` current product frontend
  - `Streamlit` older prototype path
- One Python backend powers all major product workflows
- Local RAG uses `sentence-transformers + ChromaDB`
- Groq powers generation
- Repo Reviewer is multi-agent and uses `Bandit`
- Developer Tools expose internal MCP-style operations

---

## 8. Comprehensive Cloud / GCP Architecture

This is the "everything in one place" cloud architecture.

```mermaid
flowchart TB
    USER["User / Browser"] --> FRONT["Cloud Run Frontend
Next.js / TypeScript"]

    subgraph GITHUB["GitHub + CI/CD"]
        REPO["GitHub Repo"]
        ACTIONS["GitHub Actions"]
        CI["CI checks:
backend compile
frontend typecheck"]
        CD["CD deploy workflow"]
        WIF["Workload Identity Federation / OIDC"]
    end

    REPO --> ACTIONS
    ACTIONS --> CI
    ACTIONS --> CD
    CD --> WIF

    subgraph GCP["Google Cloud Platform"]
        AR["Artifact Registry"]
        CB["Cloud Build"]
        RUNF["Cloud Run Frontend"]
        RUNB["Cloud Run Backend"]
        SM["Secret Manager"]
        VTX["Vertex AI
gemini-embedding-001"]
    end

    WIF --> GCP
    CD --> CB
    CB --> AR
    AR --> RUNB
    CD --> RUNF

    FRONT --> BACK["Cloud Run Backend
FastAPI"]
    RUNF --> FRONT
    RUNB --> BACK

    BACK --> SKEY["GROQ_API_KEY"]
    SM --> SKEY

    subgraph MODULES["Backend Product Modules"]
        CCA["Course Assistant"]
        AAB["Assignment Builder"]
        RRR["Repo Reviewer"]
        DDT["Developer Tools / MCP Console"]
    end

    BACK --> CCA
    BACK --> AAB
    BACK --> RRR
    BACK --> DDT

    subgraph CLOUDRAG["Cloud Retrieval Path"]
        DOC["Syllabus + schedule chunks"]
        VEMB["Vertex embeddings"]
        IDX["Local embedding index file in backend"]
        CRET["Custom cosine similarity retrieval"]
    end

    DOC --> VEMB
    VTX --> VEMB
    VEMB --> IDX
    IDX --> CRET
    CCA --> CRET
    AAB --> CRET

    subgraph GEN["LLM Generation Layer"]
        GHTTP["Groq API
direct HTTP client"]
    end

    CRET --> GHTTP
    CCA --> GHTTP
    AAB --> GHTTP

    subgraph REVIEWCLOUD["Repo Reviewer Cloud Path"]
        CAG["Code Review Agent"]
        SAG["Security Agent"]
        DAG["Documentation Agent"]
        SYNG["Synthesizer Agent"]
        BSEC["Bandit"]
        GIT["git clone support"]
        SAMPLEC["sample_repos bundled in backend image"]
    end

    RRR --> CAG
    RRR --> SAG
    RRR --> DAG
    CAG --> GHTTP
    SAG --> BSEC
    SAG --> GHTTP
    DAG --> GHTTP
    CAG --> SYNG
    SAG --> SYNG
    DAG --> SYNG
    RRR --> GIT
    RRR --> SAMPLEC

    subgraph MCPTOOLS["Developer Tools"]
        MCP2["MCP tools:
analyze_repo
ask_course_assistant
get_review_history (only if DB configured)"]
    end

    DDT --> MCP2

    subgraph FUTURE["Future / optional cloud extensions"]
        BQ["BigQuery analytics"]
        VVS["Managed Vector Search
(future option)"]
        SQL["Cloud SQL / hosted Postgres
(future review history persistence)"]
    end
```

### Cloud Architecture Summary
- `GitHub Actions` drives CI/CD
- `Workload Identity Federation` securely connects GitHub Actions to GCP
- Frontend and backend are deployed on `Cloud Run`
- Backend uses:
  - `Secret Manager`
  - `Vertex AI` for embeddings
  - custom retrieval logic for similarity search
  - `Groq` for answer and content generation
- `Repo Reviewer` includes:
  - multi-agent analysis
  - `Bandit`
  - GitHub cloning support
  - bundled sample repos
- BigQuery and managed vector search are natural future improvements, not core to the current working deployment

---

## 9. Presentation Guidance

If you only show two diagrams, show these:

1. **Comprehensive Local Architecture**
2. **Comprehensive Cloud / GCP Architecture**

Those two together cover:
- prototype to product evolution
- local vs cloud behavior
- retrieval path differences
- CI/CD
- deployment
- tool/runtime differences

---

## 10. One-Sentence Architecture Summary

RepoMentor AI evolved from a Streamlit prototype into a Next.js + FastAPI GenAI platform where local development uses ChromaDB and sentence-transformers for retrieval, while the deployed GCP version runs on Cloud Run, uses Vertex AI for embeddings, a custom backend retrieval layer for grounding, Groq for generation, and GitHub Actions CI/CD for repeatable deployment.
