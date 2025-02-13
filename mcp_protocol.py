from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
import uuid
import time

@dataclass
class MCPMessage:
    message_type: str 
    content: str
    metadata: Dict[str, Any]
    message_id: str = None
    timestamp: float = None
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()
    
    def to_json(self) -> str:
        return json.dumps({
            "message_type": self.message_type,
            "content": self.content,
            "metadata": self.metadata,
            "message_id": self.message_id,
            "timestamp": self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        data = json.loads(json_str)
        return cls(**data)

def create_query_message(query: str) -> MCPMessage:
    return MCPMessage(
        message_type="query",
        content=query,
        metadata={"source": "client"}
    )

def create_command_message(command: str, query_id: str) -> MCPMessage:
    return MCPMessage(
        message_type="command",
        content=command,
        metadata={"query_id": query_id, "source": "llm"}
    )

def create_result_message(result: str, command_id: str) -> MCPMessage:
    return MCPMessage(
        message_type="result",
        content=result,
        metadata={"command_id": command_id, "source": "server"}
    )