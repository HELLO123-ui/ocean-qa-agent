from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "QA Agent backend is running"}
