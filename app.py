"""AI Lead Research Agent - Streamlit UI.

Enter an Ideal Client Profile, run the agent, review and edit the drafts in a
table, then export to CSV. This tool produces DRAFTS ONLY. It never sends.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st

from agent.config import load_profile, load_sample_icp, load_settings
from agent.export import dataframe_to_csv_bytes, results_to_dataframe
from agent.graph import discover_companies, research_company
from agent.schemas import ICP
from theme import (
    inject_theme,
    render_demo,
    render_footer,
    render_group,
    render_header,
    render_step,
    render_stepper,
)

# A small pool: each company's pipeline is independent, but we keep the count low
# to stay polite to the LLM and search APIs (and to avoid rate limits).
MAX_WORKERS = 4

st.set_page_config(page_title="AI Lead Research Agent", layout="wide")
inject_theme()

settings = load_settings()
profile = load_profile()
sample = load_sample_icp()


# --- Header -----------------------------------------------------------------

render_header()
render_demo()

# Only surface setup problems (e.g. a missing key) - stay quiet when all is well.
for problem in settings.validate():
    st.warning(problem)


# --- ICP form ---------------------------------------------------------------

render_stepper(1)

with st.form("icp_form"):
    render_step(
        "Describe your ideal client",
        "Tell the agent who you want to reach and what you're offering. It does the rest.",
    )

    # WHO you target - the matching criteria, two tidy columns of equal width.
    render_group("Who you target")
    col1, col2 = st.columns(2)
    with col1:
        industry = st.text_input(
            "Industry", value=sample.get("industry", ""),
            placeholder="e.g. recruitment agencies",
        )
        location = st.text_input(
            "Location", value=sample.get("location", ""),
            placeholder="e.g. London, UK",
        )
    with col2:
        company_size = st.text_input(
            "Company size", value=sample.get("company_size", ""),
            placeholder="e.g. 10 to 50 employees",
        )
        keywords = st.text_input(
            "Keywords (optional)", value=sample.get("keywords", ""),
            placeholder="comma separated extra signals",
        )

    # WHAT you offer - the single most important input, so give it room.
    render_group("What you offer", "the most important field")
    offer = st.text_area(
        "Your offer",
        value=sample.get("offer", ""),
        height=120,
        placeholder="In a sentence or two: what you do and the result it gets them.",
        help="Every draft is built around this, so be specific about the outcome.",
    )

    # HOW MANY - a single clear control.
    render_group("How many companies")
    num_companies = st.slider(
        "Number of companies to research", 1, 20, int(sample.get("num_companies", 5))
    )

    # Power-user path, hidden by default so the form stays uncluttered.
    with st.expander("Advanced - target specific companies instead"):
        manual_raw = st.text_area(
            "Companies to research (one per line)",
            value="\n".join(sample.get("manual_companies", []) or []),
            height=90,
            help="Listing companies here skips discovery and researches exactly these.",
        )

    submitted = st.form_submit_button("Run research", type="primary")


# --- Run --------------------------------------------------------------------

if submitted:
    if not offer.strip():
        st.error("Add your offer first - the drafts are built around it.")
        st.stop()
    if settings.provider == "openai" and not settings.openai_api_key:
        st.error("OPENAI_API_KEY is not set. Add it to your .env and reload.")
        st.stop()

    icp = ICP(
        industry=industry,
        company_size=company_size,
        location=location,
        keywords=keywords,
        offer=offer,
        num_companies=num_companies,
        manual_companies=[line.strip() for line in manual_raw.splitlines() if line.strip()],
    )

    with st.status("Finding matching companies...", expanded=True) as status:
        companies = discover_companies(icp, settings)
        if not companies:
            status.update(label="No companies found", state="error")
            st.warning("No companies came back. Try broadening the ICP or listing companies manually.")
            st.stop()
        total = len(companies)
        st.write(f"Found {total} companies. Researching {min(MAX_WORKERS, total)} at a time...")

        # Research companies concurrently. Each pipeline is independent, so we run
        # them in a small thread pool. We pass graph=None so every worker compiles
        # its own chain and builds its own LLM/search clients - no shared mutable
        # state crosses threads. Results are reassembled in the original order.
        results: list = [None] * total
        progress = st.progress(0.0)
        done = 0

        def _research(company):
            return research_company(company, icp, profile, settings, graph=None)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(_research, c): i for i, c in enumerate(companies)}
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()
                done += 1
                st.write(f"{done}/{total}  {companies[idx].name}")
                progress.progress(done / total)

        failed = sum(1 for r in results if r.error)
        researched = total - failed
        if failed == total:
            status.update(label=f"All {total} companies failed", state="error")
        elif failed:
            status.update(
                label=f"Done - {researched} of {total} researched, {failed} failed",
                state="complete",
            )
        else:
            status.update(label=f"Done - {total} leads researched", state="complete")

    # Honest post-run summary, outside the status box so it stays visible.
    if failed == total:
        st.error(
            f"All {total} companies failed to research. This usually means a bad or missing "
            f"API key, or a rate limit. Check the Notes column for the error, fix the cause, "
            f"and run again."
        )
    elif failed:
        st.warning(
            f"{researched} of {total} companies researched. {failed} failed - see the Notes "
            f"column (flagged below) for what went wrong."
        )
    else:
        st.success(f"{total} of {total} companies researched.")

    st.session_state["results_df"] = results_to_dataframe(results)


# --- Results ----------------------------------------------------------------

if "results_df" in st.session_state:
    render_stepper(2)
    render_step(
        "Review and edit the drafts",
        "Edit any cell, especially the drafts. Your edits are included in the CSV export.",
    )

    # Sort strongest fit first so the best leads sit at the top of the table.
    # Failed rows have no real fit score, so they fall to the bottom naturally.
    display_df = (
        st.session_state["results_df"]
        .sort_values("Fit", ascending=False, kind="stable")
        .reset_index(drop=True)
    )

    # Visually flag any row that failed with a leading status marker. st.data_editor
    # does not support pandas Styler row-tinting, so we use an explicit column - it
    # survives editing and CSV export, and makes failures impossible to miss.
    display_df.insert(
        0,
        "Status",
        ["Failed" if str(n).strip() else "OK" for n in display_df["Notes"]],
    )

    edited = st.data_editor(
        display_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Status": st.column_config.TextColumn(
                width="small", help="Failed rows could not be researched - see Notes.", disabled=True
            ),
            "What they do": st.column_config.TextColumn(width="medium"),
            "Pain points": st.column_config.TextColumn(width="medium"),
            "Draft": st.column_config.TextColumn(width="large"),
        },
        key="results_editor",
    )

    st.download_button(
        "Download CSV",
        data=dataframe_to_csv_bytes(edited),
        file_name="leads.csv",
        mime="text/csv",
    )


render_footer()
