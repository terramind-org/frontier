// Entry of the npm bundle (dist-cli/frontier.mjs); `import.meta.main` in cli.ts is bun-only.
import { main } from './cli.ts';

process.exit(await main(process.argv.slice(2)));
