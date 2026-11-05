// Packs a Bambu Studio resources/profiles folder (JSON only) into one file the page
// can fetch: { "BBL.json": "...", "BBL/machine/....json": "...", ... }.
//   node test/pack-profiles.mjs <resources-dir> <out.json>
import { readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { join, relative } from "node:path";

const [resources, out] = process.argv.slice(2);
const base = join(resources, "profiles");
const files = {};
(function walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p);
    else if (name.endsWith(".json")) files[relative(base, p).replace(/\\/g, "/")] = readFileSync(p, "utf8");
  }
})(base);
writeFileSync(out, JSON.stringify(files));
console.log(`${Object.keys(files).length} files, ${(statSync(out).size / 1e6).toFixed(1)} MB -> ${out}`);
