
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def accept_device(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        print(f"Memory Cache updated. Active devices: \n{list(self.active_connections.keys())}")

    def remove_device(self, device_id:str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            print(f"Device {device_id} has been gracefully disconnected\nRemaining Devices: \n{list(self.active_connections.keys())}")

        
    async def send_target_message(self, message: dict, target_device_id: str) -> bool:
        # print(f"🔍 [HOP 3] Dictionary Check. Looking for: '{target_device_id}'. Current memory keys: {list(self.active_connections.keys())}")
        if target_device_id in self.active_connections:
            target_websocket = self.active_connections[target_device_id]

            await target_websocket.send_json(message)
            # print(f"✅ [HOP 4] Bytes successfully pushed to network socket for '{target_id}'")
            return True
        
        print (f"Failed to Route message. target device {target_device_id} is offline")
        # print(f"HOP4, lookup failed. '{target_device_id}' is not in memory")
        return False




manager = ConnectionManager() # creates one global instance of the active connection list in RAM