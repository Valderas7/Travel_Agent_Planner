from langchain_openai import ChatOpenAI
from core.config import settings

# Se instancia el modelo de lenguaje local de LM Studio
llm = ChatOpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key="lm-studio",
    model=settings.LLM_MODEL,
    temperature=0,
)