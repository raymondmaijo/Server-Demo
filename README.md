# Server-Demo

How to Run It
Open your terminal, navigate to the folder where you saved the file, and run:

Bash
python server.py
(Note: Depending on your system, you might need to use python3 server.py).

You will see Server is running at http://localhost:3000 in your terminal. Keep this terminal window open.

How to Call it From curl
Open a new terminal window and run these commands to test your endpoints:

Test Endpoint 1 (/status):

Bash
curl http://localhost:3000/status
Expected Output: {"status": "OK", "uptime": 3.14}

Test Endpoint 2 (/api/data):

Bash
curl http://localhost:3000/api/data
Expected Output: {"message": "Hello from the backend!", "items": [1, 2, 3]}

Test a 404 route:

Bash
curl http://localhost:3000/does-not-exist
Expected Output: {"error": "Not Found"}

4. How to Call it From Your Browser
Because these are simple GET endpoints, you can view them directly in any web browser just like the others:

Open your browser.

Type http://localhost:3000/status into the address bar and hit Enter.

Type http://localhost:3000/api/data into the address bar and hit Enter.
