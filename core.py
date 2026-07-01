import json
import base64
import hashlib
import time
import uuid
from ecdsa import SigningKey, VerifyingKey, SECP256k1

class OZeroIdentity:
    """
    Manages the cryptographic identity of an AI agent using SECP256k1 and SHA-256.
    """
    @staticmethod
    def generate():
        """Generates a new decentralized identity (DID) and keypair."""
        private_key = SigningKey.generate(curve=SECP256k1)
        public_key = private_key.verifying_key
        pub_hex = public_key.to_string().hex()
        
        # Security Fix: Derive DID via SHA-256 hash instead of insecure truncation
        did_suffix = hashlib.sha256(bytes.fromhex(pub_hex)).hexdigest()[:40]
        
        return {
            "private_key": private_key.to_string().hex(),
            "did": "did:ozero:" + did_suffix,
            "public_key_hex": pub_hex
        }

class OZeroProtocol:
    """
    Core protocol for A2A trust, featuring anti-replay mechanics 
    and deterministic JSON canonicalization.
    """
    @staticmethod
    def _canonicalize(payload):
        """Forces strict, cross-language JSON formatting without whitespaces."""
        return json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')

    @staticmethod
    def create_intent(agent_id, action, constraints, trust_anchor_id=None):
        """Creates a standardized payload with a cryptographic nonce and TTL."""
        return {
            "version": "1.1.0",
            "nonce": str(uuid.uuid4()), 
            "timestamp": int(time.time()),
            "agent_id": agent_id,
            "action": action,
            "constraints": constraints,
            "trust_anchor": trust_anchor_id
        }

    @classmethod
    def sign(cls, private_key_hex, intent):
        """Signs the canonical version of the intent."""
        sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
        canonical_intent = cls._canonicalize(intent)
        signature = sk.sign(canonical_intent)
        return {
            "intent": intent,
            "signature": base64.b64encode(signature).decode('utf-8')
        }

class OZeroNetworkNode:
    """
    Enterprise receiver node that validates intent cryptographic proof and parameters.
    """
    def __init__(self, trusted_anchors=None, ttl_seconds=300):
        self.trusted_anchors = trusted_anchors or []
        self.ttl_seconds = ttl_seconds
        self.seen_nonces = {} # Maps nonce -> ingestion_timestamp

    def _cleanup_expired_nonces(self):
        """Memory protection: Removes nonces older than the allowed TTL window."""
        current_time = time.time()
        expired = [nonce for nonce, timestamp in self.seen_nonces.items() if current_time - timestamp > self.ttl_seconds]
        for nonce in expired:
            del self.seen_nonces[nonce]

    def verify(self, signed_payload, agent_public_key_hex):
        """Validates the signature, anti-replay properties, and trust anchor."""
        self._cleanup_expired_nonces()
        
        intent = signed_payload.get("intent")
        signature_b64 = signed_payload.get("signature")
        
        if not intent or not signature_b64:
            return {"status": "REJECTED", "reason": "Malformed signed payload structure."}
            
        nonce = intent.get("nonce")
        timestamp = intent.get("timestamp")
        
        # Security Fix: Symmetric clock protection mitigating future-timestamp manipulation
        if abs(time.time() - timestamp) > self.ttl_seconds:
            return {"status": "REJECTED", "reason": "Timestamp out of sync or expired."}
            
        # Anti-Replay Check
        if nonce in self.seen_nonces:
            return {"status": "REJECTED", "reason": "Replay Attack Detected."}
            
        # Cryptographic Validation
        try:
            vk = VerifyingKey.from_string(bytes.fromhex(agent_public_key_hex), curve=SECP256k1)
            canonical_intent = OZeroProtocol._canonicalize(intent)
            signature = base64.b64decode(signature_b64)
            
            if not vk.verify(signature, canonical_intent):
                return {"status": "REJECTED", "reason": "Invalid cryptographic signature."}
        except Exception as e:
            return {"status": "REJECTED", "reason": f"Verification failed: {str(e)}"}
            
        # Liability & Trust Anchor Check
        anchor = intent.get("trust_anchor")
        if anchor and anchor not in self.trusted_anchors:
            return {"status": "REJECTED", "reason": "Trust Anchor not recognized."}
            
        # Register nonce with current timestamp for eviction logic
        self.seen_nonces[nonce] = time.time()
        tx_hash = hashlib.sha256(OZeroProtocol._canonicalize(intent)).hexdigest()

        return {
            "status": "APPROVED",
            "transaction_hash": tx_hash,
            "message": "A2A interaction verified securely."
        }