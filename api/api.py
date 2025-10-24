import sqlite3
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
import unicodedata
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from redis.asyncio import Redis, from_url
import asyncio

def remove_accents(text):
    """
    Remove accents from the Greek characters in the input text.
    """
    normalized_text = unicodedata.normalize('NFD', text)
    return ''.join([char for char in normalized_text if not unicodedata.combining(char)])

def greek_to_greeklish(text):
    """
    Turn greek to greeklish for printing
    """
    text = remove_accents(text)

    greeklish_dict = {
        'α': 'a', 'β': 'v', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'i',
        'θ': 'th', 'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x',
        'ο': 'o', 'π': 'p', 'ρ': 'r', 'σ': 's', 'τ': 't', 'υ': 'y', 'φ': 'f',
        'χ': 'ch', 'ψ': 'ps', 'ω': 'o', 'ς': 's',
        'Α': 'A', 'Β': 'V', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'I',
        'Θ': 'TH', 'Ι': 'I', 'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X',
        'Ο': 'O', 'Π': 'P', 'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y', 'Φ': 'F',
        'Χ': 'CH', 'Ψ': 'PS', 'Ω': 'O'
    }

    greeklish_text = ''.join([greeklish_dict.get(char, char) for char in text])
    return greeklish_text

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "API_KEY_HERE"

def get_db_connection():
    conn = sqlite3.connect('notifications.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.get("/")
@limiter.limit("5/minute")
def read_root(request:Request):
    return {"message": "Welcome to our API!"}

@app.get("/get_records/")
@limiter.limit("7/minute")
async def get_records(request:Request, key: str = Query(..., min_length=1)):
    if key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    timeout = 10
    polling_interval = 1
    with get_db_connection() as conn:
        notifications = conn.execute('SELECT message FROM notifications').fetchall()
        messages = [notification["message"] for notification in notifications]

        if messages:
            conn.execute('DELETE FROM notifications')
            conn.commit()

    return {"messages": messages}

class AddRecordReq(BaseModel):
    key: str
    message: str

@app.post("/add_record/")
@limiter.limit("20/minute")
def add_record(request:Request, record: AddRecordReq):
    if record.key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    with get_db_connection() as conn:
        conn.execute('INSERT INTO notifications (message) VALUES (?)', (greek_to_greeklish(record.message),))
        conn.commit()

    return {"message": f"Record added with message: '{greek_to_greeklish(record.message)}'"}

init_db()