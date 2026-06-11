# cloud-society-ai-backend
these are the instructions for the backend.


Part 1: Launch an EC2 Instance

In AWS Learner Lab, open the AWS Console.

Go to:

EC2 → Instances → Launch instance

Use these settings:

Setting	Value
Name	ai-server
AMI	Ubuntu Server 24.04 or 22.04
Instance type	t3.medium or t3.small
Key pair	Create or select one
Storage	20–30 GB

For Security Group, allow:

Type	Port	Source
SSH	22	My IP
Custom TCP	8000	Anywhere
Custom TCP	11434	My IP or Anywhere for testing only

Launch the instance.

Part 2: SSH Into EC2

From your terminal:

ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

If needed:

chmod 400 your-key.pem

Part 3: Install Updates

sudo apt update

sudo apt upgrade -y

Part 4: Install Python Tools

sudo apt install python3-pip python3-venv curl -y

Part 5: Install Ollama

curl -fsSL https://ollama.com/install.sh | sh

Check that it installed:

ollama --version
Part 6: Download a Small AI Model

Use a small model so it can run cheaply on CPU.

ollama pull phi3:mini

Test it:

ollama run phi3:mini

Ask it something like:

Explain AWS S3 in one sentence.

Exit the model chat with:

/bye
Part 7: Create the FastAPI App

Create a project folder:

mkdir ai-server
cd ai-server

Create a Python virtual environment:

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install fastapi uvicorn requests

Create the app file:

nano main.py

Paste this:

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {"message": "AI server is running"}

@app.post("/chat")
def chat(request: ChatRequest):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3:mini",
            "prompt": request.prompt,
            "stream": False
        }
    )

    data = response.json()

    return {
        "response": data.get("response", "No response generated")
    }

Save and exit:

CTRL + O
Enter
CTRL + X
Part 8: Run the API Server
uvicorn main:app --host 0.0.0.0 --port 8000

Leave this running.

Open in your browser:

http://YOUR_EC2_PUBLIC_IP:8000

You should see:

{"message":"AI server is running"}
Part 9: Test the Chat Endpoint

Open a second terminal and SSH into the server again, or use your local terminal:

curl -X POST http://YOUR_EC2_PUBLIC_IP:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain cloud computing in one sentence."}'

You should get an AI-generated response.

Part 10: Update the Static Website

In your S3 website’s index.html, use this simple frontend:

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Simple AWS AI App</title>
</head>
<body>
  <h1>Simple AWS AI App</h1>

  <textarea id="prompt" rows="5" cols="50" placeholder="Ask the AI something..."></textarea>
  <br />

  <button onclick="sendPrompt()">Send</button>

  <h2>AI Response:</h2>
  <p id="response">Waiting for prompt...</p>

  <script>
    async function sendPrompt() {
      const prompt = document.getElementById("prompt").value;
      const responseBox = document.getElementById("response");

      responseBox.innerText = "Thinking...";

      const res = await fetch("http://YOUR_EC2_PUBLIC_IP:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt })
      });

      const data = await res.json();
      responseBox.innerText = data.response;
    }
  </script>
</body>
</html>

Replace:

YOUR_EC2_PUBLIC_IP

with your actual EC2 public IP address.

Upload the updated index.html to your S3 bucket.

Part 11: Test the Full App

Open your S3 static website URL.

Type a prompt:

What is AWS EC2?

Click Send.

The flow should be:

S3 Website → EC2 FastAPI Server → Ollama Model → AI Response
Important Note

Because this simple setup uses HTTP instead of HTTPS, browsers may block the request if your S3 website is loaded over HTTPS.

Use the S3 static website endpoint that starts with:

http://

not:

https://

For a real production app, you would later add HTTPS with API Gateway, CloudFront, or a load balancer.

Stop the Server

Press:

CTRL + C
Restart the Server Later

SSH into EC2 again:

cd ai-server
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
