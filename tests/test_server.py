from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
from typing import Optional


class TestContact(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: date
    additional_data: Optional[str] = None


app = FastAPI(title="Simple Test API")


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/test")
def test_endpoint():
    return {"status": "working"}


@app.post("/test-contact")
def test_contact_create(contact: TestContact):
    return {
        "message": "Contact received successfully",
        "data": contact.dict()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)