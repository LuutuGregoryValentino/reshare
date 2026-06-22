
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import os, json
from app.services.session import manager #importing the class instance so that the class members are shared ny all the independent module files

app = FastAPI()

FRONTEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/static/index.html"))

@app.get("/")
async def get_homepage():
    return FileResponse(FRONTEND_PATH)



@app.websocket("/ws/{device_ID}")
async def websocket_endpoint(websocket: WebSocket, device_ID: str ):
    try:
        device_id = device_ID.lower()
        
        await manager.accept_device(device_id, websocket) #adds the device to the global active connections dict in ram
        # print("manager is accepting the device")

    
        while True: #infinite loop that keeps the connection live 
            data = await websocket.receive_json()
            print(f"Received: {data["type"]}\t from Device {device_id}\n")

            packet_type = data.get("type")
            target_raw = data.get("target_id")

            if not target_raw:
                print("Recieving packet missing 'target_id'. Ignoring!!")
                continue

            target_id = target_raw.lower()

            if packet_type == "metadata":
                filename = data.get("filename")
                size = data.get("file_size")

                print(f"""
Media MetaData
From      :  {device_id}
To        :  {target_id}
File Name :  {filename}
Size      :  {size} MB                 
""")
                await manager.send_target_message(
                        message = data,
                        target_device_id = target_id
                    )
                
            elif packet_type == "chat":
                print(f"Chat from {device_id} to {target_id}")
                await manager.send_target_message(
                    message=data,
                    target_device_id=target_id,
                )

    except WebSocketDisconnect: #wehn user closes tab or losses netwrok
        manager.remove_device(device_id)
        print("Device {device_id} has disconnected gracefully")

    except Exception as e: # catches unexpected errors without crashing server
        manager.remove_device(device_id)
        print(f"Unexcpected network glitch on Device {device_id}: {e}")
    