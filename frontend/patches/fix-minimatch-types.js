const fs = require("fs");
const path = require("path");

const target = path.join(__dirname, "..", "node_modules", "@types", "minimatch", "index.d.ts");
if (!fs.existsSync(target)) {
  fs.writeFileSync(
    target,
    `export = minimatch;
declare function minimatch(target: string, pattern: string, options?: minimatch.IOptions): boolean;
declare namespace minimatch {
  interface IOptions { [key: string]: unknown; }
}
`
  );
  console.log("Patched @types/minimatch");
}
