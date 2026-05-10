from fastapi import FastAPI, UploadFile, Request
from fastapi.testclient import TestClient
import io

app = FastAPI()

@app.post("/upload")
def upload(file: UploadFile):
    return {"size": file.size}

client = TestClient(app)

def test_size():
    # Simulate a file upload
    file_content = b"x" * 1000
    response = client.post("/upload", files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")})
    print(response.json())

if __name__ == "__main__":
    test_size()
