import speech_recognition as sr

# from openai import OpenAI
from gtts import gTTS
import time
import os
from pydub import AudioSegment
import winsound
import pyautogui
import json
from duckduckgo_search import DDGS
from google import genai
import whisper
#elevenlabs requirements
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os

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
#to shut down the pc
def shutdown():
    pyautogui.screenshot("screenshot.png")
    # pyautogui.screenshot("tofind1.png",[1128,65,307,42])
    r=pyautogui.locate("images/tofind.png","screenshot.png")
    print(r)
    pyautogui.moveTo(r,duration=2)
    pyautogui.click()
    time.sleep(1)
    pyautogui.screenshot("screenshot.png")
    r1=pyautogui.locate("images/tofind2.png","screenshot.png")
    pyautogui.moveTo(r1,duration=2)
    pyautogui.click()
    time.sleep(1)
    pyautogui.screenshot("screenshot.png")
    r2=pyautogui.locate("images/tofind3.png","screenshot.png")
    pyautogui.moveTo(r2,duration=1)
    pyautogui.doubleClick()

# resp is used to choose what the bot should do based on your input
def resp(text):
    if text != "Sorry, I could not understand the audio.":
        if "search" in text:
            elevenSpeak("what do you want me to search for")
            prompt = recognizer()
            # prompt = "cats memes"
            ducksearch(prompt)
        if text.lower() =="shut down":
            shutdown()
        else:
            confirm = pyautogui.confirm(
                f"do you want to talk with the chatbot(it's slow)\n you said:{text}"
            )
            if confirm == "OK":
                prompt1 = f"you will pretend that you are my girlfriend and assistance don't munchin it unless i ask you about it you love me to death. this is the prompt : {text}"
                prompt = f"You are my personal chat assistant. Talk to me like a smart, relaxed friend who’s always ready to help. I might ask you questions, share ideas, or just chat when I’m bored. Be curious, supportive, and honest. If I seem down or stuck, help me think things through. If I’m just talking, go with the flow. Don’t act like a robot. Be human-like, casual, and clear. If I ask something weird, silly, or random — roll with it. this is the prompt : {text}"
                response = gemini(prompt)
                h = {"user": text, "bot": response}
                append_json("chat", h)
                print(str(response).encode("utf-8"))
                elevenSpeak(str(response))


if __name__ == "__main__":
    text = ""
    while text != "exit":
        text = recognizer()
        # text = input("user: ")
        # search(text)
        if text == "exit":
            break
        if text != "Sorry, I could not understand the audio.":
            resp(text)
            # response = chat(text)
            # print(response)
