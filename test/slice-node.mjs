// Slice a Bambu Studio project with the WebAssembly engine in Node, the same way a
// web page does: files in the engine's in-memory file system, Bambu's own CLI
// arguments, results read back from memory.
//
//   node test/slice-node.mjs <engine-dir> <project.3mf> <resources-dir> [out-dir]
//
// <resources-dir> is a Bambu Studio `resources` folder (only profiles/ is read).
import { mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join, relative } from "node:path";
import { performance } from "node:perf_hooks";

const [engineDir, input, resources, outDir = "test/out"] = process.argv.slice(2);
if (!engineDir || !input || !resources) {
  console.error("usage: node test/slice-node.mjs <engine-dir> <project.3mf> <resources-dir> [out-dir]");
  process.exit(2);
}
const require = createRequire(import.meta.url);
const factory = require(join(process.cwd(), engineDir, "bambu-slicer.js"));

let resolveExit;
const exited = new Promise((r) => (resolveExit = r));
const log = [];
const t0 = performance.now();
const mod = await factory({
  print: (s) => { log.push(s); if (process.env.LIVE) process.stderr.write(`[${((performance.now() - t0) / 1000).toFixed(1)}s] ${s}
`); },
  printErr: (s) => { log.push(s); if (process.env.LIVE) process.stderr.write(`[${((performance.now() - t0) / 1000).toFixed(1)}s] ${s}
`); },
  onExit: (code) => resolveExit(code),
});
const tLoad = performance.now();

// Printer profiles -> /bambu/resources (the CLI's resources_dir() in this build).
let files = 0, bytes = 0;
function copyDir(src, dst) {
  mod.FS.mkdirTree(dst);
  for (const name of readdirSync(src)) {
    const p = join(src, name);
    if (statSync(p).isDirectory()) copyDir(p, `${dst}/${name}`);
    else if (/\.(json|txt|ini|config)$/i.test(name)) {
      const data = readFileSync(p);
      mod.FS.writeFile(`${dst}/${name}`, data);
      files++; bytes += data.length;
    }
  }
}
copyDir(join(resources, "profiles"), "/bambu/resources/profiles");
mod.FS.mkdirTree("/bambu/bin");
mod.FS.mkdirTree("/in");
mod.FS.mkdirTree("/out");
mod.FS.writeFile("/in/p.3mf", readFileSync(input));
const tFiles = performance.now();

mod.callMain([...(process.env.DEBUG ? ["--debug", process.env.DEBUG] : []), "--slice", "1", "--allow-newer-file=1", "--outputdir", "/out", "--export-3mf", "o.gcode.3mf", "/in/p.3mf"]);
// Like the desktop CLI, the engine can hang after it has written its results, so
// finishing is detected from result.json (written last) rather than from exit.
const finished = new Promise((resolve) => {
  let ticks = 0;
  const iv = setInterval(() => {
    if (process.env.LIVE && ++ticks % 50 === 0) {
      let ls = "?";
      try { ls = mod.FS.readdir("/out").join(","); } catch (e) { ls = String(e); }
      process.stderr.write(`[poll ${((performance.now() - t0) / 1000).toFixed(1)}s] /out: ${ls}\n`);
    }
    try {
      mod.FS.stat("/out/result.json");
      clearInterval(iv);
      setTimeout(() => resolve("result.json"), 200);
    } catch {}
  }, 100);
});
const code = await Promise.race([exited, finished]);
const tSlice = performance.now();

mkdirSync(outDir, { recursive: true });
for (const name of mod.FS.readdir("/out")) {
  if (name === "." || name === "..") continue;
  writeFileSync(join(outDir, name), mod.FS.readFile(`/out/${name}`));
}
writeFileSync(join(outDir, "engine.log"), log.join("\n"));
let printTime = "?";
try {
  const head = mod.FS.readFile("/out/plate_1.gcode", { encoding: "utf8" }).slice(0, 4000);
  printTime = (head.match(/total estimated time: ([^\n]+)/) || [])[1] ?? "?";
} catch {}
const mem = mod.HEAP8 ? mod.HEAP8.length : 0;
console.log(JSON.stringify({
  exitCode: code,
  printTime,
  loadMs: Math.round(tLoad - t0),
  profiles: { files, mb: +(bytes / 1e6).toFixed(1), ms: Math.round(tFiles - tLoad) },
  sliceMs: Math.round(tSlice - tFiles),
  heapMb: Math.round(mem / 1e6),
  out: relative(process.cwd(), outDir),
}, null, 1));
process.exit(0);
