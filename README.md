# ShopSpark Agentic Support Bot

An end-to-end agentic customer support bot for ShopSpark, a consumer electronics e-commerce company: a custom RAG knowledge base, an order-lookup tool, a two-layer prompt-injection/tool-misuse guardrail, and a pass^k evaluation harness, plus the governance artifacts (OWASP threat model, EU AI Act Article 50 disclosure, governance memo) behind an actual launch recommendation.

Evaluated across 15 ground-truth cases (happy path, edge case, adversarial) at pass^5–pass^10: 100% pass rate, zero refunds issued and zero system-prompt leaks across 75 adversarial trials. Full results and the one real bug caught and fixed mid-evaluation are in [`eval/SUMMARY.md`](eval/SUMMARY.md).

## Architecture

```
corpus/        17 synthetic ShopSpark knowledge-base documents (return policy,
               shipping, warranty, product specs)
src/rag.py     chunk -> TF-IDF vectorize -> index in ChromaDB -> retrieve
src/tools.py   simulated order-lookup + refund tool, with the tool-call
               authorization guardrail (independent of anything the chat claims)
src/guardrail.py   input-layer prompt-injection classifier (regex + LLM
               second opinion), runs before the planner ever sees a message
src/orchestrator.py   the perceive -> plan -> act -> observe -> respond loop,
               using the Claude Code CLI (`claude -p`) as the LLM backend
eval/          ground-truth QA dataset (15 pairs, happy/edge/adversarial) and
               the pass^k evaluation harness
docs/          OWASP threat model, EU AI Act Article 50 disclosure, governance memo
logs/transcript.jsonl   full trace of every turn run during development/eval
```

### Why ChromaDB with precomputed TF-IDF vectors instead of a hosted embedding model

This sandbox has no outbound network access to model-hosting endpoints (e.g. huggingface.co), so ChromaDB's default download-based embedding function can't run. TF-IDF vectors are computed locally with scikit-learn and passed into ChromaDB as precomputed embeddings, so the vector database, its persistence, and its cosine-similarity search are all real and working, just with a locally-computable vector representation instead of a downloaded neural embedding model. Swapping in a hosted or local dense-embedding model later is a one-line change (`src/rag.py`, the `Vectorizer` class).

### Why the Claude Code CLI as the LLM backend

No LLM API key is available to scripts in this sandbox, but the Claude Code CLI itself (`claude`) is authenticated in this environment. `src/orchestrator.py` shells out to `claude -p` with all tool access disabled (`--disallowedTools "*"`) so each call is a plain, isolated text completion, real LLM inference for planning and response generation, with no ability for the subprocess call itself to take any action.

## Running it

```
pip install -r requirements.txt
cd src
python3 rag.py            # builds the vector index (also happens automatically on first bot run)
python3 orchestrator.py   # runs 3 demo queries including the injection attack
```

## Running the evaluation

```
cd eval
python3 harness.py --k 5                              # full suite, pass^5
python3 harness.py --k 10 --category adversarial       # targeted proof run
```

See `eval/SUMMARY.md` for the full results and the reproduction commands used to generate each one.

## Repository guide

| Component | Where |
|---|---|
| RAG knowledge base | `corpus/` (17 docs) + `src/rag.py` |
| Order-lookup tool | `src/tools.py` |
| Evaluation harness + ground-truth dataset | `eval/harness.py`, `eval/qa_dataset.json`, results in `eval/results_*.json` and `eval/SUMMARY.md` |
| OWASP threat model | `docs/owasp-threat-model.md` |
| EU AI Act Article 50 disclosure | `docs/eu-ai-act-article-50-disclosure.md` |
| Governance memo | `docs/governance-memo.md` |
