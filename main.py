from fastapi import FastAPI, HTTPException, status, Response
from typing import Optional
from pydantic import BaseModel
from contextlib import asynccontextmanager
import sqlite3
import uvicorn

# ==========================================
# DATABASE HELPER FUNCTIONS
# ==========================================

def dict_factory(cursor, row):
    """Converts SQLite rows into Python dictionaries, mapping 0/1 to False/True."""
    d = {}
    for idx, col in enumerate(cursor.description):
        if col[0] == "done":
            d[col[0]] = bool(row[idx])
        else:
            d[col[0]] = row[idx]
    return d

def get_db():
    """Helper function to get a database connection."""
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = dict_factory
    return conn

# ==========================================
# APP STARTUP (LIFESPAN)
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs exactly once when the application starts up."""
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    
    # Create the table if it doesn't already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    # Check if empty, and insert example tasks only if it is
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [("Study", 0), ("Do Laundry", 1), ("Watch a movie", 0)]
        )
        conn.commit()
    conn.close()
    
    yield # App runs here

# ==========================================
# APP INITIALIZATION & MODELS
# ==========================================

app = FastAPI(
    title="Task API",
    description="A complete CRUD API for managing tasks with a SQLite Database.",
    version="1.0",
    lifespan=lifespan
)

class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/", summary="Root Information")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health Check")
def health():
    return {"status": "ok"}

@app.get("/tasks", summary="List Tasks")
def showall():
    """Returns the entire list of tasks from the database."""
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return tasks

@app.get("/tasks/{id}", summary="Get Single Task")
def id_show(id: int):
    """Fetches a single task by its path parameter ID from the database."""
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if task is None:
        raise HTTPException(status_code=404, detail={"error": "Task not found"})
    return task

@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create Task")
def addpost(task: TaskCreate):
    """Creates a new task and saves it to the SQLite database."""
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is missing or empty")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)", 
        (task.title.strip(), 0)
    )
    conn.commit()
    new_id = cursor.lastrowid
    
    new_task = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    
    return new_task

@app.put("/tasks/{id}", summary="Update Task")
def update_task(id: int, task_update: TaskUpdate):
    """Updates an existing task in the database."""
    if task_update.title is None and task_update.done is None:
        raise HTTPException(status_code=400, detail="Empty or invalid body")

    conn = get_db()
    existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail={"error": "Task not found"})
    
    new_title = task_update.title.strip() if task_update.title is not None else existing["title"]
    if task_update.title is not None and not new_title:
        conn.close()
        raise HTTPException(status_code=400, detail="Title cannot be empty")
        
    new_done = task_update.done if task_update.done is not None else existing["done"]
    
    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?", 
        (new_title, new_done, id)
    )
    conn.commit()
    updated_task = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    return updated_task

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_task(id: int):
    """Deletes a task from the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail={"error": "Task not found"})
        
    conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)