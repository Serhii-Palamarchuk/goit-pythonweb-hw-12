from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: date
    additional_data: Optional[str] = None

class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: date
    additional_data: Optional[str] = None

app = FastAPI(title="Contacts API Test")

# In-memory storage for testing
contacts_db = []
next_id = 1

@app.get("/")
def read_root():
    return {"message": "Welcome to Contacts API"}

@app.post("/api/contacts/", response_model=ContactResponse)
def create_contact(contact: ContactCreate):
    global next_id
    contact_data = contact.dict()
    contact_data["id"] = next_id
    next_id += 1
    contacts_db.append(contact_data)
    return contact_data

@app.get("/api/contacts/", response_model=List[ContactResponse])
def get_contacts():
    return contacts_db

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)