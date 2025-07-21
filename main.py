import os
import json
import asyncio
import base64
import websockets
from fastapi import FastAPI, WebSocket, Request
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VOICE = "alloy"
MODEL_WS = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"

app = FastAPI()

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def incoming(request: Request):
    """Return TwiML directing Twilio to open a media stream."""
    resp = VoiceResponse()
    resp.say("Connecting you to the AI assistant.")
    connect = Connect()
    connect.stream(url=f"wss://{request.url.hostname}/media-stream")
    resp.append(connect)
    return resp.to_xml()

@app.websocket("/media-stream")
async def media_stream(ws: WebSocket):
    """Bridge audio between Twilio and OpenAI realtime."""
    await ws.accept()
    async with websockets.connect(
        MODEL_WS,
        extra_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1",
        },
    ) as openai_ws:
        await openai_ws.send(
            json.dumps(
                {
                    "type": "session.update",
                    "session": {
                        "input_audio_format": "g711_ulaw",
                        "output_audio_format": "g711_ulaw",
                        "voice": VOICE,
                        "instructions": "You are a helpful, upbeat golf-course assistant.",
                        "modalities": ["text", "audio"],
                    },
                }
            )
        )

        async def twilio_in():
            async for msg in ws.iter_text():
                data = json.loads(msg)
                if data.get("event") == "media":
                    await openai_ws.send(
                        json.dumps(
                            {
                                "type": "input_audio_buffer.append",
                                "audio": data["media"]["payload"],
                            }
                        )
                    )

        async def twilio_out():
            async for reply in openai_ws:
                r = json.loads(reply)
                if r.get("type") == "response.audio.delta":
                    await ws.send_json(
                        {
                            "event": "media",
                            "streamSid": "",
                            "media": {"payload": r["delta"]},
                        }
                    )

        await asyncio.gather(twilio_in(), twilio_out())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5050)))
