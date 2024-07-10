# IMPORTS
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import uuid
import openai
import requests
import io
import sys

# APP SETUP
app = FastAPI()

# ROUTES
@app.get("/")
async def index():
    return {"message": "API Online. Snippet API is ready for requests."}

@app.post("/add")
async def add(data: dict):
    code = data['code']
    explanation = data['explanation']
    uid = str(uuid.uuid4())
    data = {"key": uid, "snippet": code, "explanation": explanation}
    requests.post("https://snippetdb.isaacrichardson.repl.co/add", json=data)
    return JSONResponse(content={"uuid": uid})

@app.post("/get")
async def get(data: dict):
    uid = data['uuid']
    engine = data['engine']
    tokens = data['tokens']
    type = data['type']
    temperature = data['temperature']
    n = data['n']
    gpt = data['gpt']
    result = requests.get(f"https://snippetdb.isaacrichardson.repl.co/get/{uid}").json()["result"]
    if gpt == "amethyst-001":
        prompt = f"Execute the following code according to the instructions\n'{result['explanation']}':\n\n{result['code']}\n\n"
        for k, v in data['variables'].items():
            prompt += f"{k} = '{v}'\n"
        prompt += "\nOutput:"
        if type == "ChatCompletion":
            messages=[{"role": "system", "content": "You are an ai who can analyse code. You should respond with just the output of the code snippets given to you and nothing else. Do not respond with any other text, only the output. Code that is not from a specific programming language should work as long as the code's function is explained."},
            {"role": "user", "content": f"{prompt}"}]
            response = openai.ChatCompletion.create(
                    model=engine,
                    messages = messages,
                    max_tokens=tokens,
                    n=n,
                    stop=None,
                    temperature=temperature,
                )
            for i in response['choices']:
            	output = i['message']['content']
        else:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                max_tokens=tokens,
                n=n,
                stop=["'''",'"""'],
                temperature=temperature,
            )
            output = response.choices[0].text.strip()
        return JSONResponse(content={"output": output})
    elif gpt == "jade-001":
        try:
            code = ""
            for k, v in data['variables'].items():
                code += f"{k} = '{v}'\n"
            code += '\n' + result['code']
            output_buffer = io.StringIO()
            sys.stdout = output_buffer
            exec(code)
            sys.stdout = sys.__stdout__
            output = output_buffer.getvalue()
            return JSONResponse(content={"output": output})
        except SyntaxError as e:
            raise HTTPException(status_code=400, detail=f"Syntax Error: '{str(e)}'")
    else:
        raise HTTPException(status_code=400, detail=f"Invalid engine '{gpt}'. Try using amethyst-001 or jade-001")

@app.delete('/delete/{uid}')
async def delete(uid: uuid.UUID):
    response = requests.delete(f'https://snippetdb.isaacrichardson.repl.co/delete/{uid}')
    if response.status_code == 200:
        return {"result": response.json()["result"]}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())

if __name__ == '__main__':
    openai.api_key = "openai_api_key"
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
