from helper import *
import mysql.connector
import random
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from langchain_openai import AzureChatOpenAI
from groq import Groq
import json
import ctypes
import tkinter as tk
import base64
import requests
from langchain_core.messages import HumanMessage
# logger = logging.getLogger()
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Make the application DPI aware
except:
    pass

from helper import *
import mysql.connector
import random
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI
from groq import Groq
import json
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QScreen
from flask import Flask, request, jsonify,send_from_directory
from flask_cors import CORS
from groq import Groq
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import azure.cognitiveservices.speech as speechsdk
logger = logging.getLogger()

# to improve hte quality of the application , we need to set the DPI awareness of the application.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Make the application DPI aware
except:
    pass


output='Example: Type "show me cast of Oppenheimer"'

#--------------------------------------------- Google Token Handeling ------------------------------------------------------------
config_file='yaml/config.yaml'
def read_tokens(config_file=config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config['google_token'], config['refresh_token']

def write_tokens(access_token, refresh_token, config_file=config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    config['google_token'] = access_token
    config['refresh_token'] = refresh_token
    with open(config_file, 'w') as file:
        yaml.safe_dump(config, file)

def refresh_access_token(refresh_token):
    token_url = 'https://oauth2.googleapis.com/token'
    params = {
        'client_id': "201574979983-gm1stllchrhhh85eqmng8dnho2r0djj6.apps.googleusercontent.com",
        'client_secret': "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",
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }
    response = requests.post(token_url, data=params)
    if response.status_code == 200:
        new_access_token = response.json()['access_token']
        return new_access_token
    else:
        raise Exception('Failed to refresh access token: {}'.format(response.content))

def is_token_expired(access_token):
    
        return True
    
def get_access_token():
    access_token, refresh_token = read_tokens()
    # Optionally, check if the token is expired (implementation depends on your use case)
    if is_token_expired(access_token):
        access_token = refresh_access_token(refresh_token)
        write_tokens(access_token, refresh_token)
    return access_token
#--------------------------------------------- ------------------------------------------------------------------------------------




app = Flask(__name__)
CORS(app)

client_voice = ElevenLabs(api_key="89b2645aa181a53247c15bbe7918d16e")

def text_to_speech_file(text: str) -> str:
    response = client_voice.text_to_speech.convert(
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Sarah pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    save_file_path = f"static/message.mp3"
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")
    return save_file_path



@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message")
    config = yaml.load(open("yaml/config.yaml", "r"), Loader=yaml.FullLoader)
    user_input = message
    
    logging.basicConfig(
        format="%(message)s",
        handlers=[logging.StreamHandler(ColorPrint())],
    )
    logger.setLevel(logging.INFO)
    client = Groq(
        api_key="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",
    )
    #user_input = simpledialog.askstring("Scenario Selection", "Please type your request ")
    
    conversation_history = []
    prompt_template = """
    If the user is talking in general and not giving commands, respond kindly and give short responses.
    If the user asks you to do something, you are an information extraction assistant. Your task is to extract specific details from user input and return them in JSON format. The user input will contain commands related to different scenarios.
    Don't provide any note or remark in the response. Only provide the extracted details in the JSON format.
    For each command, extract a list of the following details:
    - scenario: the application or platform mentioned in the input (e.g., "tmdb", "spotify", "stable", "calendar", "notion", "upclick",
        "discord", "sheets", "trello", "jira", "salesforce", "google-meet" , "gmail", "docs")
    - id: if the ID is not mentioned, default to 2
    - query: the action or command described by the user
    this is the list of the possible scenarios : ["tmdb", "spotify", "stable", "calendar", "notion", "upclick",
        "discord", "sheets", "trello", "jira", "salesforce", "google-meet" , "gmail", "docs"]
    Return only the extracted details in the following JSON format take note that the listeScenario can contain only 1 or multiple Scenarios and cannot be empty:
    {
    "listeScenario": [
        {
        "scenario": "<scenario1>",
        "id": "<id1>",
        "query": "<query1>"
        },
        {
        "scenario": "<scenario2>",
        "id": "<id2>",
        "query": "<query2>"
        },
        ...
    ]
    }


    Example 1
    If the user input is: "Open Trello and create a dashboard called 'board_vip'", your output should be:
    {
    "listeScenario": [
        {
        "scenario": "Gmail",
        "id": "2",
        "query": "send an email to John containing 'hey how are you ?'"
        },
        {
        "scenario": "Trello",
        "id": 2,
        "query": "create a dashboard called 'board_vip'"
        }
    ]
    }
    
    
    Example 2 : Create a new docs file with the title: "Hachicha". Print the complete api response result as it is.
    {
    "listeScenario": [
    {
    "scenario": "docs",
    "id": "2",
    "query": "Create a new docs file with the title: 'Hachicha'. Print the complete api response result as it is"
    }
    ]
    }
    Here is the user input:
    """
    conversation_history.append({"role": "system", "content": prompt_template})
    conversation_history.append({"role": "user", "content": user_input})
    chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model="llama3-8b-8192",
        )
    output = chat_completion.choices[0].message.content
            # Add the chatbot's response to the conversation history
    conversation_history.append(chat_completion.choices[0].message)

    # Print the result
    print("Chatbot response:", output)
    
    try:
        parsed_output = json.loads(output)
        # Access the first scenario in the "listeScenario" array
        for  item in parsed_output["listeScenario"]:
            scenario =  item["scenario"]
            print (scenario)
            print(item["query"])

        
            #scenario = simpledialog.askstring("Scenario Selection", "Please select a scenario (trello/jira/salesforce): ")
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

            user_id = parsed_output["listeScenario"][0]["id"]

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
                access_token = get_access_token()
                os.environ["GOOGLE_TOKEN"] = access_token

                api_spec, headers = process_spec_file(
                    file_path="specs/calendar_oas.json", token=os.environ["GOOGLE_TOKEN"]
                )
                query_example = "What events do I have today?"

            elif scenario == "sheets":
                access_token = get_access_token()
                os.environ["GOOGLE_TOKEN"] = access_token

                api_spec, headers = process_spec_file(
                    file_path="specs/sheets_oas.json", token=os.environ["GOOGLE_TOKEN"]
                )
                query_example = 'Create a new Spreadsheet with the name: "Exercise Logs". Print the complete api response result as it is.'

            
            elif scenario == "docs":
                access_token = get_access_token()
                os.environ["GOOGLE_TOKEN"] = access_token

                api_spec, headers = process_spec_file(
                    file_path="specs/docs_oas.json", token=os.environ["GOOGLE_TOKEN"]
                )
                query_example = 'Create a new docs file with the title: "Hachicha". Print the complete api response result as it is.'
            
            elif scenario == "gmail":
                access_token = get_access_token()
                os.environ["GOOGLE_TOKEN"] = access_token

                api_spec, headers = process_spec_file(
                    file_path="specs/gmail_oas.json", token=os.environ["GOOGLE_TOKEN"]
                )
                query_example = 'Send an email From: mohamedhachicha2001@gmail.com To: hachicha.mohamed@esprit.tn Subject: Saying Hello This is a message just to say hello.'

            elif scenario == "google-meet":
                access_token = get_access_token()
                os.environ["GOOGLE_TOKEN"] = access_token

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
            query = item["query"]
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
            
            #TO_DO sound notification
            
            response = "Done !"
    except json.JSONDecodeError as e:
        response = output


    # audio_file_path = text_to_speech_file(response)
    # return jsonify({"response": response, "audio_file": os.path.basename(audio_file_path)})
    return jsonify({"response": response, "audio_file": os.path.basename("C:\\Users\\hachichaMed\\Desktop\\Agile-Loop\\static\\message.mp3")})
    


def speech_to_text_file():
    speech_key, service_region = "fd1c98be42a2404d91f56ab21507bd1c", "francecentral"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    print("Say something...")
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    print(result.text)
    return result.text

@app.route('/static/<path:filename>', methods=['GET'])
def serve_audio(filename):
    return send_from_directory('static', filename)

@app.route("/speech_to_text", methods=["POST"])
def speech_to_text():
    recognized_text = speech_to_text_file()
    return jsonify({"recognized_text": recognized_text})
class FlaskThread(QThread):
    def __init__(self, app):
        QThread.__init__(self)
        self.app = app

    def run(self):
        self.app.run(port=5000, debug=False, use_reloader=False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Jarvis")
        self.setGeometry(100, 100, 1000, 800)  # Increased size to 1000x800
        self.center_window()
        self.webview = QWebEngineView()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        html_file = os.path.join(base_dir, 'index.html')
        file_url = QUrl.fromLocalFile(html_file)

        self.webview.setUrl(file_url)
        layout = QVBoxLayout()
        layout.addWidget(self.webview)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def center_window(self):
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)


if __name__ == "__main__":
    flask_thread = FlaskThread(app)
    flask_thread.start()

    pyqt_app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(pyqt_app.exec_())