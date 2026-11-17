import { readFileSync, watch } from "node:fs";

const [path, marker, deadline] = Bun.argv.slice(2);
const remaining = Date.parse(deadline) - Date.now();
if (remaining <= 0) process.exit(1);

await new Promise<void>((resolve, reject) => {
  function check() {
    if (!readFileSync(path, "utf8").split("\n").includes(marker)) return;
    clearTimeout(timer);
    watcher.close();
    resolve();
  }
  const watcher = watch(path, check);
  const timer = setTimeout(() => {
    watcher.close();
    reject(new Error("search deadline elapsed"));
  }, remaining);
  check();
});
