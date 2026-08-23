import json
import sqlite3
import threading
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8000
DATABASE = Path("realtime_events.db")
CLIENTS = set()
CLIENTS_LOCK = threading.Lock()


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            detail TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    return connection


def list_events():
    connection = get_connection()
    rows = connection.execute(
        "SELECT id, title, detail, created_at FROM events ORDER BY id DESC LIMIT 50"
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def create_event(title, detail):
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    connection = get_connection()
    cursor = connection.execute(
        "INSERT INTO events (title, detail, created_at) VALUES (?, ?, ?)",
        (title, detail, created_at),
    )
    connection.commit()
    event = {
        "id": cursor.lastrowid,
        "title": title,
        "detail": detail,
        "created_at": created_at,
    }
    connection.close()
    return event


def broadcast(event):
    message = f"data: {json.dumps(event)}\n\n".encode("utf-8")
    with CLIENTS_LOCK:
        clients = list(CLIENTS)
    disconnected = []
    for client in clients:
        try:
            client.wfile.write(message)
            client.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            disconnected.append(client)
    with CLIENTS_LOCK:
        for client in disconnected:
            CLIENTS.discard(client)


class RequestHandler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/events":
            self.send_json({"events": list_events()})
            return
        if path == "/api/stream":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            with CLIENTS_LOCK:
                CLIENTS.add(self)
            try:
                self.wfile.write(b": connected\n\n")
                self.wfile.flush()
                while True:
                    self.rfile.read(1)
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                with CLIENTS_LOCK:
                    CLIENTS.discard(self)
            return
        if path == "/" or path == "/index.html":
            content = Path("index.html").read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):
        if urlparse(self.path).path != "/api/events":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            title = str(payload.get("title", "")).strip()
            detail = str(payload.get("detail", "")).strip()
            if not title or not detail:
                raise ValueError("title dan detail wajib diisi")
            event = create_event(title[:100], detail[:500])
            broadcast(event)
            self.send_json(event, HTTPStatus.CREATED)
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "title dan detail wajib diisi"}, HTTPStatus.BAD_REQUEST)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    get_connection().close()
    server = ThreadingHTTPServer((HOST, PORT), RequestHandler)
    print(f"Real-time app berjalan di http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dihentikan")
    finally:
        server.server_close()
