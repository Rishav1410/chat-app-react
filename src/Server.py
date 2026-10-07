"""
Tiny chat relay server for the React chat app.

Run it with:   python Server.py
It uses only Python's standard library, so there is nothing to install.

How it works
------------
The two chat apps never talk to each other directly. Both talk to THIS
server, and the server passes messages between them (like a post office).

Each user is identified by an IP address that they type in. Using the typed
address (instead of the real network address) lets you run both users on the
same computer, where both would otherwise look like 127.0.0.1.

API (all responses are JSON)
----------------------------
POST /connect   {"me": "1.1.1.1", "name": "Rishi", "peer": "2.2.2.2"}
    Say "I'm here" and who you want to chat with.
    -> {"ok": true, "peerOnline": false, "peerName": null}

POST /send      {"from": "1.1.1.1", "to": "2.2.2.2", "text": "hello"}
    Put a message in the queue for the other person.
    -> {"ok": true, "message": {...}}

GET  /poll?me=1.1.1.1&peer=2.2.2.2
    Ask "anything new for me?" Call this every 1-2 seconds.
    Each poll also tells the server you're still online.
    -> {"messages": [...], "peerOnline": true, "peerName": "Alex"}
"""

import json
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"     # listen on every network card, so other computers can reach it
PORT = 8000
ONLINE_TIMEOUT = 5   # seconds without a poll before a user counts as offline

# ---------------------------------------------------------------------------
# Global state. Everything lives in memory and is lost when the server stops.
# ---------------------------------------------------------------------------
users = {}          # ip -> {"name": "Rishi", "last_seen": 1759...}
message_queue = {}  # recipient ip -> list of messages waiting to be picked up
next_id = 1         # each message gets the next number as its id
lock = threading.Lock()  # several requests can arrive at once; only one may change the data at a time


def is_online(ip):
    """A user is online if they polled within the last ONLINE_TIMEOUT seconds."""
    user = users.get(ip)
    return user is not None and time.time() - user["last_seen"] < ONLINE_TIMEOUT


def peer_status(peer):
    user = users.get(peer)
    return {
        "peerOnline": is_online(peer),
        "peerName": user["name"] if user else None,
    }


class ChatHandler(BaseHTTPRequestHandler):
    # ---------- small helpers ----------

    def send_cors_headers(self):
        # The React app runs on a different port (3000), so the browser asks
        # for permission first. These headers say "yes, you may call me".
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return None

    def log_message(self, format, *args):
        # Silence the default one-line-per-request log. Polling happens every
        # second, so it would flood the terminal. We print our own lines instead.
        pass

    # ---------- routing ----------

    def do_OPTIONS(self):
        # The browser's "may I?" check before a POST with JSON.
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        data = self.read_json()
        if not isinstance(data, dict):
            return self.send_json({"error": "Body must be a JSON object"}, 400)

        if path == "/connect":
            self.handle_connect(data)
        elif path == "/send":
            self.handle_send(data)
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/poll":
            params = parse_qs(url.query)
            me = params.get("me", [""])[0].strip()
            peer = params.get("peer", [""])[0].strip()
            self.handle_poll(me, peer)
        else:
            self.send_json({"error": "Not found"}, 404)

    # ---------- the three API endpoints ----------

    def handle_connect(self, data):
        me = str(data.get("me", "")).strip()
        name = str(data.get("name", "")).strip()
        peer = str(data.get("peer", "")).strip()
        if not me or not name or not peer:
            return self.send_json({"error": "me, name and peer are required"}, 400)

        with lock:
            users[me] = {"name": name, "last_seen": time.time()}
            message_queue.setdefault(me, [])
            status = peer_status(peer)

        print(f"[connect] {name} ({me}) wants to chat with {peer} "
              f"-> peer is {'online' if status['peerOnline'] else 'offline'}")
        self.send_json({"ok": True, **status})

    def handle_send(self, data):
        global next_id
        sender = str(data.get("from", "")).strip()
        to = str(data.get("to", "")).strip()
        text = str(data.get("text", "")).strip()
        if not sender or not to or not text:
            return self.send_json({"error": "from, to and text are required"}, 400)

        with lock:
            if sender not in users:
                return self.send_json({"error": "Call /connect first"}, 403)

            message = {
                "id": next_id,
                "from": sender,
                "sender": users[sender]["name"],
                "text": text,
                "time": datetime.now().strftime("%H:%M"),
            }
            next_id += 1
            # Always queue it. If the other person is offline, it simply waits
            # here until their next poll.
            message_queue.setdefault(to, []).append(message)
            users[sender]["last_seen"] = time.time()
            waiting = len(message_queue[to])

        print(f"[send]    {message['sender']} -> {to}: {text!r} "
              f"({waiting} waiting for {to})")
        self.send_json({"ok": True, "message": message})

    def handle_poll(self, me, peer):
        if not me or not peer:
            return self.send_json({"error": "me and peer are required"}, 400)

        with lock:
            if me not in users:
                # Happens if the server restarted. The app should call /connect again.
                return self.send_json({"error": "Call /connect first"}, 403)

            users[me]["last_seen"] = time.time()  # "I'm still here"

            # Hand over only the messages from the person I'm chatting with,
            # and keep anything else in the queue.
            queue = message_queue.get(me, [])
            delivered = [m for m in queue if m["from"] == peer]
            message_queue[me] = [m for m in queue if m["from"] != peer]
            status = peer_status(peer)

        if delivered:
            print(f"[deliver] {len(delivered)} message(s) to {users[me]['name']} ({me})")
        self.send_json({"messages": delivered, **status})


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ChatHandler)
    print(f"Chat server running on http://localhost:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")