import openai
from os import environ

# Load your API key from an environment variable or secret management service
openai.api_key = environ.get('OPENAI_API_KEY')


def review_code(source_code):
    try:
        # Create a list to store all the messages for context
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
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
        messages.append({'role': 'assistant', 'content': chat_message})
        # return chat_message
        return environ.get('OPENAI_API_KEY')

    except Exception as e:
        raise e
