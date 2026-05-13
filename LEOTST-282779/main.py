"""
Pure-stdlib Python REST API with Swagger UI.
No external packages required — runs on Python 3.9+.

Start:  python main.py
Open:   http://127.0.0.1:8000/docs   (Swagger UI)
        http://127.0.0.1:8000/openapi.json
"""

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "127.0.0.1"
PORT = 8000

# ---------------------------------------------------------------------------
# In-memory data store (pre-populated with test data)
# ---------------------------------------------------------------------------
_items: dict[int, dict] = {
    1: {"id": 1, "name": "Laptop",     "description": "High-performance laptop", "price": 1299.99},
    2: {"id": 2, "name": "Mouse",      "description": "Wireless optical mouse",  "price": 29.99},
    3: {"id": 3, "name": "Keyboard",   "description": "Mechanical keyboard",     "price": 89.99},
    4: {"id": 4, "name": "Monitor",    "description": "27-inch 4K display",      "price": 499.99},
    5: {"id": 5, "name": "Headphones", "description": "Noise-cancelling ANC",    "price": 199.99},
}
_next_id = 6

# ---------------------------------------------------------------------------
# OpenAPI 3.0 spec
# ---------------------------------------------------------------------------
OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Test API",
        "description": "A simple test API with Swagger UI (pure stdlib)",
        "version": "1.0.0",
    },
    "paths": {
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Health check",
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/items": {
            "get": {
                "tags": ["Items"],
                "summary": "List all items",
                "responses": {"200": {"description": "List of items"}},
            },
            "post": {
                "tags": ["Items"],
                "summary": "Create an item",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name", "price"],
                                "properties": {
                                    "name": {"type": "string", "example": "Widget"},
                                    "description": {"type": "string", "example": "A useful widget"},
                                    "price": {"type": "number", "example": 9.99},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "201": {"description": "Item created"},
                    "400": {"description": "Bad request"},
                },
            },
        },
        "/items/{item_id}": {
            "parameters": [
                {"name": "item_id", "in": "path", "required": True, "schema": {"type": "integer"}}
            ],
            "get": {
                "tags": ["Items"],
                "summary": "Get item by ID",
                "responses": {
                    "200": {"description": "Item found"},
                    "404": {"description": "Not found"},
                },
            },
            "put": {
                "tags": ["Items"],
                "summary": "Update an item",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "price": {"type": "number"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Updated"},
                    "404": {"description": "Not found"},
                },
            },
            "delete": {
                "tags": ["Items"],
                "summary": "Delete an item",
                "responses": {
                    "200": {"description": "Deleted"},
                    "404": {"description": "Not found"},
                },
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Self-contained API Tester UI (zero external dependencies)
# ---------------------------------------------------------------------------
SWAGGER_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Test API – Interactive Tester</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:system-ui,sans-serif;background:#f4f6fb;color:#222}
  header{background:#1a56db;color:#fff;padding:18px 32px}
  header h1{font-size:1.4rem;font-weight:700}header p{font-size:.85rem;opacity:.8;margin-top:4px}
  .container{max-width:900px;margin:28px auto;padding:0 16px}
  .card{background:#fff;border-radius:10px;box-shadow:0 2px 8px #0001;margin-bottom:20px;overflow:hidden}
  .card-header{display:flex;align-items:center;gap:12px;padding:14px 20px;cursor:pointer;border-bottom:1px solid #eee}
  .badge{display:inline-block;padding:3px 10px;border-radius:5px;font-size:.75rem;font-weight:700;color:#fff;min-width:58px;text-align:center}
  .GET{background:#2563eb}.POST{background:#16a34a}.PUT{background:#d97706}.DELETE{background:#dc2626}
  .card-header .path{font-family:monospace;font-size:.95rem;font-weight:600}
  .card-header .desc{font-size:.82rem;color:#666;margin-left:auto}
  .card-body{padding:18px 20px;display:none}
  .card-body.open{display:block}
  label{font-size:.8rem;font-weight:600;color:#444;display:block;margin-bottom:4px;margin-top:12px}
  input,textarea,select{width:100%;padding:8px 10px;border:1px solid #d1d5db;border-radius:6px;font-size:.88rem;font-family:monospace}
  textarea{height:100px;resize:vertical}
  button.run-btn{margin-top:14px;padding:9px 22px;background:#1a56db;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:.88rem;font-weight:600}
  button.run-btn:hover{background:#1646b8}
  .response-box{margin-top:14px;background:#0f172a;color:#e2e8f0;border-radius:8px;padding:14px;font-family:monospace;font-size:.82rem;white-space:pre-wrap;max-height:280px;overflow:auto;display:none}
  .status-line{font-size:.78rem;margin-bottom:6px;font-weight:700}
  .s2{color:#4ade80}.s4{color:#f87171}.s5{color:#f87171}
  .url-bar{font-size:.8rem;color:#555;margin-bottom:8px;font-family:monospace}
  .test-urls{background:#fff;border-radius:10px;box-shadow:0 2px 8px #0001;padding:20px 24px;margin-bottom:24px}
  .test-urls h2{font-size:1rem;font-weight:700;margin-bottom:12px;color:#1a56db}
  .test-urls ul{list-style:none;display:flex;flex-wrap:wrap;gap:10px}
  .test-urls a{display:inline-block;padding:7px 16px;background:#eff6ff;color:#1a56db;border:1px solid #bfdbfe;border-radius:6px;font-size:.82rem;font-family:monospace;text-decoration:none;font-weight:600}
  .test-urls a:hover{background:#dbeafe}
</style>
</head>
<body>
<header>
  <h1>Test API &mdash; Interactive Tester</h1>
  <p>Self-contained API tester &bull; No internet connection required &bull; Pre-loaded with 5 test items</p>
</header>
<div class="container">

  <!-- Quick test URLs -->
  <div class="test-urls">
    <h2>Quick Test URLs (open in browser / Postman)</h2>
    <ul>
      <li><a href="/health" target="_blank">GET /health</a></li>
      <li><a href="/items" target="_blank">GET /items</a></li>
      <li><a href="/items/1" target="_blank">GET /items/1</a></li>
      <li><a href="/items/2" target="_blank">GET /items/2</a></li>
      <li><a href="/items/3" target="_blank">GET /items/3</a></li>
      <li><a href="/openapi.json" target="_blank">GET /openapi.json</a></li>
    </ul>
  </div>

  <!-- GET /health -->
  <div class="card" id="c-health">
    <div class="card-header" onclick="toggle('health')">
      <span class="badge GET">GET</span>
      <span class="path">/health</span>
      <span class="desc">Health check</span>
    </div>
    <div class="card-body" id="b-health">
      <div class="url-bar">GET http://127.0.0.1:8000/health</div>
      <button class="run-btn" onclick="run('health','GET','/health')">Send Request</button>
      <div class="response-box" id="r-health"></div>
    </div>
  </div>

  <!-- GET /items -->
  <div class="card" id="c-list">
    <div class="card-header" onclick="toggle('list')">
      <span class="badge GET">GET</span>
      <span class="path">/items</span>
      <span class="desc">List all items</span>
    </div>
    <div class="card-body" id="b-list">
      <div class="url-bar">GET http://127.0.0.1:8000/items</div>
      <button class="run-btn" onclick="run('list','GET','/items')">Send Request</button>
      <div class="response-box" id="r-list"></div>
    </div>
  </div>

  <!-- GET /items/{id} -->
  <div class="card">
    <div class="card-header" onclick="toggle('getone')">
      <span class="badge GET">GET</span>
      <span class="path">/items/{item_id}</span>
      <span class="desc">Get item by ID</span>
    </div>
    <div class="card-body" id="b-getone">
      <label>item_id (path param)</label>
      <input type="number" id="p-getone" value="1" min="1">
      <button class="run-btn" onclick="run('getone','GET','/items/'+document.getElementById('p-getone').value)">Send Request</button>
      <div class="response-box" id="r-getone"></div>
    </div>
  </div>

  <!-- POST /items -->
  <div class="card">
    <div class="card-header" onclick="toggle('post')">
      <span class="badge POST">POST</span>
      <span class="path">/items</span>
      <span class="desc">Create a new item</span>
    </div>
    <div class="card-body" id="b-post">
      <div class="url-bar">POST http://127.0.0.1:8000/items</div>
      <label>Request Body (JSON)</label>
      <textarea id="b-post-body">{\n  &quot;name&quot;: &quot;New Item&quot;,\n  &quot;description&quot;: &quot;A brand new item&quot;,\n  &quot;price&quot;: 49.99\n}</textarea>
      <button class="run-btn" onclick="runBody('post','POST','/items','b-post-body')">Send Request</button>
      <div class="response-box" id="r-post"></div>
    </div>
  </div>

  <!-- PUT /items/{id} -->
  <div class="card">
    <div class="card-header" onclick="toggle('put')">
      <span class="badge PUT">PUT</span>
      <span class="path">/items/{item_id}</span>
      <span class="desc">Update an item</span>
    </div>
    <div class="card-body" id="b-put">
      <label>item_id (path param)</label>
      <input type="number" id="p-put" value="1" min="1">
      <label>Request Body (JSON)</label>
      <textarea id="b-put-body">{\n  &quot;name&quot;: &quot;Updated Laptop&quot;,\n  &quot;description&quot;: &quot;Updated description&quot;,\n  &quot;price&quot;: 999.99\n}</textarea>
      <button class="run-btn" onclick="runBody('put','PUT','/items/'+document.getElementById('p-put').value,'b-put-body')">Send Request</button>
      <div class="response-box" id="r-put"></div>
    </div>
  </div>

  <!-- DELETE /items/{id} -->
  <div class="card">
    <div class="card-header" onclick="toggle('del')">
      <span class="badge DELETE">DELETE</span>
      <span class="path">/items/{item_id}</span>
      <span class="desc">Delete an item</span>
    </div>
    <div class="card-body" id="b-del">
      <label>item_id (path param)</label>
      <input type="number" id="p-del" value="1" min="1">
      <button class="run-btn" onclick="run('del','DELETE','/items/'+document.getElementById('p-del').value)">Send Request</button>
      <div class="response-box" id="r-del"></div>
    </div>
  </div>

</div>
<script>
  function toggle(id){
    const b=document.getElementById('b-'+id);
    b.classList.toggle('open');
  }
  async function run(id,method,path){
    const box=document.getElementById('r-'+id);
    box.style.display='block';
    box.textContent='Sending...';
    try{
      const res=await fetch(path,{method});
      const data=await res.json();
      const cls=res.status<300?'s2':res.status<500?'s4':'s5';
      box.innerHTML='<span class="status-line '+cls+'">HTTP '+res.status+'</span>'+JSON.stringify(data,null,2);
    }catch(e){box.textContent='Error: '+e.message;}
  }
  async function runBody(id,method,path,bodyId){
    const box=document.getElementById('r-'+id);
    box.style.display='block';
    box.textContent='Sending...';
    try{
      const raw=document.getElementById(bodyId).value
                 .replace(/&quot;/g,'"').replace(/&amp;/g,'&');
      const res=await fetch(path,{method,headers:{'Content-Type':'application/json'},body:raw});
      const data=await res.json();
      const cls=res.status<300?'s2':res.status<500?'s4':'s5';
      box.innerHTML='<span class="status-line '+cls+'">HTTP '+res.status+'</span>'+JSON.stringify(data,null,2);
    }catch(e){box.textContent='Error: '+e.message;}
  }
  // Auto-open first two panels
  toggle('health');toggle('list');
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Route helpers
# ---------------------------------------------------------------------------

def _send(handler, status: int, body, content_type="application/json"):
    payload = json.dumps(body, indent=2).encode() if content_type == "application/json" else body.encode()
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def _read_json(handler):
    length = int(handler.headers.get("Content-Length", 0))
    raw = handler.rfile.read(length)
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):  # quiet startup noise
        print(f"{self.address_string()} - {fmt % args}")

    # ---- GET ---------------------------------------------------------------

    def do_GET(self):
        path = self.path.split("?")[0]

        if path in ("/", "/docs"):
            _send(self, 200, SWAGGER_HTML, "text/html")

        elif path == "/openapi.json":
            _send(self, 200, OPENAPI_SPEC)

        elif path == "/health":
            _send(self, 200, {"status": "ok"})

        elif path == "/items":
            _send(self, 200, list(_items.values()))

        elif m := re.fullmatch(r"/items/(\d+)", path):
            item_id = int(m.group(1))
            if item_id not in _items:
                _send(self, 404, {"detail": "Item not found"})
            else:
                _send(self, 200, _items[item_id])

        else:
            _send(self, 404, {"detail": "Not found"})

    # ---- POST --------------------------------------------------------------

    def do_POST(self):
        global _next_id
        path = self.path.split("?")[0]

        if path == "/items":
            try:
                data = _read_json(self)
            except (json.JSONDecodeError, KeyError):
                _send(self, 400, {"detail": "Invalid JSON"})
                return
            if "name" not in data or "price" not in data:
                _send(self, 400, {"detail": "'name' and 'price' are required"})
                return
            item = {"id": _next_id, "name": data["name"],
                    "description": data.get("description", ""),
                    "price": data["price"]}
            _items[_next_id] = item
            _next_id += 1
            _send(self, 201, item)
        else:
            _send(self, 404, {"detail": "Not found"})

    # ---- PUT ---------------------------------------------------------------

    def do_PUT(self):
        path = self.path.split("?")[0]
        if m := re.fullmatch(r"/items/(\d+)", path):
            item_id = int(m.group(1))
            if item_id not in _items:
                _send(self, 404, {"detail": "Item not found"})
                return
            try:
                data = _read_json(self)
            except json.JSONDecodeError:
                _send(self, 400, {"detail": "Invalid JSON"})
                return
            item = _items[item_id]
            item.update({k: data[k] for k in ("name", "description", "price") if k in data})
            _send(self, 200, item)
        else:
            _send(self, 404, {"detail": "Not found"})

    # ---- DELETE ------------------------------------------------------------

    def do_DELETE(self):
        path = self.path.split("?")[0]
        if m := re.fullmatch(r"/items/(\d+)", path):
            item_id = int(m.group(1))
            if item_id not in _items:
                _send(self, 404, {"detail": "Item not found"})
                return
            del _items[item_id]
            _send(self, 200, {"detail": "Item deleted"})
        else:
            _send(self, 404, {"detail": "Not found"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Serving at http://{HOST}:{PORT}")
    print(f"Swagger UI  -> http://{HOST}:{PORT}/docs")
    print(f"OpenAPI JSON -> http://{HOST}:{PORT}/openapi.json")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
