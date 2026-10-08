from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os, time

BASE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE, "meds.json")

def read_meds():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def write_meds(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/meds":
            self.send_json(read_meds())
        elif self.path in ("/", "/index.html"):
            with open(os.path.join(BASE, "index.html"), "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path == "/api/meds":
            n = int(self.headers.get("Content-Length", 0))
            d = json.loads(self.rfile.read(n) or b"{}")
            if not d.get("name") or not d.get("time"):
                return self.send_json({"error": "name and time required"}, 400)
            meds = read_meds()
            med = {"id": int(time.time() * 1000), "name": d["name"],
                   "dose": d.get("dose", ""), "time": d["time"], "taken": False}
            meds.append(med)
            write_meds(meds)
            self.send_json(med)
        else:
            self.send_json({"error": "not found"}, 404)

    def do_PUT(self):
        p = self.path.strip("/").split("/")
        if len(p) == 4 and p[0] == "api" and p[1] == "meds" and p[3] == "taken":
            meds = read_meds()
            for m in meds:
                if str(m["id"]) == p[2]:
                    m["taken"] = True
            write_meds(meds)
            self.send_json({"ok": True})
        else:
            self.send_json({"error": "not found"}, 404)

    def do_DELETE(self):
        p = self.path.strip("/").split("/")
        if len(p) == 3 and p[0] == "api" and p[1] == "meds":
            meds = [m for m in read_meds() if str(m["id"]) != p[2]]
            write_meds(meds)
            self.send_json({"ok": True})
        else:
            self.send_json({"error": "not found"}, 404)

if __name__ == "__main__":
    print("Server running at http://localhost:3000")
    HTTPServer(("", 3000), Handler).serve_forever()
