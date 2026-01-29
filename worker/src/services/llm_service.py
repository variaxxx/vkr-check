from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.core.config import Settings


class LLMService:
    def __init__(self, config: Settings):
        self.llm = ChatOpenAI(
            api_key="empty",
            base_url=f"http://{config.API_IP}:{config.API_PORT}/v1",
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
        )

    def get_llm(self):
        """Возвращает инстанс LLM"""
        return self.llm

    def invoke_vision(self, content: list) -> str:
        """Выполняет vision запрос к модели"""
        response = self.llm.invoke([HumanMessage(content=content)])
        return response.content
