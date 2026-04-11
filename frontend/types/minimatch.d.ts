declare module "minimatch" {
  function minimatch(target: string, pattern: string, options?: unknown): boolean;
  export = minimatch;
}
