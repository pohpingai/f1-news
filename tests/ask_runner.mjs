// Runs Ask questions through the REAL Worker code (worker/ask-worker.js), but with the TEST news
// instead of the live website. Used by tests/report_card.py — you don't need to run this yourself.
//
// Input (stdin):  {"data_dir": "/tmp/...", "questions": ["...", "..."]}
// Output (stdout): JSON list of the Worker's answers, one per question.

import fs from "node:fs";
import { answerQuestion } from "../worker/ask-worker.js";

const input = JSON.parse(fs.readFileSync(0, "utf8"));
const TEST_SITE = "https://test-site.invalid/";

// When the Worker asks for the website's saved news, give it the test files instead.
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  url = String(url);
  if (url.startsWith(TEST_SITE)) {
    const file = `${input.data_dir}/${url.slice(TEST_SITE.length + "data/".length)}`;
    return fs.existsSync(file) ? new Response(fs.readFileSync(file)) : new Response("", { status: 404 });
  }
  return realFetch(url, init);   // OpenRouter: the real AI
};

const env = { OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY, SITE_URL: TEST_SITE };
const results = [];
for (const question of input.questions) {
  try {
    results.push({ question, ...(await answerQuestion(question, env)) });
  } catch (e) {
    results.push({ question, error: e.message, cost: 0 });
  }
}
process.stdout.write(JSON.stringify(results));
