from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use caution in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def transform_sentence(input_string, mode):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    reverse_alphabet = alphabet[::-1]
    mapping = str.maketrans(alphabet + alphabet.upper(), reverse_alphabet + reverse_alphabet.upper())

    if mode == 'encrypt':
        transformed_string = input_string.translate(mapping)
        transformed_string = ''.join(str(max(0, int(c) - 1)) if c.isdigit() else c for c in transformed_string)
        transformed_string = transformed_string[::-1]

    elif mode == 'decrypt':
        transformed_string = input_string[::-1]
        transformed_string = ''.join(
            str(int(c) + 1) if c.isdigit() and c != '0' else '0' if c == '0' else c
            for c in transformed_string
        )
        reverse_mapping = str.maketrans(reverse_alphabet + reverse_alphabet.upper(), alphabet + alphabet.upper())
        transformed_string = transformed_string.translate(reverse_mapping)

    else:
        raise ValueError("Invalid mode. Use 'encrypt' or 'decrypt'.")

    return transformed_string

class RequestData(BaseModel):
    text: str
    mode: str  # "encrypt" or "decrypt"

@app.post("/transform")
def transform(data: RequestData):
    try:
        result = transform_sentence(data.text, data.mode.lower())
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
return
FileResponse(os.path.join("static","index.html"))