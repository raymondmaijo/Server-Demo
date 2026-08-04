from fastapi import FastAPI, HTTPException, status, Response
from typing import Optional
from pydantic import BaseModel
import uvicorn

# Initialize the application
app = FastAPI(
    title="Task API",
    description="A complete CRUD API for managing tasks.",
    version="1.0"
)

# Stage 2: In-memory database pre-filled with 3 example tasks
tasks = [
    {"id": 1, "title": "Study", "done": False},
    {"id": 2, "title": "Do Laundry", "done": True},
    {"id": 3, "title": "Watch a movie", "done": False}
]

# Pydantic models for request validation
class TaskCreate(BaseModel):
    title: Optional[str] = None #[cite: 1]

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# ==========================================
# STAGE 1: Root and Health Endpoints
# ==========================================

@app.get("/", summary="Root Information")
def read_root():
    """Returns basic information about the API."""
    # We use the root to return the API description as requested in Stage 1
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health Check")
def health():
    """Checks if the server is alive."""
    return {"status": "ok"} #[cite: 1]

# ==========================================
# STAGE 2: Read (List and Single Task)
# ==========================================

@app.get("/tasks", summary="List Tasks")
def showall():
    """Returns the entire list of tasks."""
    return tasks #[cite: 1]

@app.get("/tasks/{id}", summary="Get Single Task")
def id_show(id: int):
    """Fetches a single task by its path parameter ID."""
    for i in tasks: #[cite: 1]
        if i["id"] == id: #[cite: 1]
            return i #[cite: 1]
    
    # Return 404 if not found with proper machine-readable error
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})

# ==========================================
# STAGE 3: Create (POST a new task)
# ==========================================

@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create Task")
def addpost(task: TaskCreate):
    """Creates a new task and assigns it a unique ID."""
    # Validation: server never trusts the client
    if not task.title or not task.title.strip(): #[cite: 1]
        raise HTTPException(status_code=400, detail="Title is missing or empty")
    
    new_id = max(t["id"] for t in tasks) + 1 #[cite: 1]
    
    newtask = {
        "id": new_id,
        "title": task.title.strip(),
        "done": False #[cite: 1]
    }
    tasks.append(newtask) #[cite: 1]
    return newtask #[cite: 1]
@app.put("/tasks/{id}", summary="Update Task")
def update_task(id: int, task_update: TaskUpdate):
    """Updates an existing task's title and/or completion status."""
    # Validate that at least one field was provided
    if task_update.title is None and task_update.done is None:
        raise HTTPException(status_code=400, detail="Empty or invalid body")

    for task in tasks:
        if task["id"] == id:
            if task_update.title is not None:
                if not task_update.title.strip():
                    raise HTTPException(status_code=400, detail="Title cannot be empty")
                task["title"] = task_update.title.strip()
            if task_update.done is not None:
                task["done"] = task_update.done
            return task
            
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_task(id: int):
    """Removes a task from the list completely."""
    for i, task in enumerate(tasks):
        if task["id"] == id:
            del tasks[i]
            # 204 No Content needs an empty Response body
            return Response(status_code=status.HTTP_204_NO_CONTENT)
            
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) #[cite: 1]