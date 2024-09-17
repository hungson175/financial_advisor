# import logging
import asyncio
import datetime
import os

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from fad.generators.generate_agent import choose_agent, GeneratedAgent
from fad.generators.generate_sub_queries import generate_sub_queries, SubQueries
from fad.tools import websearch_tools, writer
from fad.tools.compressors import ContextCompressor
from fad.tools.scrapers.scraper import Scraper

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REPORT_FILE = 'report.md'

MAX_SUB_QUERIES = 3
MAX_SEARCH_RESULTS = 8


# logging.basicConfig(level=logging.INFO)

class Logger:
    def info(self, str):
        print(str)


class Researcher:
    def __init__(self, query: str):
        load_dotenv()
        self.query = query

    @staticmethod
    async def produce_sub_context(sub_query: str, scraped_contents: dict, embeddings):
        compressor = ContextCompressor(scraped_contents[sub_query], embeddings)
        rs = await compressor.async_get_context(sub_query)
        return rs

    @staticmethod
    async def produce_sub_summaries(sub_query: str, scraped_contents: dict, embeddings):
        compressor = ContextCompressor(scraped_contents[sub_query], embeddings)
        docs = await compressor.async_get_relevant_docs(sub_query)
        return {"query": sub_query, "summaries": docs}

    async def research(self):
        """
        This program takes an input as a question/topic, then:
        1. Generate an "expert" (called server) for that topic
        2. Using the expert to generate several search sub-queries for that topic
        3. Retrieve url,description for each search query (including the original query)
        4. For each search sub-query:
            4.1 Scrape the content of the first top_n urls
            4.2 Return the content of the first top_n urls: [(url,list(content) )]
        """
        load_dotenv()
        logging = Logger()

        logging.info('Choose an agent for the query ...')
        agent_data: GeneratedAgent = choose_agent(self.query)  # server, agent_role_prompt
        logging.info(f"Agent: \n\tRole = {agent_data.server}  \n\tDescription: {agent_data.agent_role_prompt}...")
        sub_queries: SubQueries = generate_sub_queries(
            query=self.query,
            agent_role=agent_data.agent_role_prompt,
            max_queries=MAX_SUB_QUERIES)
        # print(sub_queries)
        sub_queries.list.append(self.query)  # add the original query
        logging.info(f"Research based on sub-queries: {sub_queries.list} ...")
        search_results = websearch_tools.search_queries(sub_queries.list, max_results=MAX_SEARCH_RESULTS)
        scraped_contents = {}
        logging.info("Scraping contents...")
        for sub_query in sub_queries.list:
            logging.info(f"\tScraping for sub-query: {sub_query} ...")
            docs = search_results[sub_query]
            urls = [doc['url'] for doc in docs]
            scraped_contents[sub_query] = Scraper.scrape_multiple_urls(urls)  # list of content, not only 1 !
        # Now split the content for each sub-query to save to database
        OPENAI_EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL, check_embedding_ctx_length=False)

        # split the scraping content for each sub-query to small chunks
        summaries = await asyncio.gather(
            *[
                Researcher.produce_sub_summaries(sub_query, scraped_contents, embeddings)
                for sub_query in sub_queries.list
            ])
        sub_contexts = []
        for summ in summaries:
            # sub_query = summ["query"]
            docs = summ["summaries"]
            sub_contexts.append(ContextCompressor.pretty_print_docs(docs, MAX_SEARCH_RESULTS))

        logging.info("Done researching context !")
        logging.info("Start writing ...")
        report = await writer.write_report(
            query=self.query,
            context=sub_contexts,
            agent_role_prompt=agent_data.agent_role_prompt)
        logging.info(f"======\n Final report:\n {report.content}\nUsage_metadata: {report.usage_metadata}\n======")

        return {
            "summaries": summaries,
            "report": report.content
        }

    @classmethod
    def add_tag_to_docs(cls, documents, tags: dict):
        if tags is None:
            return documents
        tagged_docs = []
        for doc in documents:
            tdoc = doc
            # add tag to doc.metadata
            for k, v in tags.items():
                tdoc.metadata[k] = v
            tagged_docs.append(tdoc)
        return tagged_docs

    @classmethod
    def save_to_vector_db(cls, documents, tags: dict = None):
        tagged_docs = Researcher.add_tag_to_docs(documents, tags)
        Chroma.from_documents(
            documents=tagged_docs,
            collection_name="rag-chroma",
            embedding=OpenAIEmbeddings(),
            persist_directory="./.chroma",
        )


if __name__ == "__main__":
    researcher = Researcher(query="GPU as a service market share")
    rs = asyncio.run(researcher.research())

    # write report to markdown file: report_genAI_on_SE.md
    report = rs["report"]
    # get current formatted date and time for the report file name
    date_time = datetime.datetime.now()
    date_time_formatted = date_time.strftime("%Y-%m-%d_%H-%M-%S")
    report_file_name = f"../doc_reports/report + {date_time_formatted}.md"
    with open(report_file_name, 'w') as f:
        f.write(report)

    all_docs = []
    summaries = rs["summaries"]
    for summ in summaries:
        docs = summ["summaries"]
        all_docs.extend(docs)
    tag = "FPT"

    # Researcher.save_to_vector_db(tags={"ticker": "FPT"}, documents=all_docs)
