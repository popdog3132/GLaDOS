# GLaDOS Voice Agent

This repository provides a minimal voice assistant that bridges Twilio Media Streams with the OpenAI realtime API. Point a Twilio phone number at it and speak with GPT‑4o in real time.

## Prerequisites
* Python 3.9+
* Twilio account and a voice‑capable phone number
* OpenAI API key with realtime access
* `ngrok` for local development

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set OPENAI_API_KEY, PORT and SERVER_HOST
```

## Running
Start the FastAPI server:
```bash
uvicorn main:app --port 5050
```
Expose the port with ngrok in a separate terminal:
```bash
ngrok http 5050
```
Set `SERVER_HOST` in your `.env` to the publicly reachable hostname (for
example your ngrok subdomain). Configure your Twilio number to send webhooks for incoming calls to `https://<ngrok-subdomain>.ngrok.app/incoming-call`.

Dial the number and chat with the assistant.
