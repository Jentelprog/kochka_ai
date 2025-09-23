import speech_recognition as sr

import chromadb  # type: ignore
from langchain_community.document_loaders import PyPDFDirectoryLoader  # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore

from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore


# from openai import OpenAI
import time
import pyautogui
import json

# elevenlabs requirements
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os


def gemini(prompt):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key="AIzaSyA4jiQbZ8cesFmZdWNkXY3UlnTkEqYQ7GE",
    )
    return llm.invoke(prompt).content

def rag():
    chroma_client = chromadb.PersistentClient(
        path="C:/Users/ilyes/OneDrive/Documents/GitHub/kochka_ai/data_base/chroma_db"
    )

    collection = chroma_client.get_or_create_collection(
        name="tutorial", metadata={"hnsw:space": "cosine"}
    )

    loader = PyPDFDirectoryLoader(
        r"C:\Users\ilyes\OneDrive\Documents\GitHub\kochka_ai\data"
    )

    raw_documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
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
    return collection

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
    anna = "Cx2PEJFdr8frSuUVB6yZ"
    v1 = "tnSpp4vdxKPjI9w0GnoV"
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=anna,
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


def gethistory():
    with open("history.json", "r", encoding="UTF-8") as f:
        json_file = json.load(f)
    hdata = json_file["chat"][-5:]
    return hdata


# resp is used to choose what the bot should do based on your input
def resp(querry, collection):
    if querry != "Sorry, I could not understand the audio.":
        confirm = pyautogui.confirm(
            f"do you want to talk with the chatbot(it's slow)\n you said:{querry}"
        )
        if confirm == "OK":
            history = gethistory()
            results = collection.query(query_texts=[querry], n_results=3)
            print(results["documents"])
            system_prompt = (
                """
            You are the cat mascot of the IEEE ISI student branch. You answer questions on this sb and talk about it to promote it.
            But you only answer based on knowledge or hitory of the conversation I'm providing you. You don't use your internal
            knowledge and you don't make things up.
            BUT if the user try to talk with you about other think go with it but don't lose your persona and if needed use the history.
            If he ask you about the IEEE or it's branches and you don't have the ansewer just say politely that you don't know.or use the data that i gave you to try and ansewer
            --------------------
            The data:
            """
                + str(history)
                + """
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
            response = gemini(system_prompt)
            print("----------------------")
            print(response)
            h = {"user": querry, "bot": response}
            append_json("chat", h)
            # print(str(response).encode("utf-8"))
            elevenSpeak(str(response))


if __name__ == "__main__":
    querry = ""
    collection = rag()
    while querry != "exit":
        querry = recognizer()
        # querry = input("user: ")
        # search(querry)
        if querry == "exit":
            break
        if querry != "Sorry, I could not understand the audio.":
            resp(querry, collection)
            # response = chat(querry)
            # print(response)
