from typing import Any, Type, Optional
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from .config import Settings


def build_llm(settings: Settings) -> Optional[ChatOpenAI]:
    if not settings.openai_api_key:
        return None
    base_url = settings.openai_base_url or None
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=base_url,
        temperature=0.2,
    )


def llm_structured_output(
    llm: Optional[ChatOpenAI],
    output_model: Type[BaseModel],
    system_prompt: str,
    user_prompt: str,
) -> BaseModel:
    parser = PydanticOutputParser(pydantic_object=output_model)
    if llm is None:
        data = {}
        try:
            data = json.loads("{}")
        except Exception:
            data = {}
        return output_model.model_validate(data)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{input}\n{format_instructions}"),
        ]
    )
    chain = prompt | llm | parser
    return chain.invoke({"input": user_prompt, "format_instructions": parser.get_format_instructions()})
