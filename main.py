import sqlite3
from fastapi import FastAPI, HTTPException, status, Response
from contextlib import asynccontextmanager
from typing import Optional
from pydantic import BaseModel
import uvicorn

DB_FILE = "tasks.db"

# ==========================================
# DATABASE SETUP & STARTUP LOGIC
# ==========================================

def get_db_connection():
    """Helper function to get a database connection."""
    conn = sqlite3.connect(DB_FILE)
    # This allows us to access columns by name (like dictionaries)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates the table and inserts example data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create the table if it doesn't already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    ''')

    # 2. Check if the table is empty
    cursor.execute('SELECT COUNT(*) FROM tasks')
    task_count = cursor.fetchone()[0]

    # 3. Insert three example tasks ONLY if the table is empty
    if task_count == 0:
        example_tasks = [
            ("Study", False),
            ("Do Laundry", True),
            ("Watch a movie", False)
        ]
        cursor.executemany('''
            INSERT INTO tasks (title, done) 
            VALUES (?, ?)
        ''', example_tasks)
        print("Database initialized: Inserted 3 example tasks.")
    else:
        print(f"Database ready: Found {task_count} existing tasks.")

    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the application starts
    init_db()
    yield
    # Anything after 'yield' runs when the application shuts down

# Initialize the application with the lifespan event
app = FastAPI(
    title="Task API",
    description="A complete CRUD API for managing tasks backed by SQLite.",
    version="1.0",
    lifespan=lifespan
)

# Pydantic models for request validation
class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# ==========================================
# STAGE 1: Root and Health Endpoints
# ==========================================

@app.get("/", summary="Root Information")
def read_root():
    """Returns basic information about the API."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health Check")
def health():
    """Checks if the server is alive."""
    return {"status": "ok"}

@app.get("/tasks", summary="List Tasks")
def showall():
    """Returns the entire list of tasks."""
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    
 
    return [{"id": t["id"], "title": t["title"], "done": bool(t["done"])} for t in tasks]

@app.get("/tasks/{id}", summary="Get Single Task")
def id_show(id: int):
    """Fetches a single task by its path parameter ID."""
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if task is None:
        raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})
        
    return {"id": task["id"], "title": task["title"], "done": bool(task["done"])}


@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create Task")
def addpost(task: TaskCreate):
    """Creates a new task and assigns it a unique ID."""
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is missing or empty")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (title, done) VALUES (?, ?)', (task.title.strip(), False))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return {"id": new_id, "title": task.title.strip(), "done": False}

@app.put("/tasks/{id}", summary="Update Task")
def update_task(id: int, task_update: TaskUpdate):
    """Updates an existing task's title and/or completion status."""
    if task_update.title is None and task_update.done is None:
        raise HTTPException(status_code=400, detail="Empty or invalid body")

    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()
    
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})

    # Determine what to update
    new_title = task["title"]
    if task_update.title is not None:
        new_title = task_update.title.strip()
        if not new_title:
            conn.close()
            raise HTTPException(status_code=400, detail="Title cannot be empty")

    new_done = bool(task["done"])
    if task_update.done is not None:
        new_done = task_update.done

    conn.execute('UPDATE tasks SET title = ?, done = ? WHERE id = ?', (new_title, new_done, id))
    conn.commit()
    conn.close()
    
    return {"id": id, "title": new_title, "done": new_done}

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_task(id: int):
    """Removes a task from the list completely."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})
        
    conn.commit()
    conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)