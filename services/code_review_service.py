import openai
from os import environ
from fastapi import FastAPI, HTTPException

# Load your API key from an environment variable or secret management service
openai.api_key = environ.get('OPENAI_API_KEY')


def get_response_openai(source_code, language):
    try:
        instructions = 'Do an in-depth code review, and improve comments, no additionl documentaion after or bvefore the code, just rewrite the code precisely.'

        messages = [
            {'role': 'system', 'content': 'You are an experienced software engineer reviewing a random code snippet.'},
            {'role': 'system', 'content': f'Code snippet is in {language}.'},
            {'role': 'user', 'content': source_code},
            {'role': 'user', 'content': instructions}
        ]
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-0613',
            messages=messages,
            stream=True
        )
    except Exception as e:
        print("Error in creating campaigns from OpenAI:", str(e))
        raise HTTPException(503, detail=str(e))

    for chunk in response:
        choice_delta = chunk["choices"][0]["delta"]
        # basically the choice_delta is a object = {'content': 'something'}, if the object is not empty and has conent and the content is not empty, then we can return the content

        if choice_delta and choice_delta["content"]:
            current_content = choice_delta.get("content", "")
            # print(current_content)
            yield current_content
        else:
            break
        # replace \n with <br> to display in html
        # current_content = current_content.replace("\n", "<br>")
        # yield current_content
        # print(current_content)
