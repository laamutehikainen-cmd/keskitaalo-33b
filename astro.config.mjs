import { defineConfig } from "astro/config";

const repository = "keskitaalo-33b";
const owner = process.env.GITHUB_REPOSITORY_OWNER ?? "OWNER";

export default defineConfig({
  site: `https://${owner}.github.io`,
  base: `/${repository}`,
  output: "static",
  trailingSlash: "always"
});
