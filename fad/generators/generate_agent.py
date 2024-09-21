from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from fad import fad_config
from fad.customized_prompts import auto_agent_instructions, auto_translator_instructions


class GeneratedAgent(BaseModel):
    server: str = Field(description="The server that conducts the research.")
    agent_role_prompt: str = Field(description="The role of the server in the research.")


def choose_agent(query: str) -> GeneratedAgent:
    system_prompt = auto_agent_instructions()
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{query}"),
        ]
    )
    llm = ChatOpenAI(model=fad_config.SMART_LLM_MODEL, temperature=0.15)
    structured_llm = llm.with_structured_output(GeneratedAgent)

    chain: RunnableSequence = prompt_template | structured_llm
    return chain.invoke({"query": query})


def choose_translation_agent(research_topic: str) -> GeneratedAgent:
    system_prompt = auto_translator_instructions()
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{query}"),
        ]
    )
    llm = ChatOpenAI(model=fad_config.SMART_LLM_MODEL, temperature=0.15)
    structured_llm = llm.with_structured_output(GeneratedAgent)

    chain: RunnableSequence = prompt_template | structured_llm
    return chain.invoke({"query": research_topic})


if __name__ == "__main__":
    print(choose_agent("should I invest in FPT stock?"))
