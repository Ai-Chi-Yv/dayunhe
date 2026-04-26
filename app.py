
import ast
import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_HTML = BASE_DIR / "京杭大运河_游客导览增强版_三次修改.html"


def _extract_stops_from_html(html_path: Path):
    text = html_path.read_text(encoding="utf-8")
    m = re.search(r"const\s+stops\s*=\s*(\[.*?\n\s*\];)", text, re.S)
    if not m:
        raise RuntimeError("Could not find `const stops = [...]` in the HTML file.")
    raw = m.group(1).rstrip(";")
    raw = re.sub(r"(?<=\{|,)\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", r'"\1":', raw)
    raw = raw.replace("true", "True").replace("false", "False").replace("null", "None")
    data = ast.literal_eval(raw)
    if not isinstance(data, list):
        raise RuntimeError("Parsed stops data is not a list.")
    return data


try:
    STOPS = _extract_stops_from_html(DEFAULT_HTML)
    LOAD_ERROR = None
except Exception as exc:
    STOPS = []
    LOAD_ERROR = str(exc)


def _json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/":
            if DEFAULT_HTML.exists():
                content = DEFAULT_HTML.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
                return
            self._set_headers(404)
            self.wfile.write(_json_bytes({
                "message": "Frontend HTML file not found.",
                "expected_file": str(DEFAULT_HTML),
                "stops_loaded": len(STOPS),
                "error": LOAD_ERROR,
            }))
            return

        if path == "/api/health":
            self._set_headers()
            self.wfile.write(_json_bytes({
                "status": "ok",
                "stops_loaded": len(STOPS),
                "frontend_found": DEFAULT_HTML.exists(),
                "error": LOAD_ERROR,
            }))
            return

        if path == "/api/stats":
            categories = {}
            for stop in STOPS:
                cat = stop.get("category", "未知")
                categories[cat] = categories.get(cat, 0) + 1
            self._set_headers()
            self.wfile.write(_json_bytes({
                "route_length_km": 1794,
                "selected_nodes": len(STOPS),
                "categories": categories,
                "first_stop": STOPS[0]["name"] if STOPS else None,
                "last_stop": STOPS[-1]["name"] if STOPS else None,
            }))
            return

        if path == "/api/stops":
            category = (qs.get("category", [""])[0] or "").strip()
            q = (qs.get("q", [""])[0] or "").strip().lower()
            sort = (qs.get("sort", ["route"])[0] or "route").strip()

            items = STOPS
            if category and category != "all":
                items = [s for s in items if s.get("category") == category]
            if q:
                def matches(stop):
                    haystack = " ".join([
                        str(stop.get("name", "")),
                        str(stop.get("short", "")),
                        str(stop.get("category", "")),
                        str(stop.get("archName", "")),
                        str(stop.get("buildingList", "")),
                        " ".join(stop.get("tags", [])),
                    ]).lower()
                    return q in haystack
                items = [s for s in items if matches(s)]
            if sort == "name":
                items = sorted(items, key=lambda s: s.get("name", ""))
            else:
                items = sorted(items, key=lambda s: s.get("progress", 0))

            self._set_headers()
            self.wfile.write(_json_bytes({"count": len(items), "items": items}))
            return

        if path.startswith("/api/stops/"):
            slug = path.split("/api/stops/", 1)[1].strip().lower()
            for stop in STOPS:
                if stop.get("name", "").lower() == slug or stop.get("short", "").lower() == slug:
                    self._set_headers()
                    self.wfile.write(_json_bytes(stop))
                    return
            self._set_headers(404)
            self.wfile.write(_json_bytes({"error": "stop not found", "slug": slug}))
            return

        if path == "/api/current":
            idx_raw = (qs.get("idx", ["0"])[0] or "0").strip()
            try:
                idx = int(idx_raw)
            except ValueError:
                idx = 0
            if not STOPS:
                self._set_headers(500)
                self.wfile.write(_json_bytes({"error": "no stops loaded"}))
                return
            idx = max(0, min(idx, len(STOPS) - 1))
            self._set_headers()
            self.wfile.write(_json_bytes(STOPS[idx]))
            return

        if path == "/api/search":
            q = (qs.get("q", [""])[0] or "").strip().lower()
            if not q:
                self._set_headers()
                self.wfile.write(_json_bytes({"count": 0, "items": []}))
                return
            result = []
            for stop in STOPS:
                haystack = " ".join([
                    str(stop.get("name", "")),
                    str(stop.get("short", "")),
                    str(stop.get("category", "")),
                    str(stop.get("archName", "")),
                    str(stop.get("quote", "")),
                    str(stop.get("buildingList", "")),
                    " ".join(stop.get("tags", [])),
                ]).lower()
                if q in haystack:
                    result.append(stop)
            self._set_headers()
            self.wfile.write(_json_bytes({"count": len(result), "items": result}))
            return

        if path.startswith("/frontend/"):
            rel = path[len("/frontend/"):]
            file_path = BASE_DIR / rel
            if file_path.exists() and file_path.is_file():
                data = file_path.read_bytes()
                mime = "text/plain; charset=utf-8"
                if file_path.suffix.lower() == ".html":
                    mime = "text/html; charset=utf-8"
                elif file_path.suffix.lower() == ".json":
                    mime = "application/json; charset=utf-8"
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data)
                return
            self._set_headers(404)
            self.wfile.write(_json_bytes({"error": "file not found", "path": rel}))
            return

        self._set_headers(404)
        self.wfile.write(_json_bytes({"error": "not found", "path": path}))

    def log_message(self, format, *args):
        # Keep console output clean.
        return


def main():
    port = int(os.environ.get("PORT", "5000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print("Server running at http://127.0.0.1:{}".format(port))
    if LOAD_ERROR:
        print("Warning: could not load stops from HTML:", LOAD_ERROR)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
