import os
import time
import threading,time,itertools
def loading(stop_event):
    for dots in itertools.cycle(["",".","..","...",]):
        if stop_event.is_set():
            break
        print(f"\rAgent is searching and thinking{dots:<3}",end="",flush=True)
        time.sleep(0.4)
    print("\r"+""*50+"\r",end="",flush=True)
from google import genai
from google.genai import types
import serpapi
from dotenv import load_dotenv
load_dotenv()
ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
search_client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))

def google_search_tool(query: str) -> str:
    try:
        results = search_client.search({
            "q": query,
            "hl": "en",
            "gl": "us",
        })

        organic_results = results.get("organic_results", [])
        if not organic_results:
            return "No concrete web results found."
        snippets = [res.get("snippets", "") for res in organic_results[:3]]
        return "\n".join(snippets)
    except Exception as e:
        return f"Error executing search: {str(e)}"
chat = ai_client.chats.create(
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful AI assistant. You access to a Google Search tool. Use it whenever asked about real-time,current events, or factual queries ypu aren't certain about.",
        tools=[google_search_tool]
    )
)
print(":Hey there! How can i help you?. Type 'exit' to quit.")
while True:
    user_input = input("You:")
    if user_input.lower() == "exit":
        break
    stop = threading.Event()
    spinner = threading.Thread(target=loading, args=(stop,))
    spinner.start()
    reply = None
    for attempt in range(3):
       try:
          reply = chat.send_message(user_input).text
          break
       except Exception as e:
         if "503" in str(e) and attempt < 2:
             time.sleep(3)
         else:
          reply = f"Error:{e}"
          break

    stop.set()
    spinner.join()
    print(f"\nAgent:{reply}")