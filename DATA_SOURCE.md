# Data Source and Problem Statement

## Problem statement

Financial filings contain important information about a company's liquidity, debt, operations, supply chain exposure, revenue drivers, and legal risks, but the information is distributed across a long regulatory document. This project provides a semantic question-answering interface that retrieves relevant passages from an SEC filing and uses Gemini to synthesize an answer with source snippets.

The system is intended for exploratory analysis and document navigation. It is not an investment recommendation, an accounting opinion, or a substitute for reviewing the original filing.

## Primary data source

- **Publisher:** U.S. Securities and Exchange Commission (SEC)
- **Repository:** EDGAR company filing archive
- **Company:** Apple Inc.
- **Ticker:** AAPL
- **Form:** 10-K annual report
- **Accession number:** `0000320193-25-000079`
- **CIK:** `0000320193`
- **Filed:** October 31, 2025
- **Reporting period ended:** September 27, 2025
- **Official filing index:** <https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/>
- **Raw filing URL:** <https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/0000320193-25-000079.txt>

The raw filing is stored in `sec-edgar-filings/AAPL/10-K/0000320193-25-000079/full-submission.txt`. The file is the SEC EDGAR submission text returned by the downloader and includes the filing header and submitted documents.

## Collection method

`ingest.py` uses `sec-edgar-downloader` to request the latest available AAPL 10-K:

```text
dl.get("10-K", "AAPL", limit=1)
```

The downloader writes the filing under `sec-edgar-filings/`. Because SEC access requires a descriptive User-Agent, users reproducing the download should replace the placeholder contact details in `ingest.py` with their own project name and contact email, then respect SEC access policies.

## Processing and derived data

The application reads the raw text filing, splits it into overlapping text chunks, embeds chunks locally with `all-MiniLM-L6-v2`, and stores the resulting Chroma vector index in `chroma_db_clean/`. The tracked index is a derived artifact, not an additional source of truth.

The current Streamlit app retrieves up to 10 relevant chunks and sends the retrieved context to `gemini-3.6-flash` for synthesis. The raw filing remains available so answers can be checked against the original source material.

## Repository data inventory

| Path | Role |
| --- | --- |
| `sec-edgar-filings/AAPL/10-K/0000320193-25-000079/full-submission.txt` | Original SEC EDGAR filing text |
| `chroma_db_clean/` | Derived Chroma embeddings and metadata used by `app.py` |
| `ingest.py` | Downloads the source filing from SEC EDGAR |
| `app.py` | Streamlit retrieval and question-answering application |
| `agent.py` | Standalone retrieval pipeline example |

The development indexes in `chroma_db/` and `chroma_db_local/` are intentionally excluded from version control. The reproducible source filing and the clean application index are included in the repository.

## Limitations and responsible use

- This dataset currently contains one company's annual filing, not a representative sample of public companies.
- The phrase "latest" in `ingest.py` is time-dependent; a future run may download a different filing than the pinned artifact currently committed here.
- Generated answers may omit context or make interpretation errors. Always verify material claims in the original SEC filing.
- SEC filing text may contain formatting artifacts introduced by the EDGAR submission format.
- SEC data is public regulatory information; users should consult the SEC website for the authoritative and most current version.
