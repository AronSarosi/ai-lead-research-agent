"""Plain-English Privacy Notice and Terms of Use shown via the app footer.

Kept honest and specific on purpose: this is a free demonstration of a lead-research
agent. It researches public companies via web search, drafts outreach you review, and
it NEVER sends anything on your behalf. This is a demo, not professional advice, but it
accurately describes how the app actually handles data.
"""

# Shown in the policies below. Change freely.
CONTACT_EMAIL = "aron.sarosi13@gmail.com"

PRIVACY_MD = f"""
**Last updated: June 2026**

This is a **free demonstration application** built to showcase an AI lead-research agent.
Please read how your data is handled before using it.

**What we process**
- **The brief you type** (your ideal client profile and the offer you're pitching, plus any
  companies you list manually). Used only to research companies and draft outreach during
  your session.
- **Minimal technical metadata** (basic request information), used solely to keep the demo
  running and apply fair-use limits.

**How your data is used**
- Your brief is sent to a **web search provider (Tavily)** to find and research matching
  companies, and to a **language-model provider (OpenAI, or Azure OpenAI when configured)**
  to summarise what each company does and to write the outreach drafts.
- The agent researches **publicly available information** about companies via web search. It
  infers a likely contact person from public sources; **it does not verify that person and
  does not enrich, buy, or look up private contact data.**
- The providers process this under their own API data policies. OpenAI does **not** train its
  models on data submitted via the API and retains it only briefly for abuse monitoring. When
  configured for **Azure OpenAI**, this processing stays inside a private Azure tenant.
- When tracing is enabled, an **observability tool (Langfuse)** records the model calls so the
  system can be debugged and quality-checked. It is not used for advertising or profiling.

**The agent never sends**
- This tool produces **drafts only**. It does not send emails, messages, or connection
  requests, and it has no access to your mailbox or accounts. Anything that goes out, goes out
  because you copied it and sent it yourself.

**Retention**
- Your brief and the results are held only for your session and the CSV you download. On the
  hosted demo the underlying instance is ephemeral and its storage is wiped when it recycles.
- We do not build user profiles, and we do not sell or share your data with anyone other than
  the providers above (and error/observability tooling, when enabled, for debugging).

**Your responsibilities**
- Because this is a public demo, **please do not enter personal, confidential, or otherwise
  sensitive data** in the brief.
- You are responsible for how you use the drafts and contact details it produces, including
  complying with anti-spam and data-protection rules (such as UK GDPR and PECR) when you send.

Questions about privacy: {CONTACT_EMAIL}
"""

TERMS_MD = f"""
**Last updated: June 2026**

By using this free demonstration application ("the Demo"), you agree to the following.

**The Demo is provided "as is"**
- It is for **evaluation and demonstration only**, without warranties of any kind (including
  accuracy, fitness for a particular purpose, or availability).
- It researches companies from public web sources and uses AI to summarise and draft. **The
  research, the inferred contact, and the drafts may contain errors or be out of date.** Treat
  every draft as a starting point, verify any contact details, and personalise each message
  before you send it. **This is not legal, marketing, or professional advice.**

**It drafts, it does not send**
- The Demo produces **drafts only and never sends anything on your behalf.** You decide what,
  if anything, to send, and you are responsible for that outreach - including complying with
  anti-spam and data-protection law (such as UK GDPR and PECR).

**Fair use**
- To keep the Demo free and available, please don't try to overload the service, scrape it,
  or use it for unlawful purposes, harassment, or bulk unsolicited messaging. Want more, or a
  version built for your team? Get in touch.

**Your content**
- You keep all rights to the brief you enter, and you're responsible for having the right to
  use it and for ensuring it contains no sensitive or personal data (see the Privacy Notice).
- The Demo's code and design remain the property of its author.

**Limitation of liability**
- To the maximum extent permitted by law, the author is not liable for any damages arising
  from your use of the Demo, including any loss arising from reliance on its output or from
  outreach you choose to send.

Contact: {CONTACT_EMAIL}
"""
