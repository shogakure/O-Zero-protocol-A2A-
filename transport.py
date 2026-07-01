import json
import time
import websocket

class OZeroNostrTransport:
    """
    Wraps the OZero protocol for decentralized transport over the Nostr network.
    NOTE: Standard public relays reject events without a valid 'id' and 'sig'. 
    For production deployment, ensure the content payload is wrapped inside a fully 
    valid, client-signed Nostr event structure.
    """
    def __init__(self, relay_url="wss://relay.damus.io"):
        self.relay_url = relay_url
        
    def broadcast_intent(self, signed_payload, nostr_pubkey=None, nostr_signature=None, event_id=None):
        """Pushes the signed intent to a public Nostr relay."""
        ws = websocket.WebSocket()
        try:
            ws.connect(self.relay_url)
            
            # Formulating a standard Nostr Event (Kind 30000)
            event_data = {
                "kind": 30000, 
                "created_at": int(time.time()),
                "tags": [["ozero", "intent"]],
                "content": json.dumps(signed_payload),
                "pubkey": nostr_pubkey or "0000000000000000000000000000000000000000000000000000000000000000",
            }
            if event_id:
                event_data["id"] = event_id
            if nostr_signature:
                event_data["sig"] = nostr_signature
                
            nostr_event = ["EVENT", event_data]
            ws.send(json.dumps(nostr_event))
            ws.close()
            return True
        except Exception as e:
            print(f"Transport error: {e}")
            return False