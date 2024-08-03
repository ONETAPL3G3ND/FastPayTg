from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from RequestsHandler import RequestsHandler

app = FastAPI()
requests_handler = RequestsHandler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConfirmationRequest(BaseModel):
    id: str

@app.post("/confirmation")
def confirmation(confirmation_data: ConfirmationRequest) -> dict:
    requests_handler.confirmation(confirmation_data.id)
    return {"success": True}