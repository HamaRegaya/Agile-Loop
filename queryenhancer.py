from helper import *
import yaml
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

config = yaml.load(open("yaml/config.yaml", "r"), Loader=yaml.FullLoader)

query_enhancer = AzureChatOpenAI(
    azure_deployment=config['azure_deployment'],
    azure_endpoint=config['azure_endpoint'],
    api_key=config['api_key'],
    api_version=config['api_version'],
    temperature=0.8,
    max_tokens=150,
    top_p=0.1
)

query = input("Enter your question: ")

query_to_enhance = f"you are an OPENAPI expert and you will enhance the original_query to make it more detailed and suitable for an LLM to understand the tasks clearly. This is the original_query: {query}"


message = HumanMessage(
    content=query_to_enhance
)
enhanced_query = query_enhancer.invoke([message])
print(enhanced_query.content)