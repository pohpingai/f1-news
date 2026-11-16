// Runs Stats questions through the REAL Worker code (worker/ask-worker.js, the /stats tool loop),
// reading stats.json from a folder on this computer instead of the live website.
// Used by tests/report_card.py, and handy for trying questions by hand:
//
//   OPENROUTER_API_KEY=... node tests/stats_runner.mjs data "Who leads the championship?"
//
// Input:  either command-line arguments (folder, then questions) or stdin {"data_dir": "...", "questions": [...]}
// Output: JSON list of the Worker's answers (with the logged steps), one per question.

import fs from "node:fs";
import { answerStats } from "../worker/ask-worker.js";

const input = process.argv.length > 3
  ? { data_dir: process.argv[2], questions: process.argv.slice(3) }
  : JSON.parse(fs.readFileSync(0, "utf8"));
const TEST_SITE = "https://test-site.invalid/";

const realFetch = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  url = String(url);
  if (url.startsWith(TEST_SITE)) {
    const file = `${input.data_dir}/${url.slice(TEST_SITE.length + "data/".length)}`;
    return fs.existsSync(file) ? new Response(fs.readFileSync(file)) : new Response("", { status: 404 });
  }
  return realFetch(url, init);   // OpenRouter: the real AI
};

console.log = (...a) => process.stderr.write(a.join(" ") + "\n");   // the Worker's log lines → stderr
const env = { OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY, SITE_URL: TEST_SITE };
const results = [];
for (const question of input.questions) {
  try {
    results.push({ question, ...(await answerStats(question, env)) });
  } catch (e) {
    results.push({ question, error: e.message, cost: 0 });
  }
}
process.stdout.write(JSON.stringify(results, null, 1) + "\n");
