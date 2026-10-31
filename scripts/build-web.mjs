import AdmZip from "adm-zip";
import { existsSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { execFileSync } from "node:child_process";

const root = process.cwd();
const archive = resolve(root, "source/Rythu-Mitra-Web.zip");
const webDir = resolve(root, "apps/web");

if (!existsSync(archive)) {
  throw new Error("Missing source/Rythu-Mitra-Web.zip");
}
new AdmZip(archive).extractAllTo(root, true);
if (!existsSync(resolve(webDir, "package.json"))) {
  throw new Error("Frontend package.json was not extracted to apps/web");
}

execFileSync("npm", ["install", "--no-audit", "--no-fund"], {
  cwd: webDir,
  stdio: "inherit"
});
execFileSync("npm", ["run", "build"], {
  cwd: webDir,
  stdio: "inherit"
});
