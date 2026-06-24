# Industrial Knowledge Intelligence — Frontend (Person B)

React + Vite + Cytoscape knowledge-graph explorer for the ET AI Hackathon 2026,
Problem Statement #8. This is the **Person B / Frontend UI** vertical slice.

## Quick start

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

The app runs **standalone out of the box** — it ships with realistic demo data
(`src/api/mockClient.js`) so it works before Person A's backend exists. When the
FastAPI backend is up at `http://localhost:8000`, every call automatically uses
it instead (the top-right badge flips from **Demo data** to **Live backend**).
No code change needed — set `VITE_API_URL` only if the backend is elsewhere.

## Tests (TDD)

```bash
npm test           # run once
npm run test:watch # watch mode
```

Covers: dashboard render, three-panel layout, mock API, graph component,
search bar, entity panel, and agent-result rendering (TDD sections A1–A7).

## Architecture

```
src/
  api/
    client.js        # axios → backend, with mock fallback
    mockClient.js    # demo graph + agent responses
  components/
    Graph.jsx        # Cytoscape explorer (colour-coded node types)
    SearchBar.jsx
    DocumentBrowser.jsx
    EntityPanel.jsx  # details + backlinks + agent buttons/results
    AgentButtons.jsx # Run RCA / Check Compliance / Equipment History
    AgentResult.jsx  # summary + findings + confidence + citations
    Loading.jsx / ErrorState.jsx
    nodeTypes.js     # node-type colour map
  pages/
    Dashboard.jsx    # three-panel shell, wires everything together
```

### Node-type colours

| Type        | Colour |
| ----------- | ------ |
| Equipment   | Blue   |
| Procedure   | Purple |
| FailureMode | Red    |
| Supplier    | Teal   |
| Compliance  | Amber  |

## API contract consumed (locked §5.2)

- `GET /graph/relationships`
- `GET /entities`
- `GET /entities/{id}`
- `GET /search?q=`
- `POST /agents/run`

## Demo flow

Search **Pump-01** → click the node → graph centres + backlinks load →
**Run RCA** → it surfaces the bearing-failure pattern shared across three
machines tied to supplier SKF → **Check Compliance** → flags a missing permit
sign-off against OISD-118.
