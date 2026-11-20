import os, json, requests

URL = "https://connect.composio.dev/mcp"


def _parse(text):
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)
    out = None
    for line in text.splitlines():
        if line.startswith("data:"):
            payload = line[5:].strip()
            if payload.startswith("{"):
                try:
                    out = json.loads(payload)
                except Exception:
                    pass
    return out


class MCP:
    def __init__(self, key=None):
        key = key or os.environ["COMPOSIO_CONSUMER_KEY"]
        self.h = {"x-consumer-api-key": key, "Content-Type": "application/json",
                  "Accept": "application/json, text/event-stream"}
        self.sid = None
        self.n = 0
        self._post({"jsonrpc": "2.0", "id": self._id(), "method": "initialize",
                    "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                               "clientInfo": {"name": "katha-chitra-gh", "version": "1.0"}}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"}, expect=False)

    def _id(self):
        self.n += 1
        return self.n

    def _post(self, body, expect=True):
        h = dict(self.h)
        if self.sid:
            h["mcp-session-id"] = self.sid
        r = requests.post(URL, headers=h, data=json.dumps(body), timeout=600)
        if "mcp-session-id" in r.headers:
            self.sid = r.headers["mcp-session-id"]
        r.raise_for_status()
        if not expect:
            return None
        out = _parse(r.text)
        if out is None:
            raise RuntimeError("EMPTY_PARSE status=%s ctype=%s body=%r" % (r.status_code, r.headers.get("content-type"), r.text[:600]))
        return out

    def tools(self):
        r = self._post({"jsonrpc": "2.0", "id": self._id(), "method": "tools/list"})
        return r["result"]["tools"]

    def call(self, name, args):
        r = self._post({"jsonrpc": "2.0", "id": self._id(), "method": "tools/call",
                        "params": {"name": name, "arguments": args}})
        if "error" in r:
            raise RuntimeError(json.dumps(r["error"])[:500])
        return r["result"]
