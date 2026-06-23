"""AI Lead Research Agent - core package.

Modules:
  config      load .env + profile.yaml, provider settings
  schemas     Pydantic models for the agent's structured data
  llm         chat-model factory (OpenAI / Azure) + Tavily client + tracing
  search      thin Tavily search wrappers
  enrichment  clean stub for a future paid contact-enrichment API
  graph       the LangGraph per-company pipeline
  export      results -> CSV helper
"""
