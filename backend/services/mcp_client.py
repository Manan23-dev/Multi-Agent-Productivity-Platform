"""
MCP Client for agent communication
"""

import asyncio
import json
import websockets
from typing import Dict, Any, Optional, Callable
import structlog

logger = structlog.get_logger()

class MCPClient:
    """MCP Client for communicating with MCP Server"""
    
    def __init__(self, host: str = "localhost", port: int = 8001, protocol: str = "ws"):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_messages: Dict[str, asyncio.Future] = {}
        
    async def connect(self):
        """Connect to MCP server"""
        try:
            url = f"{self.protocol}://{self.host}:{self.port}"
            self.websocket = await websockets.connect(url)
            self.is_connected = True
            
            # Start message handling loop
            asyncio.create_task(self._message_loop())
            
            logger.info("MCP Client connected", url=url)
            
        except Exception as e:
            logger.error("Failed to connect to MCP server", error=str(e))
            raise
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        self.is_connected = False
        if self.websocket:
            await self.websocket.close()
        logger.info("MCP Client disconnected")
    
    async def _message_loop(self):
        """Handle incoming messages"""
        try:
            async for message in self.websocket:
                await self._process_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("MCP connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error("Error in message loop", error=str(e))
    
    async def _process_message(self, message: str):
        """Process incoming message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            message_id = data.get("id")
            
            # Handle response to pending message
            if message_id in self.pending_messages:
                future = self.pending_messages.pop(message_id)
                future.set_result(data)
                return
            
            # Handle message with registered handler
            handler = self.message_handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                logger.info("No handler for message type", message_type=message_type)
                
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON message", error=str(e))
        except Exception as e:
            logger.error("Error processing message", error=str(e))
    
    async def send_message(self, message_type: str, data: Dict[str, Any], 
                          destination: Optional[str] = None,
                          wait_for_response: bool = False) -> Optional[Dict[str, Any]]:
        """Send message to MCP server"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MCP server")
        
        message_id = f"msg_{asyncio.get_event_loop().time()}"
        message = {
            "id": message_id,
            "type": message_type,
            "source": "client",
            "destination": destination,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if wait_for_response:
            future = asyncio.Future()
            self.pending_messages[message_id] = future
        
        await self.websocket.send(json.dumps(message))
        
        if wait_for_response:
            try:
                response = await asyncio.wait_for(future, timeout=30.0)
                return response
            except asyncio.TimeoutError:
                self.pending_messages.pop(message_id, None)
                raise TimeoutError("No response received")
        
        return None
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler"""
        self.message_handlers[message_type] = handler
        logger.info("Registered message handler", message_type=message_type)
    
    async def ping(self) -> bool:
        """Send ping to server"""
        try:
            response = await self.send_message("ping", {}, wait_for_response=True)
            return response is not None
        except Exception as e:
            logger.error("Ping failed", error=str(e))
            return False
