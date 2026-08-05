from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import os, json, asyncio
from app.services.session import manager

app = FastAPI()

FRONTEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/static/index.html"))

@app.get("/")
async def get_homepage():
    return FileResponse(FRONTEND_PATH)

@app.websocket("/ws/{device_ID}")
async def websocket_endpoint(websocket: WebSocket, device_ID: str):
    device_id = device_ID.lower()
    await manager.accept_device(device_id, websocket)

    try:
        while True:
            message = await websocket.receive()

            # 1. CONTROL PLANE (JSON Signals)
            if "text" in message:
                data = json.loads(message["text"])
                packet_type = data.get("type")
                target_raw = data.get("target_id")

                if not target_raw:
                    continue

                target_id = target_raw.lower()

                if packet_type in ["metadata", "request_chunk", "chat"]:
                    print(f"📁 [{packet_type.upper()}] From {device_id} ──> {target_id}")
                    await manager.send_target_message(message=data, target_device_id=target_id)

            # 2. DATA PLANE (2MB Raw Video Slices)
            elif "bytes" in message:
                raw_bytes = message["bytes"]
                # Relay bytes to active target connections while yielding to event loop
                for target_id, conn in list(manager.active_connections.items()):
                    if target_id != device_id:
                        await conn.send_bytes(raw_bytes)
                
                # Crucial: Yield control to FastAPI event loop to allow keepalive pings
                await asyncio.sleep(0.001)

    except WebSocketDisconnect:
        manager.remove_device(device_id)
        print(f"Device {device_id} disconnected gracefully")

    except Exception as e:
        manager.remove_device(device_id)
        print(f"Unexpected network glitch on Device {device_id}: {e}")