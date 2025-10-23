"""
MCP Server for FlowAgent - Model Context Protocol implementation
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

import websockets
from websockets.server import WebSocketServerProtocol
import structlog

logger = structlog.get_logger()

@dataclass
class MCPMessage:
    """MCP Message structure"""
    id: str
    type: str
    source: str
    destination: Optional[str]
    data: Dict[str, Any]
    timestamp: str
    correlation_id: Optional[str] = None

class MCPServer:
    """MCP Server for agent communication"""
    
    def __init__(self, host: str = "localhost", port: int = 8001):
        self.host = host
        self.port = port
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        
    async def start(self):
        """Start the MCP server"""
        logger.info("Starting MCP Server", host=self.host, port=self.port)
        
        self.is_running = True
        
        # Start message processing loop
        asyncio.create_task(self._message_processing_loop())
        
        # Start WebSocket server
        async with websockets.serve(
            self._handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        ):
            logger.info("MCP Server started successfully")
            await asyncio.Future()  # Run forever
    
    async def stop(self):
        """Stop the MCP server"""
        logger.info("Stopping MCP Server")
        self.is_running = False
        
        # Close all client connections
        for client_id, websocket in self.clients.items():
            await websocket.close()
        
        self.clients.clear()
        logger.info("MCP Server stopped")
    
    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new client connection"""
        client_id = f"client_{len(self.clients) + 1}_{datetime.now().strftime('%H%M%S')}"
        
        logger.info("New client connected", client_id=client_id)
        self.clients[client_id] = websocket
        
        try:
            async for message in websocket:
                await self._process_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected", client_id=client_id)
        except Exception as e:
            logger.error("Error handling client", client_id=client_id, error=str(e))
        finally:
            self.clients.pop(client_id, None)
    
    async def _process_message(self, client_id: str, message: str):
        """Process incoming message from client"""
        try:
            message_data = json.loads(message)
            mcp_message = MCPMessage(
                id=message_data.get("id", f"msg_{datetime.now().strftime('%H%M%S%f')}"),
                type=message_data.get("type", "unknown"),
                source=client_id,
                destination=message_data.get("destination"),
                data=message_data.get("data", {}),
                timestamp=message_data.get("timestamp", datetime.now().isoformat()),
                correlation_id=message_data.get("correlation_id")
            )
            
            logger.info("Processing MCP message", 
                       message_id=mcp_message.id,
                       type=mcp_message.type,
                       source=mcp_message.source)
            
            # Add to message queue for processing
            await self.message_queue.put(mcp_message)
            
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON message", client_id=client_id, error=str(e))
        except Exception as e:
            logger.error("Error processing message", client_id=client_id, error=str(e))
    
    async def _message_processing_loop(self):
        """Main message processing loop"""
        while self.is_running:
            try:
                # Get message from queue
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Process message based on type
                await self._route_message(message)
                
            except asyncio.TimeoutError:
                # No messages in queue, continue
                continue
            except Exception as e:
                logger.error("Error in message processing loop", error=str(e))
                await asyncio.sleep(1)
    
    async def _route_message(self, message: MCPMessage):
        """Route message to appropriate handler"""
        handler = self.message_handlers.get(message.type)
        
        if handler:
            try:
                await handler(message)
            except Exception as e:
                logger.error("Error in message handler", 
                           message_type=message.type, 
                           error=str(e))
        else:
            # Default message handling
            await self._default_message_handler(message)
    
    async def _default_message_handler(self, message: MCPMessage):
        """Default message handler"""
        logger.info("Processing message with default handler", 
                   message_type=message.type,
                   source=message.source)
        
        # Route to destination if specified
        if message.destination and message.destination in self.clients:
            await self._send_to_client(message.destination, message)
        else:
            # Broadcast to all clients
            await self._broadcast_message(message)
    
    async def _send_to_client(self, client_id: str, message: MCPMessage):
        """Send message to specific client"""
        if client_id in self.clients:
            try:
                await self.clients[client_id].send(json.dumps({
                    "id": message.id,
                    "type": message.type,
                    "source": message.source,
                    "data": message.data,
                    "timestamp": message.timestamp,
                    "correlation_id": message.correlation_id
                }))
                
                logger.info("Message sent to client", 
                           client_id=client_id,
                           message_id=message.id)
                           
            except Exception as e:
                logger.error("Error sending message to client", 
                           client_id=client_id, 
                           error=str(e))
                # Remove disconnected client
                self.clients.pop(client_id, None)
    
    async def _broadcast_message(self, message: MCPMessage):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
        
        message_json = json.dumps({
            "id": message.id,
            "type": message.type,
            "source": message.source,
            "data": message.data,
            "timestamp": message.timestamp,
            "correlation_id": message.correlation_id
        })
        
        # Send to all clients concurrently
        tasks = []
        for client_id, websocket in self.clients.items():
            if client_id != message.source:  # Don't send back to sender
                tasks.append(self._send_to_client(client_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler for specific message type"""
        self.message_handlers[message_type] = handler
        logger.info("Registered message handler", message_type=message_type)
    
    async def send_message(self, message_type: str, data: Dict[str, Any], 
                          destination: Optional[str] = None, 
                          correlation_id: Optional[str] = None) -> str:
        """Send a message through the MCP server"""
        message_id = f"msg_{datetime.now().strftime('%H%M%S%f')}"
        
        message = MCPMessage(
            id=message_id,
            type=message_type,
            source="mcp_server",
            destination=destination,
            data=data,
            timestamp=datetime.now().isoformat(),
            correlation_id=correlation_id
        )
        
        if destination:
            await self._send_to_client(destination, message)
        else:
            await self._broadcast_message(message)
        
        return message_id
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get MCP server status"""
        return {
            "status": "running" if self.is_running else "stopped",
            "host": self.host,
            "port": self.port,
            "connected_clients": len(self.clients),
            "client_ids": list(self.clients.keys()),
            "message_handlers": list(self.message_handlers.keys()),
            "queued_messages": self.message_queue.qsize(),
            "uptime": datetime.now().isoformat()
        }

# Agent-specific message handlers
class AgentMessageHandlers:
    """Message handlers for agent communication"""
    
    def __init__(self, mcp_server: MCPServer):
        self.mcp_server = mcp_server
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all agent message handlers"""
        self.mcp_server.register_handler("workflow_request", self._handle_workflow_request)
        self.mcp_server.register_handler("task_execution", self._handle_task_execution)
        self.mcp_server.register_handler("alert", self._handle_alert)
        self.mcp_server.register_handler("event", self._handle_event)
        self.mcp_server.register_handler("execution_result", self._handle_execution_result)
        self.mcp_server.register_handler("agent_status", self._handle_agent_status)
    
    async def _handle_workflow_request(self, message: MCPMessage):
        """Handle workflow creation request"""
        logger.info("Handling workflow request", 
                   source=message.source,
                   workflow_id=message.data.get("workflow_id"))
        
        # Route to planner agent
        await self.mcp_server.send_message(
            "plan_workflow",
            message.data,
            destination="planner_agent"
        )
    
    async def _handle_task_execution(self, message: MCPMessage):
        """Handle task execution request"""
        logger.info("Handling task execution", 
                   source=message.source,
                   task_id=message.data.get("task_id"))
        
        # Route to executor agent
        await self.mcp_server.send_message(
            "execute_task",
            message.data,
            destination="executor_agent"
        )
    
    async def _handle_alert(self, message: MCPMessage):
        """Handle alert message"""
        logger.warning("Handling alert", 
                      source=message.source,
                      alert_type=message.data.get("type"))
        
        # Broadcast alert to all agents
        await self.mcp_server.send_message(
            "alert_notification",
            message.data
        )
    
    async def _handle_event(self, message: MCPMessage):
        """Handle event message"""
        logger.info("Handling event", 
                   source=message.source,
                   event_type=message.data.get("type"))
        
        # Route to appropriate agents based on event type
        event_type = message.data.get("type")
        
        if event_type in ["system_health", "performance_issue"]:
            # Route to planner for workflow adjustments
            await self.mcp_server.send_message(
                "system_event",
                message.data,
                destination="planner_agent"
            )
        elif event_type in ["task_completion", "workflow_progress"]:
            # Route to observer for monitoring updates
            await self.mcp_server.send_message(
                "progress_update",
                message.data,
                destination="observer_agent"
            )
    
    async def _handle_execution_result(self, message: MCPMessage):
        """Handle execution result"""
        logger.info("Handling execution result", 
                   source=message.source,
                   execution_id=message.data.get("execution_id"))
        
        # Route to observer for monitoring
        await self.mcp_server.send_message(
            "execution_complete",
            message.data,
            destination="observer_agent"
        )
    
    async def _handle_agent_status(self, message: MCPMessage):
        """Handle agent status update"""
        logger.info("Handling agent status", 
                   source=message.source,
                   agent_type=message.data.get("agent_type"))
        
        # Store agent status (could be stored in Redis)
        # For now, just log it
        pass

async def main():
    """Main function to start MCP server"""
    server = MCPServer()
    
    # Register agent message handlers
    handlers = AgentMessageHandlers(server)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down MCP server...")
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
