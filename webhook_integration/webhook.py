import json
import os
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from send_ai_message_api import url, headers
import requests
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

class MessageData(BaseModel):
    data: dict


def process_message(data):
    # print("data: ", data)
    # get the message from the data body 
    # sample data body:
    # {'object': 'page', 'entry': [{'time': 1772614452299, 'id': '311430485396263', 'messaging': [{'sender': {'id': '8841919032488258'}, 'recipient': {'id': '311430485396263'}, 'timestamp': 1772614451570, 'message': {'mid': 'm_3GUPcAw19O8zrsNcCbiG0-3YSrgHqvT2Fq9Mw3_FPux3i3k5FiWtt0RxQ_Z6FAJKzRJ4ULRoKaqpGkglQLORMA', 'text': 'Hiii my name is pranto'}}], 'hop_context': {'app_id': 420863843067553, 'metadata': ''}}]}
    message = data.data['entry'][0]['messaging'][0]['message']['text']
    print("User message: ", message)
    # get the sender id 
    sender_id = data.data['entry'][0]['messaging'][0]['sender']['id']
    print("Sender id: ", sender_id)
    
    # process the message with ai
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")
    
    ai_response = llm.invoke(
        [SystemMessage(content="You are a helpful customer support chatbot for iHelpBD. You can help users for their queries."),
        HumanMessage(content=message)])

    # send the message to the user with API
    payload = json.dumps({
      "messaging_type": "MESSAGE_TAG",
      "tag": "ACCOUNT_UPDATE",
      "recipient": {
            "id": sender_id
        },
      "message": {
            "text": ai_response.content
        }
    })
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        print("AI message sent: ", response.text)
    except Exception as e:
        print(f"An error occurred while sending message: {e}")
    finally:
        print("AI message sent: ", response.text)
    
    return data


@app.post("/ai-message")
async def webhook(data: MessageData, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(process_message, data)
        print("webhook called")
        print("response: ", data)
        return {
            "status": "ok", "message": "Message received"
            }
    except Exception as e:
        print(f"An error occurred while processing message: {e}")
        return {
            "status": "error", "message": "Failed to process message"
            }
    