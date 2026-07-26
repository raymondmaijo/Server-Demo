from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
import uvicorn

app = FastAPI()

tasks = [
    {"id": 1, "title": "Study", "done": False},
    {"id": 2, "title": "Do Laundry", "done": True},
    {"id": 3, "title": "Watch a movie", "done": False}
]

class TaskCreate(BaseModel):
    title: Optional[str] = None

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

@app.get("/tasks/{id}")
def id_show(id: int):
    f=0
    for i in tasks:
        if i["id"]==id:
            return i
            f=1
    if f==0:
        raise HTTPException(status_code=404, detail={"error": "Task 99 not found"})

@app.post("/tasks", status_code=201)
def addpost(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is missing")
    
    new_id = max(t["id"] for t in tasks) + 1
    
    newtask = {
        "id": new_id,
        "title": task.title.strip(),
        "done": False
    }
    tasks.append(newtask)
    return newtask

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)