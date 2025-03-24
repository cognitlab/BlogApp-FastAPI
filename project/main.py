from fastapi import FastAPI

app = FastAPI()

@app.get("/home")
def home():
    return "Hey I am done"