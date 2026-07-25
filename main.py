from fastapi import FastAPI
import uvicorn

app = FastAPI()

tasks = [
    {"id": 1, "title": "Study", "done": False},
    {"id": 2, "title": "Do Laundry", "done": True},
    {"id": 3, "title": "Watch a movie", "done": False}
]

@app.get("/")
def read_root():
    return {"status": "FastAPI is running on port 8000"}

@app.get("/info")
def info():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def showall():
    return tasks

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)