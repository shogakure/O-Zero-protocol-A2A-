# O-Zero Protocol
**Decentralized, Zero-Trust Agent-to-Agent (A2A) Communication Standard**

The O-Zero Protocol is a lightweight, mathematically verifiable messaging framework built specifically for autonomous AI agents. It completely replaces fragile API-key architectures with cryptographic intent validation over distributed infrastructures like Nostr.

## The Problem
As AI agents become highly autonomous, traditional API keys turn into critical security liabilities. When an agent triggers an action inside an enterprise ecosystem, a system needs to verify **who** the agent is, **what** it intends to do, and **who** vouches for it (Liability Anchors)—without passing static tokens that can be intercepted.

## Key Optimizations & Security Layers
- **Secure DID Generation:** Uses `SECP256k1` elliptic curve keys hashed via `SHA-256` to derive consistent, collision-resistant DIDs.
- **Deterministic Canonicalization:** Enforces RFC-8785-like JSON serialization structures to ensure cross-language cryptographic consistency.
- **Symmetric Clock Protection:** Prevents future-timestamp spoofing alongside traditional past TTL decay verification.
- **Memory-Safe Anti-Replay:** Auto-evicting memory structures to keep state tracking safe from DDoS or leak vectors.
- **Serverless Transport:** Designed to interface natively with the **Nostr** publish/subscribe network (Custom Event Kind 30000).

## Installation
```bash
pip install ecdsa websocket-client
