from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

class MessageData(BaseModel):
    data: dict


def process_message(data):
    print("data: ", data)
    # process the message here
    
    # send the message to the user
    # save the message to the database
    # etc.
    # return the response
    # response = f'This is your message {data.data} and it came from {data.platform}'
    
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
    