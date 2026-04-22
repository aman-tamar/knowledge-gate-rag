from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import shutil
import os
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.rag.final_pipeline import run_pipeline


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str


@app.post("/ask")
def ask_question(query: Query):

    def generate():
        answer = run_pipeline(query.question)

        
        for word in answer.split():
            yield word + " "

    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs("data", exist_ok=True)

    file_path = f"data/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    from app.kg.pdf_to_kg import process_pdf
    process_pdf(file_path)

    return {"status": "PDF processed successfully"}