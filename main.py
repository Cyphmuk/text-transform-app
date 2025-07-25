from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from cryptography.fernet import Fernet, InvalidToken
import base64
import os

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join("static", "index.html"))

# Request model for encryption/decryption
class RequestData(BaseModel):
    text: str
    mode: str  # "encrypt" or "decrypt"
    key: str   # Fernet key (base64-encoded 32-byte)

# Optional: backend-generated Fernet key
@app.get("/generate-key")
def generate_key():
    return {"key": Fernet.generate_key().decode()}

# Helper: Validate and create Fernet object from key
def get_fernet(key: str):
    try:
        key_bytes = base64.urlsafe_b64decode(key)
        if len(key_bytes) != 32:
            raise ValueError
        return Fernet(key.encode())
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Fernet key. Must be a base64-encoded 32-byte string.")

# Encrypt or decrypt text
@app.post("/transform")
def transform(data: RequestData):
    fernet = get_fernet(data.key)

    try:
        if data.mode.lower() == "encrypt":
            result = fernet.encrypt(data.text.encode()).decode()
        elif data.mode.lower() == "decrypt":
            result = fernet.decrypt(data.text.encode()).decode()
        else:
            raise HTTPException(status_code=400, detail="Invalid mode. Use 'encrypt' or 'decrypt'.")
        return {"result": result}
    except InvalidToken:
        raise HTTPException(status_code=400, detail="Decryption failed. Key is incorrect or data is corrupted.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
