#IMPORTS
import requests
import uuid
import time

#SETUP
BASE_URL = "https://snippetapi.isaacrichardson.repl.co"
ADD_ENDPOINT = "/add"
GET_ENDPOINT = "/get"
DELETE_ENDPOINT = "/delete"

def add(code,explanation,timer=False):
    if timer:
        start_time = time.time()
    filename = str(uuid.uuid4())
    data = {
        "filename": filename,
        "code": code,
        "explanation": explanation
    }
    response = requests.post(BASE_URL + ADD_ENDPOINT, json=data)
    if timer:
        end_time = time.time()
        print("Ran in ", end_time - start_time, "seconds")
    return response.json()["uuid"]

def get(uuid, variables, timer=False,gptengine="text-davinci-003",engine="jade-001",tokens=50,temperature=0.1,):
    type = "Completion"
    if timer:
        start_time = time.time()
    if "gpt" in gptengine:
        type="ChatCompletion"
    data = {
        "uuid": uuid,
        "variables": variables,
        "engine":gptengine,
        "tokens":tokens,
        "temperature":temperature,
        "type":type,
        "n":1,
        "gpt":engine
    }
    response = requests.post(BASE_URL + GET_ENDPOINT, json=data)
    if timer:
        end_time = time.time()
        print("Ran in", end_time - start_time, "seconds")
    return response.json()["output"].replace("'","")
def delete(uuid,timer=False):
    return requests.delete(BASE_URL + DELETE_ENDPOINT + f"/{uuid}").json()["result"]
