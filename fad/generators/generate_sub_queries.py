from typing import List

from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from fad import fad_config
from fad.customized_prompts import sub_queries_instruction


class SubQueries(BaseModel):
    list: List[str] = Field(description="The sub queries generated from the user query.")


def generate_sub_queries(query: str, agent_role: str, max_queries: int = 3) -> SubQueries:
    system_prompt = sub_queries_instruction(query, max_queries)
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{query}"),
        ]
    )
    llm = ChatOpenAI(model=fad_config.SMART_LLM_MODEL, temperature=0.15)
    structured_llm = llm.with_structured_output(SubQueries)

    chain: RunnableSequence = prompt_template | structured_llm
    return chain.invoke({"query": query})
