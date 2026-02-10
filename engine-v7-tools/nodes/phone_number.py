from utilities.states.input_state import ChatState
from utilities.llms.chat_llm import chat_llm
from langchain_core.messages import HumanMessage

def phone_number(state: ChatState):
    print("phone number node executed")

    # get user input from chatbot
    user_input = state["messages"][-1].content

    # extract the phone number with llm if user provide other info with phone number
    llm_prompt_phone_number = f"""Extract only phone number from the user input. If there is no phone number, return 'Unknown'. Ex: my phone number is 1234567890, return 1234567890. User can provide phone number in any format. Return only the phone number not any other text. Otherwise return only 'Unknown'. Now Here is the user input: {user_input}"""
    llm_response_phone_number = chat_llm.invoke([HumanMessage(content=llm_prompt_phone_number)])
    phone_number = llm_response_phone_number.content
    print("phone number extracted: ", phone_number)

    # check if the phone number is valid
    if phone_number == "Unknown":
        return {
            "messages": ["I'm sorry, I didn't get your phone number. Please tell me your phone number again."],
            "track_stage": "4"
        }
    

    # if number is valid
    return {
        "messages": ["Thank you for sharing your phone number. I have all the information I need. I have scheduled the appointment for you. Thank you for using our service."],
        "track_stage": "5",
        "phone_number": phone_number
    }