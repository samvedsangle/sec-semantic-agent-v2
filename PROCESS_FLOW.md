# SEC Semantic Auditor Process Flow

The diagram below is rendered by GitHub as an interactive Mermaid flow chart. Select a node to open the related source file or data artifact.

```mermaid
flowchart TD
    A([Start Streamlit app]) --> B{Google API key available?}
    B -- No --> C[Enter key in sidebar]
    C --> B
    B -- Yes --> D[Load SEC filing]
    D --> E[Load local HuggingFace embeddings]
    E --> F[Open Chroma vector index]
    F --> G([SEC vector database ready])
    G --> H[User enters or selects a question]
    H --> I{Question is not blank?}
    I -- No --> J[Show validation warning]
    I -- Yes --> K[Retrieve top 5 relevant chunks]
    K --> L[Send retrieved context to Gemini Flash Lite]
    L --> M{Gemini request succeeds?}
    M -- Yes --> N[Display audit response]
    N --> O[Display retrieved source snippets]
    M -- 429 --> P[Show quota or rate-limit guidance]
    M -- Other error --> Q[Show unexpected-error message]

    click A "../blob/main/app.py" "Open the Streamlit app"
    click D "../blob/main/sec-edgar-filings/AAPL/10-K/0000320193-25-000079/full-submission.txt" "Open the pinned SEC filing"
    click E "../blob/main/app.py" "Open the embedding configuration"
    click F "../blob/main/chroma_db_clean" "Open the derived Chroma index"
    click H "../blob/main/app.py" "Open the query input"
    click K "../blob/main/app.py" "Open retrieval configuration"
    click L "../blob/main/app.py" "Open Gemini configuration"
    click P "../blob/main/app.py" "Open error handling"

    classDef source fill:#173f5f,stroke:#20639b,color:#ffffff
    classDef decision fill:#f6d55c,stroke:#ed553b,color:#1f2933
    classDef success fill:#3caea3,stroke:#20639b,color:#ffffff
    classDef error fill:#ed553b,stroke:#c0392b,color:#ffffff
    class A,D,E,F,H,K,L source
    class B,I,M decision
    class G,N,O success
    class J,P,Q error
```

## Process stages

| Stage | What happens | Source |
| --- | --- | --- |
| Collection | Downloads the latest AAPL 10-K from SEC EDGAR | [ingest.py](ingest.py) |
| Source data | Stores the pinned Apple filing used by the project | [full-submission.txt](sec-edgar-filings/AAPL/10-K/0000320193-25-000079/full-submission.txt) |
| Embeddings | Loads `all-MiniLM-L6-v2` locally | [app.py](app.py) |
| Retrieval | Searches the Chroma index for the five most relevant chunks | [app.py](app.py) |
| Synthesis | Sends retrieved context to `gemini-3.5-flash-lite` with five retries | [app.py](app.py) |
| Presentation | Shows the answer and retrieved evidence in Streamlit | [app.py](app.py) |
| Provenance | Documents the dataset, source URLs, and limitations | [DATA_SOURCE.md](DATA_SOURCE.md) |

## Reproduce the pipeline

1. Install dependencies from [requirements.txt](requirements.txt).
2. Set `GOOGLE_API_KEY` or enter it in the Streamlit sidebar.
3. Run `ingest.py` only when you intentionally want to download a newer filing.
4. Start the interface with `streamlit run app.py`.

The raw SEC filing is the source of truth. The Chroma files are derived search artifacts, and Gemini output should be checked against the displayed source snippets and original filing.
