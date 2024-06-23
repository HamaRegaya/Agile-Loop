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
from groq import Groq
import json
import ctypes
import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk, ImageSequence
import tkinter.font as tkFont
import pyaudio
import wave
import threading

logger = logging.getLogger()

# to improve hte quality of the application , we need to set the DPI awareness of the application.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Make the application DPI aware
except:
    pass


output='Example: Type "show me cast of Oppenheimer"'


class AgileLoopApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Agile Loop")
        self.geometry("450x250+1000+500")  # Adjust the size and position as needed
        self.configure(bg="#000000")  # Background color
        self.wm_attributes("-topmost", 1)
        # Register custom font
        self.register_font("LeagueSpartan-Regular.ttf")

        # Load custom font
        self.league_spartan = tkFont.Font(family="League Spartan", size=25)
        self.league_spartan_small = tkFont.Font(family="League Spartan", size=14)
        self.league_spartan_example = tkFont.Font(family="League Spartan", size=10)

        self.is_recording = False  # Initialize recording state

        self.create_widgets()
        self.league_spartan_example = ("League Spartan", 12)  # Example font definition
        
        self.example_frame = tk.Frame(self, bg="#1c1c1c")
        self.example_frame.pack(pady=5)

        self.example_label = tk.Label(self.example_frame, text=output, font=self.league_spartan_example, bg="#000000", fg="white")
        self.example_label.pack()
        
        
    def update_label(self, new_text):
        self.example_label.config(text=new_text)
        
    
    def register_font(self, font_path):
        try:
            tkFont.nametofont("TkDefaultFont").actual()
            tkFont.Font(family="League Spartan", size=12).actual()
        except:
            self.tk.call("font", "create", "League Spartan", "-family", "League Spartan", "-size", "12", "-weight", "normal", "-slant", "roman", "-underline", "0", "-overstrike", "0")
            self.tk.call("font", "configure", "League Spartan", "-file", font_path)

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg="#000000")
        header_frame.pack(pady=10)

        # Load and resize GIF logo
        self.logo_gif = Image.open("waves.gif")  # Replace with the path to your GIF logo
        # self.logo_gif = self.logo_gif.resize((100, 80), Image.LANCZOS)  # Resize the GIF

        self.logo_frames = [ImageTk.PhotoImage(img.copy().convert("RGBA")) for img in ImageSequence.Iterator(self.logo_gif)]
        self.logo_label = tk.Label(header_frame, bg="#000000")
        self.logo_label.pack(side=tk.LEFT, padx=(0, 10))
        self.animate_logo(0)

        header_label = tk.Label(header_frame, text="Agile Loop", font=self.league_spartan, bg="#000000", fg="white")
        header_label.pack(side=tk.LEFT)

        # Search Bar
        search_frame = tk.Frame(self, bg="#000000")
        search_frame.pack(pady=20)

        self.search_entry = tk.Entry(search_frame, font=self.league_spartan_small, width=25, bd=0, insertbackground="white", bg="#333333", fg="white")
        self.search_entry.pack(side=tk.LEFT, padx=10, ipady=5)
        self.search_entry.bind("<Return>", self.perform_search)
        # Load icons
        # search_icon = PhotoImage(file="search_icon.png")  # Replace with the path to your search icon
        # mic_icon = PhotoImage(file="mic_icon.png")  # Replace with the path to your mic icon

        search_button = tk.Button(search_frame, text="🔍", font=self.league_spartan_small, bg="#ff6600", fg="white", bd=0, command=self.perform_search)
        search_button.pack(side=tk.LEFT)
        
        # Microphone Button
        self.mic_button = tk.Button(search_frame, text="🎤", font=self.league_spartan_small, bg="#ff6600", fg="white", bd=0, command=self.toggle_mic)
        self.mic_button.pack(side=tk.LEFT, padx=5)

        # # Example Label
        # example_frame = tk.Frame(self, bg="#1c1c1c")
        # example_frame.pack(pady=5)

        # example_label = tk.Label(example_frame, text=output, font=self.league_spartan_example, bg="#000000", fg="white")
        # example_label.pack()

    def animate_logo(self, frame_index):
        frame = self.logo_frames[frame_index]
        self.logo_label.configure(image=frame)
        frame_delay = self.logo_gif.info['duration'] // 10  # Divide by 10 to convert milliseconds to deciseconds
        self.after(frame_delay, self.animate_logo, (frame_index + 1) % len(self.logo_frames))

    def perform_search(self, event=None):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search query.")
            return
        # Call main function with user input
        self.main(query)

    def toggle_mic(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.mic_button.config(text="⏹️")  # Change button text to stop icon
        threading.Thread(target=self.record_audio).start()

    def stop_recording(self):
        self.is_recording = False
        self.mic_button.config(text="🎤")  # Change button text to mic icon
        # Stop the recording thread gracefully (handle in record_audio)
        self.stop_recording_event.set()

    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        WAVE_OUTPUT_FILENAME = "output.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("* recording")

        frames = []
        self.stop_recording_event = threading.Event()

        while not self.stop_recording_event.is_set():
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Transcribe the audio
        transcription = self.query(WAVE_OUTPUT_FILENAME)
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, transcription)

    def query(self, filename):
        client = Groq(
            api_key="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",
        )
        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3",
                prompt="Specify context or spelling",
                response_format="json",
                language="en",
                temperature=0.0
            )
        return transcription.text


    def main(self,user_input):
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        root.geometry("400x250")

        config = yaml.load(open("yaml/config.yaml", "r"), Loader=yaml.FullLoader)

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
        - scenario: the application or platform mentioned in the input (e.g., Trello, Slack, etc.)
        - id: if the ID is not mentioned, default to 2
        - query: the action or command described by the user
        this is the list of the possible scenarios : ["tmdb", "spotify", "stable", "calendar", "notion", "upclick",
            "discord", "sheets", "trello", "jira", "salesforce", "google-meet" , "gmail"]
        Return only the extracted details in the following JSON format:
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
            scenario = parsed_output["listeScenario"][0]["scenario"]
            print (scenario)
            
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
            query = parsed_output["listeScenario"][0]["query"]
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
            
            self.update_label("Done !")
        except json.JSONDecodeError as e:
            self.update_label(output)

if __name__ == "__main__":
    app = AgileLoopApp()
    app.mainloop()
