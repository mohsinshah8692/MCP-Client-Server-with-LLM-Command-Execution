import asyncio
import logging
from typing import Optional
import websockets
from mcp_protocol import MCPMessage, create_query_message
import os
import groq
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_client.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('mcp_client')

class LLMProcessor:
    def __init__(self, api_key: str, model_name: str = "mixtral-8x7b-32768"):
        self.client = groq.Groq(api_key=api_key)
        self.model_name = model_name
    
    async def generate_command(self, query: str) -> str:
        prompt = f"""
        You are a command generator. Your task is to convert the following request into a shell command.
        Request: {query}
        
        
        Command(s):
        """
        
        try:
            logger.info(f"Sending prompt to Groq: {prompt}")
            completion = self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model=self.model_name,
                temperature=0.1 
            )
            
            command = completion.choices[0].message.content.strip()
            logger.info(f"Received response from Groq: {command}")
            return command
        except Exception as e:
            logger.error(f"Detailed error in LLM processing: {str(e)}")
            raise Exception(f"LLM Error: {str(e)}")

class MCPClient:
    def __init__(self, api_key: str, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.llm_processor = LLMProcessor(api_key)
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
    
    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.server_url)
            logger.info("Connected to MCP server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to server: {str(e)}")
            return False
    
    async def process_query(self, query: str):
        if not self.websocket:
            logger.error("Not connected to server")
            return "Error: Not connected to server"
        
        try:
            commands = await self.llm_processor.generate_command(query)
            if not commands:
                return "Error: No command generated"
            
            results = []
            for command in commands.split('\n'):
                command = command.strip()
                if not command:
                    continue
                
                command_message = MCPMessage(
                    message_type="command",
                    content=command,
                    metadata={"query": query}
                )
                
                logger.info(f"Sending command: {command}")
                await self.websocket.send(command_message.to_json())
                
                result = await self.websocket.recv()
                result_message = MCPMessage.from_json(result)
                results.append(f"Command: {command}\nResult: {result_message.content}")
            
            return "\n\n".join(results)
            
        except Exception as e:
            logger.error(f"Detailed error in processing: {str(e)}")
            return f"Error processing query: {str(e)}"
    
    async def close(self):
        if self.websocket:
            await self.websocket.close()

async def verify_groq(api_key: str):
    try:
        client = groq.Groq(api_key=api_key)
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model="mixtral-8x7b-32768"
        )
        logger.info("Groq API connection verified")
        return True
    except Exception as e:
        logger.error(f"Groq verification failed: {str(e)}")
        return False

async def main():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY='your-api-key'")
        return

    if not await verify_groq(api_key):
        print("Error: Cannot connect to Groq API. Please check your API key and internet connection.")
        return

    client = MCPClient(api_key)
    if await client.connect():
        print("Connected to server. Ready for queries!")
        
        while True:
            try:
                query = input("\nEnter your query (or 'quit' to exit): ")
                if query.lower() == 'quit':
                    break
                
                result = await client.process_query(query)
                print("\nResult:")
                print(result)
            
            except KeyboardInterrupt:
                break
        
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())