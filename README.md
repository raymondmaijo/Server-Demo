# FastAPI Task Manager with SQLite

A complete CRUD API for managing tasks, built with Python, FastAPI, and a SQLite database. 

## Why SQLite?
SQLite was chosen for this project because it is a lightweight, serverless database engine that requires no external setup or background processes. It stores the entire database in a single standard file on the disk, making it perfect for local development, testing, and small-to-medium scale applications. 

## Where is the database stored?
The database is stored locally in the root directory of this project in a file named `tasks.db`. 

*Note: You do not need to create this file manually. The application uses a FastAPI lifespan event to automatically generate the file, create the `tasks` table, and populate it with seed data the very first time you start the server!*

## How to Start the Project

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd <your-repository-folder>