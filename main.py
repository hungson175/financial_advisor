import asyncio

from backend.report_type import DetailedReport
# from gpt_researcher.report_type import DetailedReport


from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from fad.fad_researcher import Researcher

# QUERY = "Research on FnB  market in Vietnam"
QUERY = "Systematic method to compare impact of a value added services on a Chinese cashless payment platform"
# QUERY = "Cashless payment: the most impactful value added services for payment apps, lessons learned from Chinese tech-giants"

load_dotenv()


async def generate_report(query, report_type="research_report", report_source="web_search", websocket=None):
    detailed_report = DetailedReport(
        query=query,
        report_type=report_type,
        report_source=report_source,
        source_urls=[],  # You can provide initial source URLs if available
        config_path=None,
        # tone=tone,
        websocket=websocket,
        subtopics=[],  # You can provide predefined subtopics if desired
        # headers={}  # Add any necessary HTTP headers
    )

    final_report = await detailed_report.run()
    return final_report


def get_report_in_vietnamese(query: str, report_type: str) -> dict:
    report = asyncio.run(generate_report(query, report_type))
    llm = ChatOpenAI(model_name="gpt-4o")
    prompt_template = ChatPromptTemplate.from_messages([
        ("system",
         """You are very skillful translator. 
         Your goal is to translate the following report into Vietnamese - make sure to keep the meaning,tone, and references of the report intact."""),
        # this will be auto generate from query
        ("human", "{report}")
    ])
    translator = prompt_template | llm
    result = translator.invoke(input={"report": report})
    return {
        "en": report,
        "vi": result.content
    }


def generate_file_name(query: str):
    system_prompt = """Given the query, your task is to generate a file name for the report using 3-5 words.
    Expected output: The output file name WITHOUT extension.

    Examples:
        query: "The Impact of Substances on Creativity and Innovation Throughout History"
        output: "impact_substances_creativity_innovation_history"

        query: "How does the brain process information?"
        output: "brain_process_information"

        query: "What is the impact of AI on the job market?"
        output: "impact_ai_job_market"
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{query}")
    ])

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.15)
    chain = prompt | llm
    return chain.invoke({"query": query})


def write_long_report(query: str = QUERY):
    english_file_name, vietnamese_file_name = gen_report_file_names(query)
    report_type = "research_report"
    report = get_report_in_vietnamese(query, report_type)
    # save the report to files
    with open(english_file_name, "w") as f:
        f.write(report["en"])
    with open(vietnamese_file_name, "w") as f:
        f.write(report["vi"])
    print(f"Report saved to {english_file_name} and {vietnamese_file_name}")


def gen_report_file_names(query: str):
    file_prefix = generate_file_name(query)
    english_file_name = file_prefix.content + "_en.md"
    vietnamese_file_name = file_prefix.content + "_vi.md"
    return english_file_name, vietnamese_file_name


def write_short_report(query: str = QUERY):
    researcher = Researcher(query=query)
    rs = asyncio.run(researcher.research())
    # write report to markdown file: report_genAI_on_SE.md
    report = rs["report"]
    en_fn, _ = gen_report_file_names(QUERY)
    with open(en_fn, 'w') as f:
        f.write(report)
    all_docs = []
    summaries = rs["summaries"]
    for summ in summaries:
        docs = summ["summaries"]
        all_docs.extend(docs)
    # Researcher.save_to_vector_db(all_docs)


def main():
    # query = "The Impact of AI on Software Outsourcing Companies: Strategies for Adaptation"
    # query = "Adapting to the Impact of Generative AI: How HR Managers Can Stay Relevant ?"
    # get user input to write long/short report  ?
    # ls_type = input("Write long or short report ? (l: long/s: short): ")
    # query = input("Your research topic: ")
    ls_type = 's'
    if ls_type.lower() == 's' or ls_type.lower() == 'short':
        write_short_report(query=QUERY)
    else:
        write_long_report(query=QUERY)


if __name__ == "__main__":
    main()
