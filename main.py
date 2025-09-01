import speech_recognition as sr

import chromadb  # type: ignore
import pypdf  # type: ignore
from langchain_community.document_loaders import PyPDFDirectoryLoader  # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore

from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore


# from openai import OpenAI
import time
import pyautogui
import json
from duckduckgo_search import DDGS
from google import genai

# elevenlabs requirements
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os


class LLMManager:
    def _init_(self) -> None:
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=api_key,
        )

    def invoke(self, prompt, **kwargs) -> str:
        return self.llm.invoke(prompt).content


def rag():
    chroma_client = chromadb.PersistentClient(
        path=r"C:\Users\yassi\Downloads\ieee ai\content\chroma_db"
    )

    collection = chroma_client.get_or_create_collection(
        name="tutorial", metadata={"hnsw:space": "cosine"}
    )

    loader = PyPDFDirectoryLoader(r"C:\Users\yassi\Downloads\ieee ai\content\data")

    raw_documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = text_splitter.split_documents(raw_documents)

    documents = []
    metadata = []
    ids = []

    i = 0

    for chunk in chunks:
        documents.append(chunk.page_content)
        ids.append("ID" + str(i))
        metadata.append(chunk.metadata)

        i += 1

    collection.upsert(documents=documents, metadatas=metadata, ids=ids)


# goToDesk is a function that i made so each time the bot take control i go back to desktop to avoid errors from having defrent starting points
def goToDesk():
    pyautogui.FAILSAFE = False
    c = pyautogui.size()
    pyautogui.moveTo(c)
    pyautogui.click()


# ducksearch is function useing the duckduckgo library to get link that will be searched for in the browser later
def ducksearch(prompt, max_results=2):
    results = DDGS().text(prompt, max_results=max_results)
    i = 1
    links = []
    for result in results:
        # googleSpeak(f"the link number{i}")
        # googleSpeak(f"the title is {result['title']}")
        print(result["href"])  # Note: it's "href" not "link" in the current version
        links.append(result["href"])
        # googleSpeak(result["body"])
        i += 1
    # googleSpeak("wich one do you chose")
    # n=recognizer()
    # googleSpeak(n)
    search(links[1])


# recognizer is a function used to reconize the speach from the user and turn it to text
def recognizer():
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        print("Please speak something:")
        audio = recognizer.listen(source)

        try:
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
        except sr.UnknownValueError:
            text = "Sorry, I could not understand the audio."
            print(text)
        except sr.RequestError as e:
            text = ""
            print(f"Could not request results; {e}")
    return text


# speak is using elevenlabs good quaity but limited time of free use
def elevenSpeak(text):
    load_dotenv()
    with open(
        r"C:\Users\ilyes\OneDrive\Desktop\api.txt", "r"
    ) as f:  # change this part so you have your api key here
        api_key = f.readlines()[2]
    elevenlabs = ElevenLabs(
        api_key=api_key,
    )

    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id="tnSpp4vdxKPjI9w0GnoV",
        model_id="eleven_multilingual_v2",
    )

    play(audio)


# append_json is used to append the json file that is used as history
def append_json(field, content):
    with open("history.json", "r", encoding="UTF-8") as f:
        json_file = json.load(f)
    json_file[field].append(content)
    with open("history.json", "w", encoding="UTF-8") as f:
        json.dump(json_file, f, indent=4)


# gemini is used to comunicate with gemini api as an alternative for the local server
def gemini(text):
    with open(
        r"C:\Users\ilyes\OneDrive\Desktop\api.txt", "r"
    ) as f:  # change this part so you have your api key here
        api_key = f.readlines()[0]

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(model="gemini-2.5-flash", contents=text)
    return response.text


# to shut down the pc
def shutdown():
    pyautogui.screenshot("screenshot.png")
    # pyautogui.screenshot("tofind1.png",[1128,65,307,42])
    r = pyautogui.locate("images/tofind.png", "screenshot.png")
    print(r)
    pyautogui.moveTo(r, duration=2)
    pyautogui.click()
    time.sleep(1)
    pyautogui.screenshot("screenshot.png")
    r1 = pyautogui.locate("images/tofind2.png", "screenshot.png")
    pyautogui.moveTo(r1, duration=2)
    pyautogui.click()
    time.sleep(1)
    pyautogui.screenshot("screenshot.png")
    r2 = pyautogui.locate("images/tofind3.png", "screenshot.png")
    pyautogui.moveTo(r2, duration=1)
    pyautogui.doubleClick()


llm = LLMManager()


# resp is used to choose what the bot should do based on your input
def resp(text):
    if text != "Sorry, I could not understand the audio.":
        if "search" in text:
            elevenSpeak("what do you want me to search for")
            prompt = recognizer()
            # prompt = "cats memes"
            ducksearch(prompt)
        if text.lower() == "shut down":
            shutdown()
        else:
            confirm = pyautogui.confirm(
                f"do you want to talk with the chatbot(it's slow)\n you said:{text}"
            )
            if confirm == "OK":
                collection = rag()
                results = collection.query(query_texts=[querry], n_results=3)

                print(results["documents"])

                system_prompt = (
                    """
                You are a mascot of the IEEE ISI student branch. You answer questions on this sb and talk about it to promote it.
                But you only answer based on knowledge I'm providing you. You don't use your internal
                knowledge and you don't make thins up.
                If you don't know the answer, just say: I don't know
                --------------------
                The data:
                """
                    + str(results["documents"])
                    + """
                --------------------
                the question : """
                    + str(querry)
                    + """
                """
                )

                response = llm.invoke(system_prompt)
                print("----------------------")
                print(response)
                h = {"user": text, "bot": response}
                append_json("chat", h)
                print(str(response).encode("utf-8"))
                elevenSpeak(str(response))


if __name__ == "__main__":
    querry = ""
    while querry != "exit":
        querry = recognizer()
        # querry = input("user: ")
        # search(querry)
        if querry == "exit":
            break
        if querry != "Sorry, I could not understand the audio.":
            resp(querry)
            # response = chat(querry)
            # print(response)
