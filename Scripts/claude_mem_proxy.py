#!/usr/bin/env python3
"""TCP proxy: 100.124.194.102:37778 → 127.0.0.1:37778
Exposes claude-mem on the Tailscale interface for vault-neo access.
Started at login via KarmaClaudeMemProxy scheduled task."""

import asyncio
import logging
import sys

LISTEN_HOST = "100.124.194.102"   # P1 Tailscale IP
LISTEN_PORT = 37778
TARGET_HOST = "127.0.0.1"         # claude-mem loopback binding
TARGET_PORT = 37778

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [claude-mem-proxy] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


async def pipe(reader, writer):
    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError):
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def handle_client(client_reader, client_writer):
    peer = client_writer.get_extra_info("peername", "unknown")
    try:
        target_reader, target_writer = await asyncio.open_connection(
            TARGET_HOST, TARGET_PORT
        )
        await asyncio.gather(
            pipe(client_reader, target_writer),
            pipe(target_reader, client_writer),
        )
    except Exception as e:
        log.debug("Connection from %s failed: %s", peer, e)
    finally:
        try:
            client_writer.close()
        except Exception:
            pass


async def main():
    server = await asyncio.start_server(
        handle_client, LISTEN_HOST, LISTEN_PORT
    )
    log.info(
        "Proxy started: %s:%d → %s:%d",
        LISTEN_HOST, LISTEN_PORT, TARGET_HOST, TARGET_PORT,
    )
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

