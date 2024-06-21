from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from PyPDF2 import PdfReader
import os

app = FastAPI()

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")
    
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    process_pdf(file_location)
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

def process_pdf(filepath):
    with open(filepath, 'rb') as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        print(f'Total pages: {num_pages}')
        # Add more processing as needed

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
        </body>
    </html>
    """
    return HTMLResponse(content=content)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
