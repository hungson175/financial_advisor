from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from fad import customized_prompts, fad_config


async def write_report(
        query: str,
        context,
        agent_role_prompt: str,
):
    generation_prompt = customized_prompts.generate_report_prompt(
        question=query,
        context=context,
        total_words=1024,
    )
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", agent_role_prompt),
        ("user", generation_prompt),
    ])
    llm = ChatOpenAI(model_name=fad_config.SMART_LLM_MODEL, temperature=0.35)
    chain = prompt_template | llm
    return chain.invoke({})
