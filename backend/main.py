from fastapi import FastAPI, File, UploadFile, HTTPException,Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from ingest import create_vectore_store
from PyPDF2 import PdfReader
import os
import uuid
import io
app = FastAPI()

sessions = {}
engines={}


UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")
    
    session_id = str(uuid.uuid4())
    content = await file.read()
    pdf_reader = PdfReader(io.BytesIO(content))
    document = ""
    for page in pdf_reader.pages:
        document += page.extract_text()
    
    index = await create_vectore_store(document=document,sessionId=session_id)
    sessions[session_id] = index

    return {"info": f"file '{file.filename}' saved at '{session_id}'"}

@app.post("/ask_question/")
async def ask_question(session_id: str = Form(...), question: str = Form(...)):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    index = sessions[session_id]
    if session_id not in engines:

        query_engine = await index.as_query_engine(response_mode="compact")
        engines[session_id] = query_engine
    else:
        query_engine = engines[session_id]

    response = await query_engine.query("summarize the given content?")

    return {"answer": response}
    
@app.get("/", response_class=HTMLResponse)
async def main():
    content = """
<html>
        <head>
            <title>Upload PDF</title>
        </head>
        <body>
            <h1>Upload a PDF</h1>
            <form action="/uploadfile/" enctype="multipart/form-data" method="post">
                <input name="file" type="file">
                <input type="submit">
            </form>
            <h2>Ask a Question</h2>
            <form action="/ask_question/" method="post">
                <label for="session_id">Session ID:</label>
                <input type="text" id="session_id" name="session_id"><br><br>
                <label for="question">Question:</label>
                <input type="text" id="question" name="question"><br><br>
                <input type="submit">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=content)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
