import asyncio
import websockets
import json
import threading

class ChannelClient:
    def __init__(self):
        self.websocket = None
        self.subscribed_channels = set()
    
    async def connect(self, uri="ws://localhost:8765"):
        """Connect to the WebSocket server"""
        try:
            self.websocket = await websockets.connect(uri)
            print(f"Connected to {uri}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    async def send_user_info(self, username):
        """Send username to server"""
        await self.websocket.send(json.dumps({
            "type": "user_info",
            "username": username
        }))
    
    async def subscribe_to_channel(self, channel):
        """Subscribe to a channel"""
        await self.websocket.send(json.dumps({
            "type": "subscribe",
            "action": "subscribe",
            "channel": channel
        }))
    
    async def unsubscribe_from_channel(self, channel):
        """Unsubscribe from a channel"""
        await self.websocket.send(json.dumps({
            "type": "unsubscribe",
            "action": "unsubscribe",
            "channel": channel
        }))
    
    async def send_message(self, channel, message):
        """Send message to a channel"""
        await self.websocket.send(json.dumps({
            "type": "message",
            "channel": channel,
            "message": message
        }))
    
    async def list_channels(self):
        """Request list of available channels"""
        await self.websocket.send(json.dumps({
            "type": "list_channels"
        }))
    
    async def listen_for_messages(self):
        """Listen for incoming messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_server_message(data)
                except json.JSONDecodeError:
                    # Handle non-JSON messages
                    await self.handle_server_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server")
        except Exception as e:
            print(f"Error listening for messages: {e}")
    
    async def handle_server_message(self, data):
        """Handle different types of messages from server"""
        # If data is already a dict, use it. Otherwise it might be a string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                print(f"Raw message: {data}")
                return
        
        msg_type = data.get("type")
        
        # Handle custom server messages
        if msg_type == "request_info":
            print(f"Server: {data.get('message')}")
        elif msg_type == "channel_list":
            print(f"Server: {data.get('message', '')}")
            channels = data.get('channels', [])
            for i, channel in enumerate(channels, 1):
                print(f"  {i}. #{channel}")
        elif msg_type == "subscription_success":
            channel = data.get('channel')
            self.subscribed_channels.add(channel)
            print(f"✓ {data.get('message')}")
        elif msg_type == "unsubscription_success":
            channel = data.get('channel')
            self.subscribed_channels.discard(channel)
            print(f"✓ {data.get('message')}")
        elif msg_type == "channel_message":
            username = data.get('username')
            channel = data.get('channel')
            message = data.get('message')
            print(f"#{channel} <{username}> {message}")
        elif msg_type == "user_joined":
            print(f"📥 {data.get('message')}")
        elif msg_type == "user_left":
            print(f"📤 {data.get('message')}")
        elif msg_type == "error":
            print(f"❌ Error: {data.get('message')}")
        else:
            # Handle external API messages or unknown formats
            # Pretty print JSON with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {json.dumps(data, indent=2)}")
            
            # Detect common external API patterns
            if data.get('event') == 'subscribed':
                print(f"✓ Subscribed to channel: {data.get('channel', 'unknown')}")
            elif data.get('event') == 'updated' and data.get('channel') == 'heartbeat':
                print("💓 Heartbeat")
            elif data.get('seqnum'):
                print(f"📦 Message #{data.get('seqnum')}")

def get_user_input(client, is_custom_server=True):
    """Handle user input in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    while True:
        try:
            user_input = input().strip()
            if not user_input:
                continue
                
            if user_input.startswith('/'):
                # Handle commands
                parts = user_input.split(' ', 2)
                command = parts[0][1:]  # Remove '/'
                
                if command == 'quit':
                    break
                elif command == 'help':
                    if is_custom_server:
                        print("Custom Server Commands:")
                        print("  /subscribe <channel>  - Subscribe to a channel")
                        print("  /unsubscribe <channel> - Unsubscribe from channel")
                        print("  /channels - List available channels")
                        print("  #<channel> <message> - Send message to channel")
                    else:
                        print("External API Commands:")
                        print("  Send JSON messages directly to interact with the API")
                        print("  Example: {\"channel\": \"heartbeat\", \"event\": \"subscribe\"}")
                    print("  /help - Show this help")
                    print("  /quit - Exit")
                elif is_custom_server:
                    # Custom server commands
                    if command == 'subscribe' and len(parts) > 1:
                        channel = parts[1]
                        asyncio.run_coroutine_threadsafe(
                            client.subscribe_to_channel(channel), 
                            main_loop
                        )
                    elif command == 'unsubscribe' and len(parts) > 1:
                        channel = parts[1]
                        asyncio.run_coroutine_threadsafe(
                            client.unsubscribe_from_channel(channel), 
                            main_loop
                        )
                    elif command == 'channels':
                        asyncio.run_coroutine_threadsafe(
                            client.list_channels(), 
                            main_loop
                        )
                    else:
                        print("Unknown command. Type /help for available commands.")
                else:
                    print("Unknown command. Type /help for available commands.")
            
            elif is_custom_server and user_input.startswith('#'):
                # Send message to channel (custom server only)
                parts = user_input.split(' ', 1)
                if len(parts) > 1:
                    channel = parts[0][1:]  # Remove '#'
                    message = parts[1]
                    asyncio.run_coroutine_threadsafe(
                        client.send_message(channel, message), 
                        main_loop
                    )
                else:
                    print("Usage: #<channel> <message>")
            
            elif not is_custom_server:
                # Raw JSON mode for external APIs
                try:
                    # Try to parse as JSON first
                    json.loads(user_input)
                    # If valid JSON, send it
                    asyncio.run_coroutine_threadsafe(
                        client.websocket.send(user_input), 
                        main_loop
                    )
                except json.JSONDecodeError:
                    print("Invalid JSON. Please send valid JSON messages.")
                    print("Example: {\"channel\": \"heartbeat\", \"event\": \"subscribe\"}")
            
            else:
                if is_custom_server:
                    print("Invalid input. Use /help for commands or #<channel> <message> to send messages.")
                else:
                    print("Send JSON messages to interact with the API, or /help for commands.")
                
        except EOFError:
            break
        except Exception as e:
            print(f"Input error: {e}")

async def main():
    global main_loop
    main_loop = asyncio.get_event_loop()
    
    client = ChannelClient()
    
    # Get server address
    print("WebSocket Channel Client")
    print("=" * 25)
    server_address = input("Enter WebSocket server address (default: ws://localhost:8765): ").strip()
    if not server_address:
        server_address = "ws://localhost:8765"
    
    # Validate and format the address
    if not server_address.startswith(('ws://', 'wss://')):
        # Assume ws:// if no protocol specified
        if server_address.startswith('localhost') or server_address.startswith('127.0.0.1'):
            server_address = f"ws://{server_address}"
        else:
            server_address = f"wss://{server_address}"
    
    # Special handling for known secure APIs
    if 'blockchain.info' in server_address and server_address.startswith('ws://'):
        server_address = server_address.replace('ws://', 'wss://')
    
    print(f"Connecting to {server_address}...")
    
    # Connect to server
    if not await client.connect(server_address):
        return
    
    # Check if this is a custom server (waits for user info request) or external API
    print("Detecting server type...")
    is_custom_server = False
    
    try:
        # Wait for initial message with timeout
        initial_message = await asyncio.wait_for(client.websocket.recv(), timeout=3.0)
        data = json.loads(initial_message)
        
        if data.get("type") == "request_info":
            # This is our custom server
            is_custom_server = True
            print("Detected custom channel server")
            username = input("Enter your username: ").strip() or "Anonymous"
            await client.send_user_info(username)
        else:
            # This is an external API
            print("Detected external WebSocket API")
            print("Received:", data)
            print("\nThis appears to be an external API. Raw message mode enabled.")
            print("You can send JSON messages directly, or type /quit to exit")
    except asyncio.TimeoutError:
        print("No initial message received - assuming external API")
        print("Raw message mode enabled. Type /quit to exit")
    except Exception as e:
        print(f"Error detecting server type: {e}")
        print("Raw message mode enabled.")
    
    # Start listening for messages
    listen_task = asyncio.create_task(client.listen_for_messages())
    
    # Start input handler in separate thread
    input_thread = threading.Thread(target=get_user_input, args=(client, is_custom_server), daemon=True)
    input_thread.start()
    
    if is_custom_server:
        print("\nConnected to custom server! Type /help for commands.")
        print("Example: /subscribe general")
        print("Example: #general Hello everyone!")
    else:
        print("\nConnected to external API! Type /help for commands.")
        print("Send JSON messages directly to interact with the API.")
    
    try:
        await listen_task
    except KeyboardInterrupt:
        print("\nDisconnecting...")
    finally:
        if client.websocket:
            await client.websocket.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
