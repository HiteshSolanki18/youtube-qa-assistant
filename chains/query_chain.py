from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from utils.prompt_templates import get_prompt_template
from dotenv import load_dotenv

load_dotenv()

def context_processor(documents):
    return "\n".join([doc.page_content for doc in documents])

def build_chain(retriever):
    llm = GoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_tokens=1000)
    template = get_prompt_template()
    parser = StrOutputParser()

    parallel_chain = RunnableParallel({
        "context": retriever | RunnableLambda(context_processor),
        "question": RunnablePassthrough(),
    })

    return parallel_chain | template | llm | parser