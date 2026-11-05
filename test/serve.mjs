// Local test server for the browser page. Sends the two headers a page needs for
// WebAssembly threads (cross-origin isolation).
//   node test/serve.mjs [port] [project.3mf]
// The optional project is served as /input.3mf so the page can slice it on load.
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize, resolve } from "node:path";

const root = resolve(new URL("..", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1"));
const port = Number(process.argv[2] || 8765);
const project = process.argv[3];
const types = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".wasm": "application/wasm", ".json": "application/json", ".3mf": "application/octet-stream" };

createServer((req, res) => {
  const url = decodeURIComponent(req.url.split("?")[0]);
  let file = url === "/input.3mf" && project ? project : join(root, normalize(url).replace(/^[/\\]+/, ""));
  if (url === "/") file = join(root, "test", "browser.html");
  if (!file.startsWith(root) && file !== project) { res.writeHead(403).end(); return; }
  if (!existsSync(file) || statSync(file).isDirectory()) { res.writeHead(404).end("not found"); return; }
  res.writeHead(200, {
    "Content-Type": types[extname(file)] || "application/octet-stream",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cache-Control": "no-store",
  });
  createReadStream(file).pipe(res);
}).listen(port, "127.0.0.1", () => console.log(`http://localhost:${port}/`));
