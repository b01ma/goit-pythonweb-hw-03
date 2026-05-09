from __future__ import annotations

import json
import mimetypes
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from jinja2 import Environment, FileSystemLoader, select_autoescape


BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
DATA_FILE = STORAGE_DIR / "data.json"
TEMPLATE_DIR = BASE_DIR / "templates"


jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def ensure_storage() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")


def read_messages() -> dict[str, dict[str, str]]:
    ensure_storage()
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def save_message(message_data: dict[str, str]) -> None:
    messages = read_messages()
    messages[str(datetime.now())] = message_data
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self.send_html(BASE_DIR / "index.html")
            return

        if self.path in {"/message", "/message.html"}:
            self.send_html(BASE_DIR / "message.html")
            return

        if self.path == "/read":
            self.send_read_page()
            return

        if self.path in {"/style.css", "/logo.png"}:
            self.send_static(BASE_DIR / self.path.lstrip("/"))
            return

        self.send_html(BASE_DIR / "error.html", status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/message":
            self.send_html(BASE_DIR / "error.html", status=HTTPStatus.NOT_FOUND)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        parsed_data = parse_qs(body.decode("utf-8"), keep_blank_values=True)

        message_data = {
            "username": parsed_data.get("username", [""])[0],
            "message": parsed_data.get("message", [""])[0],
        }
        save_message(message_data)

        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", "/")
        self.end_headers()

    def send_read_page(self) -> None:
        template = jinja_env.get_template("read.html")
        rendered_page = template.render(messages=read_messages())
        content = rendered_page.encode("utf-8")

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_html(self, file_path: Path, status: HTTPStatus = HTTPStatus.OK) -> None:
        if not file_path.exists():
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return

        content = file_path.read_bytes()
        self.send_response(status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_static(self, file_path: Path) -> None:
        if not file_path.exists():
            self.send_html(BASE_DIR / "error.html", status=HTTPStatus.NOT_FOUND)
            return

        mime_type, _ = mimetypes.guess_type(file_path.name)
        content = file_path.read_bytes()

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", mime_type or "application/octet-stream")
        self.send_header("Content-length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def run(host: str = "0.0.0.0", port: int = 3000) -> None:
    ensure_storage()
    server = HTTPServer((host, port), HttpHandler)
    try:
        print(f"Server started at http://{host}:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
