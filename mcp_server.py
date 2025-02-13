import asyncio
import logging
import subprocess
from typing import List
import websockets
from mcp_protocol import MCPMessage
import json


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mcp_server.log'
)
logger = logging.getLogger('mcp_server')

class CommandExecutor:
    BLOCKED_COMMANDS = {'sudo', 'rm -rf', 'mkfs', 'dd', 'format'}
    
    @staticmethod
    def is_safe_command(command: str) -> bool:
        command_lower = command.lower()
        return not any(blocked in command_lower for blocked in CommandExecutor.BLOCKED_COMMANDS)
    
    @staticmethod
    async def execute_command(command: str) -> str:
        if not CommandExecutor.is_safe_command(command):
            return "Error: Command contains blocked operations"
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode()
            else:
                return f"Error: {stderr.decode()}"
        except Exception as e:
            return f"Error executing command: {str(e)}"

class MCPServer:
    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.command_executor = CommandExecutor()
        self.active_connections: List[websockets.WebSocketServerProtocol] = []

    async def handle_connection(self, websocket: websockets.WebSocketServerProtocol):
        self.active_connections.append(websocket)
        try:
            async for message in websocket:
                try:
                    mcp_message = MCPMessage.from_json(message)
                    logger.info(f"Received message: {mcp_message.message_type}")
                    
                    if mcp_message.message_type == "command":
                        result = await self.command_executor.execute_command(mcp_message.content)
                        response = MCPMessage(
                            message_type="result",
                            content=result,
                            metadata={"command_id": mcp_message.message_id}
                        )
                        await websocket.send(response.to_json())
                        
                        logger.info(f"Executed command: {mcp_message.content}")
                        logger.info(f"Result: {result}")
                
                except json.JSONDecodeError:
                    logger.error("Invalid message format")
                    continue
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        finally:
            self.active_connections.remove(websocket)

    async def start(self):
        async with websockets.serve(self.handle_connection, self.host, self.port):
            logger.info(f"Server started on ws://{self.host}:{self.port}")
            await asyncio.Future()  

if __name__ == "__main__":
    server = MCPServer()
    asyncio.run(server.start())