import re
import uvicorn
import socketio
from fastapi import FastAPI
from typing import Dict, List
from weaviate_ import setup_weaviate_interface
from openai import OpenAI
import markdown

client = OpenAI()
app = FastAPI()
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)
sessions: Dict[str, List[Dict[str, str]]] = {}

weaviate_interface = None


@app.on_event("startup")
async def app_startup():
    global weaviate_interface
    weaviate_interface = await setup_weaviate_interface()


def generate_response(user_message: str, context: str = None) -> str:
    with open(
        "/Users/adakibet/cosmology/platform/trial/team-mate3/weaviate_/context.txt", "r"
    ) as file:
        file_contents = file.read()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "system",
                "content": f"""
                {file_contents}
                {context}
                """,
            },
            {"role": "user", "content": user_message},
        ],
    )
    print(f"OpenAI response: {response}")
    return response.choices[0].message.content


@app.get("/")
def read_root():
    return {"Hello": "World"}


@sio.on("connect")
async def connect(sid, env):
    print("New Client Connected to This id :" + " " + str(sid))


@sio.on("disconnect")
async def disconnect(sid):
    print("Client Disconnected: " + " " + str(sid))


@sio.on("connectionInit")
async def handle_connection_init(sid):
    await sio.emit("connectionAck", room=sid)


@sio.on("sessionInit")
async def handle_session_init(sid, data):
    print(f"===> Session {sid} initialized")
    session_id = data.get("sessionId")
    if session_id not in sessions:
        sessions[session_id] = []
    print(
        f"""
        **** Session {session_id} initialized for
        {sid} session data: {sessions[session_id]}
        """
    )
    await sio.emit(
        "sessionInit",
        {"sessionId": session_id, "chatHistory": sessions[session_id]},
        room=sid,
    )


@sio.on("textMessage")
async def handle_chat_message(sid, data):
    print(f"Message from {sid}: {data}")
    session_id = data.get("sessionId")
    message_type = data.get("type")

    if session_id:
        received_message = {}
        print("message type", message_type)
        if message_type == "textMessage":
            received_message = {
                "id": data.get("id"),
                "message": data.get("message"),
                "isUserMessage": True,
                "timestamp": data.get("timestamp"),
            }

        elif message_type == "audioData":
            audio_data = data.get("audioData")

            transcription_response = client.audio.transcriptions.create(
                model="whisper-1", file=audio_data, response_format="text"
            )
            transcribed_text = transcription_response.text
            print("this is the transcribed_text", transcribed_text)

            received_message = {
                "id": data.get("id"),
                "message": transcribed_text,
                "isUserMessage": True,
                "timestamp": data.get("timestamp"),
            }
            context = None

        sessions[session_id].append(received_message)

        search_results = await weaviate_interface.client.semantic_search(
            class_name="JobPosting",
            query=received_message["message"],
            fields=["title", "company"],
            limit=5,
        )
        context = search_results
        print("context", context)

        openai_response = generate_response(
            user_message=data.get("message"), context=context
        )

        # Format the response
        if re.search(
            r"^(\d+\.|\*\s+)", openai_response, re.MULTILINE
        ):  # Check for lists
            formatted_response = (
                f"<ul><li>{openai_response.replace(
                    '\n', '</li><li>')}</li></ul>"
            )
        elif re.search(
            r"^(```|~~~)", openai_response, re.MULTILINE
        ):  # Code blocks (fenced or indented)
            formatted_response = (
                f"<pre><code>{openai_response.replace("```", "")}</code></pre>"
            )
        else:
            formatted_response = markdown.markdown(
                openai_response
            )  # Convert to Markdown

        response_message = {
            "id": data.get("id") + "_response",
            "textResponse": formatted_response,  # Send formatted response
            "isUserMessage": False,
            "timestamp": data.get("timestamp"),
            "isComplete": True,
        }

        await sio.emit("textResponse", response_message, room=sid)
        sessions[session_id].append(response_message)

        print(f"Message from {sid} in session {session_id}: {data.get('message')}")

    else:
        print(f"No session ID provided by {sid}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=6789,
        lifespan="on",
        reload=True
    )
