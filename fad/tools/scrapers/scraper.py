import asyncio
import logging
from abc import abstractmethod
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.retrievers import ArxivRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from pydantic.v1 import BaseModel


class Scraper:
    def __init__(self, url: str, description: str = None):
        self.url = url
        self.description = description

    @abstractmethod
    def scrape(self) -> str:
        pass

    @staticmethod
    def scrape_multiple_urls(urls: List[str]):

        with ThreadPoolExecutor(max_workers=16) as executor:
            scraped_contents = executor.map(Scraper.scrape_single_url, urls)
        final_contents = [content for content in scraped_contents if
                          content["raw_content"] is not None and len(content["raw_content"]) > 128]
        # final_contents = []
        # for url in urls:
        #     scraped_contents = Scraper.scrape_single_url(url)
        #     final_contents.append(scraped_contents)

        return final_contents

    @staticmethod
    def scrape_single_url(url: str, description: str = None):
        try:
            scraper = Scraper.create_scraper(url, description)
            content = scraper.scrape()
            return {
                "url": url,
                "description": description,
                "raw_content": content,
            }
        except Exception as e:
            logging.error(f"Error while scraping site {url} :\n {str(e)}")
            return {
                "url": url,
                "description": description,
                "raw_content": None,
            }

    @staticmethod
    def create_scraper(url: str, description):
        mapping_scraper = {
            "pdf": PDFScraper,
            "arxiv": ArxivScraper,
            "rest": WebsiteScraper,
        }

        stype = "rest"

        if url.endswith(".pdf"):
            stype = "pdf"
        elif "arxiv.org" in url:
            stype = "arxiv"

        return mapping_scraper[stype](url, description)


class ArxivScraper(Scraper):
    def scrape(self) -> str:
        query = self.url.split("/")[-1]
        retriever = ArxivRetriever(load_max_docs=2, doc_content_chars_max=None)
        docs = retriever.get_relevant_documents(query=query)
        return docs[0].page_content


class PDFScraper(Scraper):

    def scrape(self) -> str:
        loader = PyMuPDFLoader(self.url)
        doc = loader.load()
        return str(doc)


class SiteData(BaseModel):
    title: str
    description: str
    content: str


class WebsiteScraper(Scraper):

    def __scraping_site(self):
        from langchain_community.document_loaders import WebBaseLoader
        scraper = WebBaseLoader(self.url)
        scraper.requests_kwargs = {"verify": False}
        docs = scraper.load()
        return docs

    def __scraper_compressor(self, doc):
        # compress the content by using gpt-4o to remove unrelevant information
        llm = ChatOpenAI(model="gpt-4o-mini")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You a helpful assistant, you will read the content returned by a web scraper, "
                           "and remove the information that is not relevant to the page content (header, footer, sidebar, navigation, other links, etc.) using the title and description of the page.\n"
                           "Expected output:\n"
                           "A string, the content of the page after removing the unrelevant information - nothing less, nothing more. No summary, no introduction, no comments, etc."),
                ("user",
                 "Title: {title}\n===\nDescription: {description}\n===\n Page content: \n```\n{page_content}\n```"),
            ]
        )
        chain = prompt | llm
        result = chain.invoke({"title": doc.metadata["title"],
                               "description": doc.metadata["description"],
                               "page_content": doc.page_content})
        return result.content

    def scrape(self) -> str:
        docs = self.__scraping_site()
        content = ""
        for doc in docs:
            page_content = doc.page_content
            import re
            page_content = re.sub(r"\n+", "\n", page_content)
            content += page_content
        return content
        # site_data_list = []
        # for doc in docs:
        #     content = doc.page_content if not compress else self.__scraper_compressor(doc)
        #     # remove multiple newlines (even more than 2) from the content with 2 \n
        #     content = re.sub(r"\n+", "\n", content)
        #     site_data = SiteData(title=doc.metadata["title"],
        #                         description=doc.metadata["description"],
        #                         content=content)
        #     site_data_list.append(site_data)
        # return site_data_list
