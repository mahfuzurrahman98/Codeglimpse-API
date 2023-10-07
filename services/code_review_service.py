import openai
from os import environ
import json

import requests

# Load your API key from an environment variable or secret management service
openai.api_key = environ.get('OPENAI_API_KEY')


def review_code0(source_code):
    try:
        service_url = environ.get('CODE_REVIEW_SERVICE_URL')
        # send a post request to the code review service with the source_code, endpoint is /review-code
        payload = json.dumps({
            "source_code": source_code
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request(
            "POST",
            service_url + '/review-code',
            headers=headers,
            data=payload
        )

        # it will return a json with {message, and data}, just take the data and return it
        response_text = json.loads(response.text)
        # print(response_text)
        return response_text['data']

    except Exception as e:
        # print(e)
        raise e

def review_code(source_code):
        openai.api_key = environ.get('OPENAI_API_KEY')
        # Create a list to store all the messages for context
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'}
        ]

        # Add the source_code to the list
        messages.append({'role': 'user', 'content': source_code})

        # Add the prompt to modify the code
        messages.append({'role': 'system', 'content': 'Do a in depth proper code review, make the code documented, and put better comments where needed. Just give the code as output, No additional messages like "here is your code, Sure, blah blah".'})

        # Request gpt-3.5-turbo for chat completion
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages
        )

        # Print the response and add it to the messages list
        chat_message = response['choices'][0]['message']['content']
        # just keep the portion between ``` and ```, and also remove the first line
        chat_message = chat_message.split('```')[1].split('```')[0].split('\n', 1)[1]
        
        messages.append({'role': 'assistant', 'content': chat_message})
        return chat_message