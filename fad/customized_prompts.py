from datetime import date


def auto_translator_instructions():
    return """
    This task involves translating a comprehensive research report from English to Vietnamese while adhering to specific translation standards. The agent must ensure that specific field-related nouns remain untranslated and in English. General terms can be translated as needed. The agent must also maintain the structural integrity of the document and preserve all references (links).
    Role
    The translator agent should be created based on the specific research topic, ensuring the translation respects domain-specific terminology. Each agent is tailored for its field and tasked with translating content while preserving accuracy and meaning.

    Examples:
    task: "Generative AI impacts on Software Development"
    response:
    {{
        "server": "🧠 AI Translator Agent",
        "agent_role_prompt": "You are an expert AI researcher and translator. Your objective is to translate technical and research-heavy content related to artificial intelligence from English to Vietnamese. Keep specific AI-related nouns such as 'neural network,' 'CNN,' 'transformer,' and 'GPT' in English. Maintain the original report structure and keep all references (links) intact."
    }}
    task: "Cryotherapy: the most effective method for muscle recovery"
    response:
    {{
        "server": "💪 Sports Science Translator Agent",
        "agent_role_prompt": "You are a sports science translator with expertise in translating medical and research articles. Translate content related to cryotherapy and muscle recovery from English to Vietnamese. Keep specific medical and sports science terms such as 'Cryotherapy,' 'Photobiomodulation,' and 'Hyperbaric Oxygen Therapy' in English. Maintain the original report structure and keep all references (links) intact."
    }}
    task: "Sustainability efforts in modern agriculture"
    response:
    {{
        "server": "🌱 Environmental Translator Agent",
        "agent_role_prompt": "You are an AI-driven environmental science translator. Your task is to translate reports on sustainability and agriculture from English to Vietnamese. Keep specific scientific nouns such as 'photosynthesis,' 'hydroponics,' and 'permaculture' in English. Maintain the original report structure and keep all references (links) intact."
    }}
    """


def auto_agent_instructions():
    return """
This task involves researching a given topic, regardless of its complexity or the availability of a definitive answer. The research is conducted by a specific server, defined by its type and role, with each server requiring distinct instructions.
Agent
The server is determined by the field of the topic and the specific name of the server that could be utilized to research the topic provided. Agents are categorized by their area of expertise, and each server type is associated with a corresponding emoji.

examples:
task: "should I invest in apple stocks?"
response: 
{{
    "server": "💰 Finance Agent",
    "agent_role_prompt: "You are a seasoned finance analyst AI assistant. Your primary goal is to compose comprehensive, astute, impartial, and methodically arranged financial reports based on provided data and trends."
}}
task: "could reselling sneakers become profitable?"
response: 
{{ 
    "server":  "📈 Business Analyst Agent",
    "agent_role_prompt": "You are an experienced AI business analyst assistant. Your main objective is to produce comprehensive, insightful, impartial, and systematically structured business reports based on provided business data, market trends, and strategic analysis."
}}
task: "what are the most interesting sites in Tel Aviv?"
response:
{{
    "server:  "🌍 Travel Agent",
    "agent_role_prompt": "You are a world-travelled AI tour guide assistant. Your main purpose is to draft engaging, insightful, unbiased, and well-structured travel reports on given locations, including history, attractions, and cultural insights."
}}
"""


def sub_queries_instruction(
        question: str,
        max_queries: int = 3
):
    return (
        f'Write {max_queries} google search queries to search online that form an objective opinion from the following task: "{question}"'
        f'You must respond with a list of strings in the following format: ["query 1", "query 2", "query 3"].\n'
        f"The response should contain ONLY the list."
    )


def escape_curly_braces(input):
    if isinstance(input, list):
        return [escape_curly_braces(i) for i in input]
    if isinstance(input, dict):
        return {k: escape_curly_braces(v) for k, v in input.items()}
    if isinstance(input, str):
        return input.replace("{", "{{").replace("}", "}}")
    raise ValueError(f"Unsupported type: {type(input)}")


def generate_report_prompt(
        question: str,
        context,
        report_format="apa",
        total_words=1000,
        tone=None,
):
    reference_prompt = f"""
    You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.
    Every url should be hyperlinked: [url website](url)
    Additionally, you MUST include hyperlinks to the relevant URLs wherever they are referenced in the report: 

    eg: Author, A. A. (Year, Month Date). Title of web page. Website Name. [url website](url)
    """

    tone_prompt = f"Write the report in a {tone.value} tone." if tone else ""
    return f"""
    Information: "{escape_curly_braces(context)}"
    ---
    Using the above information, answer the following query or task: "{question}" in a detailed report --
    The report should focus on the answer to the query, should be well structured, informative, 
    in-depth, and comprehensive, with facts and numbers if available and a minimum of {total_words} words.
    You should strive to write the report as long as you can using all relevant and necessary information provided.

    Please follow all of the following guidelines in your report:
    - You MUST determine your own concrete and valid opinion based on the given information. Do NOT defer to general and meaningless conclusions.
    - You MUST write the report with markdown syntax and {report_format} format.
    - Use an unbiased and journalistic tone.
    - Use in-text citation references in {report_format} format and make it with markdown hyperlink placed at the end of the sentence or paragraph that references them like this: ([in-text citation](url)).
    - Don't forget to add a reference list at the end of the report in {report_format} format and full url links without hyperlinks.
    - {reference_prompt}
    - {tone_prompt}

    Please do your best, this is very important to my career.
    Assume that the current date is {date.today()}.
    """
