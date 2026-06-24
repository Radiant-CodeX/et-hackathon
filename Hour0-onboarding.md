# Hour 0 — Onboarding

Read your section, run the commands, confirm your slice boots. Do this
**before** writing any code. Goal: by the end of Hour 0, all four of us
have the repo running locally and have seen our own piece respond.

The whole app runs on stubs by default (`USE_STUBS=true`), so nothing is
blocked on the Azure key or on anyone else finishing first.

---

## Everyone (first 15 minutes)

```bash
git clone <repo-url> && cd <repo>
cp .env.example .env          # leave USE_STUBS=true for now
docker-compose up --build
```

Confirm these open:

- Frontend: http://localhost:3000 (search sidebar + graph + detail panel)
- API docs: http://localhost:8000/docs
- Neo4j: http://localhost:7474 (login neo4j / password)

Smoke test the API:

```bash
curl http://localhost:8000/health
# {"status":"ok","azure_configured":false,"use_stubs":true}
```

If `docker-compose up` fails on a dependency version, that's the first
thing to fix — flag it in the team channel immediately. Better now than
at Hour 30.

Branch strategy: one branch per person.

```bash
git checkout -b feature/backend     # Person A
git checkout -b feature/frontend    # Person B
git checkout -b feature/agents      # Person C
git checkout -b feature/ops         # Person D
```

You each own separate files, so merges should be clean. The only shared
files are `docker-compose.yml`, `.env.example`, and `backend/models.py`
(the contract) — coordinate before touching those.

---

## Person A — Backend Core

Your slice is the API + graph + ingestion. Confirm it boots, then make
the real pieces real.

```bash
cd backend
pip install -r requirements.txt
USE_STUBS=true uvicorn main:app --reload
```

Confirm:

```bash
curl http://localhost:8000/entities
curl "http://localhost:8000/search?q=pump"
curl http://localhost:8000/graph/relationships
```

Run tests:

```bash
USE_STUBS=true pytest ../tests -v   # all should pass
```

Your real work (not done yet):

- `ingest.py` — the extraction prompt is a first draft. Tune it so it
  pulls clean entities/relationships from the real demo PDFs, not just
  the stub.
- `graph.py` — the queries work against the stub shape; validate them
  against actually-ingested data and add any missing relationship logic.
- Lock the contract: review `backend/models.py` + `docs/api_contract.md`
  with the team in the first hour. After that, no changes without a sync.
- By Hour 8: real schema populated in Neo4j so C can test on live data.

---

## Person B — Frontend

Your slice is the three-panel explorer. It already renders against the
backend (stub or real — you can't tell the difference, which is the point).

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

Confirm:

- Sidebar lists entities, search filters them
- Graph renders nodes color-coded by type
- Clicking a node opens the detail panel
- The three agent buttons return a result with confidence + citations

Your real work (not done yet):

- Graph performance + polish with 50+ real nodes (the stub graph is tiny).
- Make agent results read credibly — this is where UX meets the
  innovation score. Confidence bars, citation links, clean layout.
- Loading/error states everywhere.
- The 90-second demo video near the end.

If the backend isn't up, set `VITE_API_URL` or just run against a
teammate's instance. You are never blocked.

---

## Person C — Agents (the differentiator)

Your slice currently FAKES its intelligence. The stubs return hard-coded
strings. Your whole sprint is making them genuinely reason.

```bash
cd backend
pip install -r requirements.txt
USE_STUBS=true python -c "import agents; \
print(agents.run_rca('Pump-01', {'entity':{'name':'Pump-01','type':'Equipment'},'backlinks':[],'related':[]}))"
```

That prints the stub. Your job is to make it real.

Your real work (not done yet):

- The three agents in `backend/agents/` import the shared `llm` from
  `ai_client`. Wire real prompts and parse real JSON output.
- Build the RAG layer: index document chunks with `AzureOpenAIEmbeddings`
  - Chroma so findings can cite actual source text.
- Guard against hallucination — every finding must cite a real chunk or
  say "insufficient evidence." Judges will probe this.
- Tune prompts against the planted demo pattern (the SKF bearing failures
  across Pump-01 and Compressor-03) so RCA actually "discovers" it.

To go live, set `USE_STUBS=false` and fill Azure values in `.env`.

---

## Person D — Demo & Ops

Your slice is what makes the demo run and land. The scaffold has the
plumbing; you make it bulletproof and tell the story.

```bash
docker-compose up --build      # confirm one-command startup works clean
USE_STUBS=true pytest tests -v # confirm the suite passes
```

Check the seed ran:

```bash
curl http://localhost:8000/entities   # should list seeded entities
```

Your real work (not done yet):

- Demo data: only 5 docs exist, we want 10+. Add more, keep the planted
  bearing-failure pattern intact (it's the RCA "wow" moment). See
  `demo-data/` for the style.
- Verify `docker-compose up` works from a clean clone on a fresh machine,
  zero manual steps. Test this for real before submission.
- Expand `tests/` as the real backend lands.
- Demo script + timing + the 8-slide deck.

Security: `.env` is gitignored. Never commit the real Azure key. Confirm
`git status` never shows `.env`.

---

## End-of-Hour-0 checklist

- [ ] Everyone has the app running locally on stubs
- [ ] Everyone has confirmed their own slice responds
- [ ] `docker-compose up` works for all four of us
- [ ] Tests pass (`pytest tests -v`)
- [ ] API contract reviewed and locked by the team
- [ ] Branches created, no one working on `main`
- [ ] Any dependency-version issues flagged and fixed

Once all boxes are checked, Phase 2 (heads-down build) begins.
