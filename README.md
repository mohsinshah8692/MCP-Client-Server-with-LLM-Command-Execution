# Machine Command Processor (MCP)

A client-server system that uses LLMs to convert natural language queries into shell commands. The system consists of three main components: a client that processes natural language queries through Groq's LLM API, a server that executes shell commands, and a shared protocol for communication.

## Features

- Natural language to shell command conversion using Groq's LLM API
- WebSocket-based client-server communication
- Command execution safety checks
- Comprehensive logging system
- Asynchronous operation using Python's asyncio
- Structured message protocol with UUID tracking

## Prerequisites

- Python 3.7+
- Groq API key
- WebSocket support
- Required Python packages:
  - websockets
  - groq
  - asyncio
  - logging

## Installation

1. Clone the repository
2. Install required packages:
```bash
pip install websockets groq
```
3. Set up your Groq API key:
```bash
export GROQ_API_KEY='your-api-key'
```

## Components

### MCP Client (`mcp_client.py`)
- Handles user input
- Connects to Groq API for command generation
- Communicates with server via WebSocket
- Processes and displays results

### MCP Server (`mcp_server.py`)
- Executes shell commands
- Implements command safety checks
- Manages WebSocket connections
- Returns command execution results

### Protocol (`mcp_protocol.py`)
- Defines message structure
- Handles message serialization/deserialization
- Provides message creation utilities

## Usage

1. Start the server:
```bash
python mcp_server.py
```

2. In a separate terminal, start the client:
```bash
python mcp_client.py
```

3. Enter natural language queries when prompted. For example:
```
Enter your query: list all files in the current directory
```

## Security Features

- Blocked dangerous commands including:
  - sudo
  - rm -rf
  - mkfs
  - dd
  - format
- Command validation before execution
- Logged operations for audit trails

## Logging

The system maintains two log files:
- `mcp_client.log`: Client-side operations and LLM interactions
- `mcp_server.log`: Server-side operations and command execution



## Contributing

[Add contribution guidelines here]
