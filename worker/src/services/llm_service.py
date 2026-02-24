import asyncio
from typing import List, Dict, Union

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.core.config import Settings

class LLMService:
    def __init__(self, config: Settings):
        self.llm = ChatOpenAI(
            api_key="empty",
            base_url=f"http://{config.API_IP}:{config.API_PORT}/v1",
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS
        )

    async def llm_text_request(self, prompt: ChatPromptTemplate, **kwargs) -> str:
        """Выполняет асинхронный текстовый запрос к модели"""
        template_dict = kwargs.pop("template_dict", None)
        if template_dict:
            for i in template_dict:
                template_dict[i] = str(template_dict[i]).replace("{", " ").replace("}", " ")
        
        chain = prompt | self.llm.bind(**kwargs) | StrOutputParser()

        try:
            if template_dict:
                response = await chain.ainvoke(template_dict)
            else:
                response = await chain.ainvoke({})
            return response
        except Exception as e:
            print(f"Ошибка асинхронной генерации: {str(e)}")
            return ""

    async def llm_vision_request(self, messages: list, **kwargs) -> str:
        """Выполняет асинхронный vision запрос к модели"""
        try:
            response = await self.llm.ainvoke(messages, **kwargs)
            return response.content
        except Exception as e:
            print(f"Ошибка асинхронного vision запроса: {str(e)}")
            return ""
    
    @staticmethod
    def create_text_prompt(user_text: str, system_prompt: str = None) -> ChatPromptTemplate:
        """Создает промпт для текстового запроса (синхронный метод)"""
        messages = []
        user_prompt = f"{user_text}"

        if system_prompt:
            messages.append(("system", system_prompt))
        
        messages.append(("user", user_prompt))
        return ChatPromptTemplate.from_messages(messages)
    
    @staticmethod
    def create_vision_prompt(user_text: str, pages: List[str], system_prompt: str = None) -> List[Union[SystemMessage, HumanMessage]]:
        """Создает промпт для vision запроса (синхронный метод)"""
        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        human_content = [
            {
                "type": "text", 
                "text": f"{user_text}"
            }
        ]

        for b64 in pages:
            human_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })
        
        messages.append(HumanMessage(content=human_content))
        return messages