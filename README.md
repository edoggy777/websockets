WebSocket Channel System

A Python-based WebSocket server and universal client for real-time channel communication and external API testing.

Multi-channel subscription system (like Discord/Slack)
Real-time messaging between connected users
User join/leave notifications
Configurable channels (general, tech, random, announcements)
Clean JSON-based protocol

Universal WebSocket Client

Dual Mode Operation: Automatically detects custom servers vs external APIs
Smart URL Handling: Auto-converts protocols (ws:// ↔ wss://)
External API Support: Test any public WebSocket API with JSON commands
Pretty Output: Formatted timestamps, heartbeat detection, and colored messages

# Install Dependencies

pip install websockets

# How to Run / Additionally you can paste in json

<img width="742" height="483" alt="Screenshot from 2025-09-01 11-20-20" src="https://github.com/user-attachments/assets/986efcb3-bf0b-41ac-a118-c555c8e782f0" />


bash$:~/websockets$ python3 ws_client.py 

WebSocket Channel Client

Enter WebSocket server address (default: ws://localhost:8765): wss://ws-feed.exchange.coinbase.com 
Connecting to wss://ws-feed.exchange.coinbase.com...
Connected to wss://ws-feed.exchange.coinbase.com
Detecting server type...
No initial message received - assuming external API
Raw message mode enabled. Type /quit to exit

Connected to external API! Type /help for commands.
Send JSON messages directly to interact with the API.
{"type": "subscribe", "channels": ["ticker"], "product_ids": ["BTC-USD"]}


# Output

bash$:~/websockets$ python3 ws_client.py 

WebSocket Channel Client

Enter WebSocket server address (default: ws://localhost:8765):  wss://ws-feed.exchange.coinbase.com  
Connecting to wss://ws-feed.exchange.coinbase.com...
Connected to wss://ws-feed.exchange.coinbase.com
Detecting server type...
No initial message received - assuming external API
Raw message mode enabled. Type /quit to exit

Connected to external API! Type /help for commands.
Send JSON messages directly to interact with the API.
{"type": "subscribe", "channels": ["ticker"], "product_ids": ["BTC-USD"]}
[10:25:21] {
  "type": "subscriptions",
  "channels": [
    {
      "name": "ticker",
      "product_ids": [
        "BTC-USD"
      ],
      "account_ids": null
    }
  ]
}
[10:25:21] {
  "type": "ticker",
  "sequence": 111174002031,
  "product_id": "BTC-USD",
  "price": "108647.36",
  "open_24h": "108990.11",
  "volume_24h": "4448.70932897",
  "low_24h": "107250",
  "high_24h": "109907.51",
  "volume_30d": "156618.14704213",
  "best_bid": "108647.36",
  "best_bid_size": "0.27932052",
  "best_ask": "108647.37",
  "best_ask_size": "0.00802119",
  "side": "sell",

