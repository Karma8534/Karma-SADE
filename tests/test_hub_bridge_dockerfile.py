from pathlib import Path


def test_hub_bridge_dockerfile_builds_proxy_runtime():
    source = Path("hub-bridge/app/Dockerfile").read_text(encoding="utf-8")
    assert "COPY app/proxy.js ./" in source
    assert "COPY app/public/ ./public/" in source
    assert 'CMD ["node", "proxy.js"]' in source
    assert "No npm install" in source
    assert "COPY lib/" not in source
    assert "RUN npm install" not in source
    assert "server.js" not in source
