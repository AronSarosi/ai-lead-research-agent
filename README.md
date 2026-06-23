# AI Lead Research Agent

Turn an Ideal Client Profile into review-ready cold-outreach drafts.

You describe the kind of client you want (industry, size, location, keywords) and
the offer you're pitching. For each matching company the agent:

1. finds the company and researches it (what they do, recent signals, fit)
2. hypothesises a couple of pain points your offer could solve
3. finds a likely contact / decision-maker
4. drafts a short, personalised outreach message that ties a specific detail
   about them to your offer

> **Drafts only.** This tool researches and writes. It never sends anything. Every
> message is yours to read, edit, and send (or bin) by hand.

The drafts are written in *your* voice, pulled from `profile.yaml`, so they sound
like you rather than generic AI.

---

## What's under the hood

- **Streamlit** UI - enter the ICP, run, edit the drafts in a table, export to CSV
- **LangGraph + LangChain** agent - a small pipeline per company:
  `research -> pain points -> contact -> draft`
- **Tavily** for web search
- **OpenAI** by default, with a two-model split: `gpt-4o-mini` for the cheap research
  steps and a stronger `OPENAI_DRAFT_MODEL` (default `gpt-4o`) just for writing the
  outreach, so drafts don't sound generic. Azure OpenAI supported via one env switch.
- **Langfuse** tracing - optional, only on when its keys are set

```
ai-lead-research-agent/
  app.py            # Streamlit UI
  profile.yaml      # your name, offer, demo links, tone notes  <- edit this
  sample_icp.yaml   # the sample the form is pre-filled from
  agent/            # config, schemas, llm, search, graph, enrichment, export
  tests/            # pytest suite (fully mocked, no live API calls)
  Dockerfile        # production image for Google Cloud Run
```

### How a run is wired

```
ICP  ->  discover_companies  ->  per-company pipeline (run in a small thread pool)
                                   research -> pain_points -> contact -> draft
                                                                        |
                                            editable results table -> CSV
```

`discover_companies` turns the ICP into a shortlist (or uses your manual list and
skips discovery entirely). Each company then runs its own compiled LangGraph
pipeline; companies are researched a few at a time in a thread pool, and a
failure on one company never sinks the rest of the batch. The research steps run
on the cheap model; only the final draft uses the stronger one.

---

## Setup

Requires **Python 3.10+**.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your keys
cp .env.example .env
# then open .env and fill in OPENAI_API_KEY and TAVILY_API_KEY
```

### API keys you need

| Key | What for | Where to get it |
| --- | --- | --- |
| `OPENAI_API_KEY` | The LLM that researches and drafts | https://platform.openai.com/api-keys |
| `TAVILY_API_KEY` | Web search (free tier available) | https://app.tavily.com |
| `LANGFUSE_*` | Optional tracing | https://cloud.langfuse.com |

**Model choice.** `OPENAI_MODEL` (default `gpt-4o-mini`) handles research; `OPENAI_DRAFT_MODEL`
(default `gpt-4o`) writes the outreach. Want sharper copy? Raise `OPENAI_DRAFT_MODEL` (e.g.
`gpt-4.1`). Want it cheaper? Set both to `gpt-4o-mini`. A 5-company run is a few cents either way.

**Temperature.** Two knobs, both optional. `LLM_TEMPERATURE` (default `0.4`) keeps the
structured research steps consistent; `LLM_DRAFT_TEMPERATURE` (default `0.6`) runs the draft
step a touch warmer so the outreach reads less robotic. Lower for safer output, higher for more
variety (0.0 to 1.0).

Without a Tavily key the agent still runs, it just drafts from the ICP alone with
less company-specific detail.

---

## Run it

```bash
streamlit run app.py
```

It opens in your browser. The form is pre-filled from `sample_icp.yaml`, so you can:

1. Hit **Run research** to try it on the sample (boutique London recruitment agencies)
2. Watch it find companies and research each one
3. Edit any draft directly in the results table
4. Click **Download CSV** to export your edited drafts

Then change the ICP fields to your own target and run again.

---

## Run as a container

The repo ships a `Dockerfile` (Python 3.12 slim, non-root user) so you can run it
anywhere without a local Python setup.

```bash
# Build
docker build -t lead-research-agent .

# Run, passing your keys in from the host .env
docker run --rm -p 8080:8080 --env-file .env lead-research-agent
```

Then open http://localhost:8080. The container listens on `$PORT` (default 8080)
and binds `0.0.0.0`, so it slots straight into most container platforms.

## Deploy to Google Cloud Run

The image is built for Cloud Run: it reads `$PORT`, runs Streamlit headless, and
turns off Streamlit's own CORS/XSRF since the platform fronts HTTPS and the
websocket.

```bash
# From the project root, build and deploy in one step (Cloud Build does the build)
gcloud run deploy lead-research-agent \
  --source . \
  --region europe-west2 \
  --allow-unauthenticated \
  --set-env-vars LLM_PROVIDER=openai
```

Set your secrets as Cloud Run environment variables (or, better, via Secret
Manager) rather than baking them into the image. At a minimum you need
`OPENAI_API_KEY`; add `TAVILY_API_KEY` for live web research. The `.dockerignore`
keeps `.env`, the virtualenv, and caches out of the build context.

If you make the service public, treat it as a personal/internal tool: anyone with
the URL can spend your API quota.

---

## Tests

A pytest suite lives in `tests/`. It is fully offline: the LLM and Tavily are
mocked or driven down no-network code paths, so no API keys and no live calls are
needed.

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

It covers the export table shape and columns, `Settings.validate()` branches,
search context formatting, the manual-list and mocked discovery paths, and the
schema defaults/bounds.

---

## Make it sound like you

Open **`profile.yaml`** and edit:

- `name` - who the message is from
- `one_line_offer` - what you do, in plain words
- `demo_links` - links the draft may include (at most one per message)
- `tone_notes` - how you write (this genuinely steers the output)
- `credibility` - a light proof line it can reference
- `sign_off` - how you sign off

No restart needed for content edits - just reload the Streamlit page.

---

## Switch to Azure OpenAI

In `.env`:

```ini
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

Everything else stays the same - the rest of the code is provider-agnostic.

---

## Scope

**In v1:** ICP input, company discovery (or a manual company list), per-company
research, pain-point hypotheses, likely contact, personalised draft, editable
results table, CSV export.

**Out of scope for v1 (by design):**

- Sending email - drafts only, always
- CRM integration
- Paid contact-enrichment APIs - v1 infers a likely contact from free web search

It runs locally with `streamlit run app.py`, and it is containerised: the
`Dockerfile` produces a Cloud Run-ready image (see [Deploy to Google Cloud
Run](#deploy-to-google-cloud-run)).

---

## Roadmap

The v1 code leaves clean seams for the obvious next steps:

- **Verified contacts.** `agent/enrichment.py::enrich_contact` is an intentional
  extension seam. It returns `None` today, so the contact node falls back to
  web-search inference. Implement it against a provider like Apollo, Hunter, or
  Clearbit (read its key from `agent/config.py::Settings`) and the rest of the
  pipeline picks up the verified `Contact` with no further changes.
- **More providers.** Provider selection already lives in one place
  (`agent/llm.py`), so adding another backend is a localised change.
- **Sending stays off the table** - by design, this tool drafts and never sends.

---

## Notes on the contact step

In v1 a contact is a *hypothesis*. The agent uses web search to name a real
decision-maker where it can (marked `found` / `likely`); otherwise it suggests the
best target role like "Head of Marketing" (marked `guess`) and never invents a
specific person. Treat anything below `found` as a starting point to verify.
