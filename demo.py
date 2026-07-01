import sys
import os
# Allow root module import when running as a standalone script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ozero import OZeroIdentity, OZeroProtocol, OZeroNetworkNode

# 1. Generate Identity
print("--- 1. Generating Agent Identity ---")
agent = OZeroIdentity.generate()
print(f"Agent DID: {agent['did']}\n")

# 2. Create and Sign Intent
print("--- 2. Creating and Signing Intent ---")
intent = OZeroProtocol.create_intent(
    agent_id=agent["did"],
    action="EXECUTE_TRADE",
    constraints={"pair": "BTC/USD", "max_price": 65000},
    trust_anchor_id="did:ozero:bank_of_future"
)
signed_payload = OZeroProtocol.sign(agent["private_key"], intent)
print("Signed Payload Generation Successful.\n")

# 3. Verify on Receiver Node
print("--- 3. Verifying Payload at Enterprise Node ---")
node = OZeroNetworkNode(trusted_anchors=["did:ozero:bank_of_future"])
result = node.verify(signed_payload, agent["public_key_hex"])
print(f"Result Status: {result['status']}")
print(f"Tx Hash: {result.get('transaction_hash')}")