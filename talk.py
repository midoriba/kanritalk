from openai import OpenAI

MODEL_NAME = 'gpt-3.5-turbo'
MAX_TOKENS = 200

client = OpenAI()
prompt 
def extract_slot_value(utterance):
    client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {'user': ''}
        ]
    )

talks = []

slots = {'好きな食べ物': '', '': ''}
slot_counts = len(slots)
slot_to_ask = 0
while True:
    system_messages = [
        {'role': 'system', 'content': f'あなたは親切なアシスタントです。ユーザーに「{slots.keys[slot_to_ask]}について尋ねてください'},
    ]
    talks.append({'role':'user', 'content': input('user: ')})
    messages = system_messages + talks

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages
    )

    talks.append({'role':'assistant', 'content':response.choices[0].message.content})
    print(f"{talks[-1]['role']}: {talks[-1]['content']}")
    
        