from helper import *
import mysql.connector
import random
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from langchain_core.prompts import ChatPromptTemplate
# from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
# from langchain.chat_models import AzureChatOpenAI
import base64

logger = logging.getLogger()


def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.geometry("400x250")

    config = yaml.load(open("yaml/config.yaml", "r"), Loader=yaml.FullLoader)

    logging.basicConfig(
        format="%(message)s",
        handlers=[logging.StreamHandler(ColorPrint())],
    )
    logger.setLevel(logging.INFO)

    scenario = simpledialog.askstring("Scenario Selection", "Please select a scenario (trello/jira/salesforce): ")

    scenario = scenario.lower()
    api_spec, headers = None, None

    # database connection details
    db_config = {
        'host': 'localhost',
        'database': 'synapse-copilot',
        'user': 'root',
        'password': '',
    }

    # Connect to the MySQL server
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    user_id = simpledialog.askinteger("User ID", "Enter the user id:")

    if scenario == "tmdb":
        os.environ["TMDB_ACCESS_TOKEN"] = config["tmdb_access_token"]
        api_spec, headers = process_spec_file(
            file_path="specs/tmdb_oas.json", token=os.environ["TMDB_ACCESS_TOKEN"]
        )
        query_example = "Give me the number of movies directed by Sofia Coppola"

    elif scenario == "spotify":
        os.environ["SPOTIPY_CLIENT_ID"] = config["spotipy_client_id"]
        os.environ["SPOTIPY_CLIENT_SECRET"] = config["spotipy_client_secret"]
        os.environ["SPOTIPY_REDIRECT_URI"] = config["spotipy_redirect_uri"]

        api_spec, headers = process_spec_file(file_path="specs/spotify_oas.json")

        query_example = "Add Summertime Sadness by Lana Del Rey in my first playlist"

    elif scenario == "discord":
        os.environ["DISCORD_CLIENT_ID"] = config["discord_client_id"]

        api_spec, headers = process_spec_file(
            file_path="specs/discord_oas.json", token=os.environ["DISCORD_CLIENT_ID"]
        )
        query_example = "List all of my connections"

    elif scenario == "stable":
        api_spec, headers = process_spec_file(
            file_path="specs/stablediffiusion_oas.json", token=os.environ["API_KEY"]
        )
        query_example = "Create cat image"

    elif scenario == "calendar":
        if user_id is not None:
            try:
                ser_qu = f"SELECT * FROM credentials WHERE user_id = {user_id};"
                cursor.execute(ser_qu)
                res = cursor.fetchone()
                res_t = res[2]
                messagebox.showinfo("Information", f"your token {res_t}")
                os.environ["GOOGLE_TOKEN"] = res_t
                dic = {
                    "user_id": user_id,
                    "your_token": res_t
                }
                messagebox.showinfo("Information", dic)
            except:
                messagebox.showinfo("Information", "Key is not present in the database")
                return ""

        else:
            messagebox.showinfo("Information", "Your id is incorrect.")

        api_spec, headers = process_spec_file(
            file_path="specs/calendar_oas.json", token=os.environ["GOOGLE_TOKEN"]
        )
        query_example = "What events do I have today?"

    elif scenario == "sheets":
        os.environ["GOOGLE_TOKEN"] = config["google_token"]

        api_spec, headers = process_spec_file(
            file_path="specs/sheets_oas.json", token=os.environ["GOOGLE_TOKEN"]
        )
        query_example = 'Create a new Spreadsheet with the name: "Exercise Logs". Print the complete api response result as it is.'

    elif scenario == "gmail":
        os.environ["GOOGLE_TOKEN"] = config["google_token"]

        api_spec, headers = process_spec_file(
            file_path="specs/gmail_oas.json", token=os.environ["GOOGLE_TOKEN"]
        )
        query_example = 'Send an email From: mohamedhachicha2001@gmail.com To: hachicha.mohamed@esprit.com Subject: Saying Hello This is a message just to say hello.'

    elif scenario == "google-meet":
        if user_id is not None:
            try:
                ser_qu = f"SELECT * FROM credentials WHERE user_id = {user_id};"
                cursor.execute(ser_qu)
                res = cursor.fetchone()
                res_t = res[2]
                messagebox.showinfo("Information", f"your token {res_t}")
                os.environ["GOOGLE_TOKEN"] = res_t
                dic = {
                    "user_id": user_id,
                    "your_token": res_t
                }
                messagebox.showinfo("Information", dic)
            except:
                messagebox.showinfo("Information", "Key is not present in the database")
                return ""

        else:
            messagebox.showinfo("Information", "Your id is incorrect.")

        api_spec, headers = process_spec_file(
            file_path="specs/calendar_oas.json", token=os.environ["GOOGLE_TOKEN"]
        )
        query_example = "Create a Google Meet the date is 25-06-2024 at 8:00 a.m with the name 'Bo7' that lasts 3 hours the event name is 'bo7' and print the complete API response result as it is."
    
    elif scenario == "notion":
        os.environ["NOTION_KEY"] = config["NOTION_KEY"]
        query_example = "Get me my page on notion"

    elif scenario == "upclick":
        os.environ["UPCLICK_KEY"] = config["UPCLICK_KEY"]

        api_spec, headers = process_spec_file(
            file_path="specs/upclick_oas.json", token=os.environ["UPCLICK_KEY"]
        )

        headers["Content-Type"] = "application/json"
        query_example = "Get me my spaces of team on upclick"

    elif scenario == "jira":
        if user_id is not None:
            try:
                ser_qu = f"SELECT * FROM jira_credentials WHERE user_id = {user_id};"
                cursor.execute(ser_qu)
                res = cursor.fetchone()
                token = res[2]
                host = res[3]
                username = res[3]

                messagebox.showinfo("Information", f"Fetched Jira token: {token}")
                messagebox.showinfo("Information", f"Fetched Jira host: {host}")
                messagebox.showinfo("Information", f"Fetched Jira username: {username}")

                os.environ["JIRA_TOKEN"] = token
                os.environ["jira_HOST"] = host

                dic = {
                    "user_id": user_id,
                    "user_token": token,
                    "user_host": host,
                    "user_name": username
                }
                messagebox.showinfo("Information", dic)

                replace_api_credentials(
                    model="api_selector",
                    scenario=scenario,
                    actual_key=username,
                    actual_token=token
                )
                replace_api_credentials(
                    model="planner",
                    scenario=scenario,
                    actual_key=username,
                    actual_token=token
                )
            except Exception as e:
                messagebox.showinfo("Information", f"key is not present in the database due to: {e}")
                return ""

            # Call the jira specific method to change the host and token with actual values
            replace_api_credentials_in_jira_json(
                scenario=scenario,
                actual_token=token,
                actual_host=host,
                actual_username=username
            )
            api_spec, headers = process_spec_file(
                ### to make the specs file minify or smaller for better processing
                file_path="specs/jira_oas.json",
                token=token,
                username=username
            )
        query_example = "Create a new Project with name 'abc_project'"

    elif scenario == "trello":
        if user_id is not None:
            try:
                # ser_qu = f"SELECT * FROM trello_credentials WHERE user_id = {user_id};"
                # cursor.execute(ser_qu)
                # res = cursor.fetchone()
                # print(f"Fetched Trello credentials: {res}")
                # key = str(res[2])
                # token = str(res[3])
                key = config["trello_key"]
                token = config["trello_token"]
                os.environ["TRELLO_API_KEY"] = key
                os.environ["TRELLO_TOKEN"] = token

                dic = {
                    "user_id": user_id,
                    "user_key": key,
                    "user_token": token
                }
                messagebox.showinfo("Information", dic)
            except Exception as e:
                print(f"Key is not present in the database {e}")
                return ""
        replace_api_credentials_in_json(
            ###to replace all the key and token variables in the specs file with real values
            scenario=scenario,
            actual_key=key,
            actual_token=token
        )
        api_spec, headers = process_spec_file(  ### to make the specs file minfy or smaller for for better processing
            file_path="specs/trello_oas.json",
            token=os.environ["TRELLO_TOKEN"],
            key=os.environ["TRELLO_API_KEY"]
        )

        replace_api_credentials(
            model="api_selector",
            scenario=scenario,
            actual_key=os.environ["TRELLO_API_KEY"],
            actual_token=os.environ["TRELLO_TOKEN"]
        )
        replace_api_credentials(
            model="planner",
            scenario=scenario,
            actual_key=os.environ["TRELLO_API_KEY"],
            actual_token=os.environ["TRELLO_TOKEN"]
        )

        query_example = "Create a new board with name 'abc_board'"

    elif scenario == "salesforce":
        credentials_fetch_query = f"SELECT * FROM salesforce_credentials WHERE user_id = {user_id};"
        cursor.execute(credentials_fetch_query)
        query_result = cursor.fetchone()

        domain = query_result[1]
        version = query_result[2]
        client_id = query_result[3]
        client_secret = query_result[4]
        access_token = query_result[5]

        print(f"Salesforce Domain: {domain}")
        print(f"Salesforce Version: {version}")
        print(f"Salesforce Client ID: {client_id}")
        print(f"Salesforce Client Secret: {client_secret}")
        print(f"Salesforce Access Token: {access_token}")

        replace_credentials_salesforce_json(
            scenario=scenario,
            actual_domain=domain,
            actual_version=version,
            actual_client_id=client_id,
            actual_client_secret=client_secret,
            actual_access_token=access_token
        )

        api_spec, headers = process_spec_file(
            file_path="specs/salesforce_oas.json",
            token=access_token,
        )
        query_example = "Create a new folder with name 'abc_folder'"
    else:
        raise ValueError(f"Unsupported scenario: {scenario}")

    populate_api_selector_icl_examples(scenario=scenario)
    populate_planner_icl_examples(scenario=scenario)

    requests_wrapper = Requests(headers=headers)

    # text-davinci-003
    

    # llm = ChatGroq(
    # temperature=0,
    # model="llama3-8b-8192",
    # api_key=config['GROQ_API_KEY'] # Optional if not set as an environment variable
    # )
    llm = AzureChatOpenAI(
        azure_deployment=config['azure_deployment'],
        azure_endpoint=config['azure_endpoint'],
        api_key=config['api_key'],
        api_version=config['api_version'],
        temperature=0
    )
    

    #llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0.0, max_tokens=1024)
    api_llm = ApiLLM(
        llm,
        api_spec=api_spec,
        scenario=scenario,
        requests_wrapper=requests_wrapper,
        simple_parser=False,
    )

    print(f"Example instruction: {query_example}")
    query = simpledialog.askstring("Query Input", "Please input an instruction (Press ENTER to use the example instruction): ", initialvalue=query_example)
    if query == "":
        query = query_example

    logger.info(f"Query: {query}")

    start_time = time.time()
    
    query_enhancer = AzureChatOpenAI(
        azure_deployment=config['azure_deployment'],
        azure_endpoint=config['azure_endpoint'],
        api_key=config['api_key'],
        api_version=config['api_version'],
        temperature=0
    )

    # query_to_enhance = f"you are an OPENAPI expert and you will enhance the original_query ,Keep every detail in the original_query and include the API s to use also make it suitable for an LLM to understand the tasks clearly. This is the original_query: {query}"


    # message = HumanMessage(
    #     content=query_to_enhance
    # )
    # enhanced_query = query_enhancer.invoke([message])
    # print(enhanced_query.content)

    if scenario == "gmail":
        how_to_encode = f"""extract from this query the content of the gmail message in this format : 
        
        From: example@example.com 
        To: example@example.com 
        Subject: the subject 

        the message
        
        
        this is the query : {query}
        """
        human_email_content = HumanMessage(
            content=how_to_encode
        )
        email_content = query_enhancer.invoke([human_email_content])
        print(email_content.content)
        base64content = base64.b64encode(email_content.content.encode('utf-8')).decode('utf-8')
        query = "this is the base64 content of the email : " + base64content  
    
    api_llm.run(query)
    logger.info(f"Execution Time: {time.time() - start_time}")


if __name__ == "__main__":
    main()
