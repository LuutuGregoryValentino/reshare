
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import os

from app.services.session import manager #importing the class instance so that the class members are shared ny all the independent module files

app = FastAPI()

FRONTEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../frontend/static/index.html"))

@app.get("/")
async def get_homepage():
    return FileResponse(FRONTEND_PATH)



@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_ID: str ):
    device_id = device_ID.lower()
    
    await manager.accept_device(device_id, websocket) #adds the device to the global active connections dict in ram

    try:
        while True: #infinite loop that keeps the connection live 
            data = await websocket.receive_text()
            print(f"Received: {data}\t from Device {device_id}\n")

            if data.startswith("TARGET"): #chekc if incoming message follows format  "TARGET:Reciever:Message"
                try:
                    _ , target_ID, message_content = data.split(':', 2)
                    target_id = target_ID.lower()

                    success = await manager.send_target_messages(
                        message = f"From {device_id}: {message_content}",
                        target_device_id = target_id
                    )

                    if not success:
                        await websocket.send_text(f"Hub system: {target_id} is currently offline")

                except ValueError: # for when the message dosnt follow the correct format eg. "TARGET:gregs_phone"
                    await websocket.send_text(f'HUB ERROR: Format must be "TARGET:receiving:message')

            else:
                await websocket.send_text(f"Hub heard {device_id} say: {data}")


    except WebSocketDisconnect: #wehn user closes tab or losses netwrok
        manager.remove_device(device_id)
        print("Device {device_id} has disconnected gracefully")

    except Exception as e: # catches unexpected errors without crashing server
        manager.remove_device(device_id)
        print(f"Unexcpected network glitch on Device {device_id}: {e}")
    