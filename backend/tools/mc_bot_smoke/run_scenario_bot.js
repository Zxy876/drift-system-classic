const fs = require('fs');
const path = require('path');
const mineflayer = require('mineflayer');

const host = process.env.MC_HOST || '127.0.0.1';
const port = Number(process.env.MC_PORT || 25565);
const username = process.env.MC_USERNAME || 'DriftScenarioBot';
const auth = process.env.MC_AUTH || 'offline';
const version = process.env.MC_VERSION || false;
const timeoutMs = Number(process.env.MC_CONNECT_TIMEOUT_MS || 30000);
const actionDelayMs = Number(process.env.MC_ACTION_DELAY_MS || 2500);
const settleMs = Number(process.env.MC_SETTLE_MS || 5000);
const scenarioFile = process.env.MC_SCENARIO_FILE || '';

if (!scenarioFile) {
  console.error('[bot-scenario] missing MC_SCENARIO_FILE');
  process.exit(10);
}

const scenarioPath = path.resolve(scenarioFile);
if (!fs.existsSync(scenarioPath)) {
  console.error(`[bot-scenario] scenario file not found: ${scenarioPath}`);
  process.exit(11);
}

let actions;
try {
  const raw = fs.readFileSync(scenarioPath, 'utf8');
  const parsed = JSON.parse(raw);
  actions = Array.isArray(parsed) ? parsed : [];
} catch (err) {
  console.error(`[bot-scenario] failed to parse scenario: ${String(err && err.message ? err.message : err)}`);
  process.exit(12);
}

if (actions.length === 0) {
  console.error('[bot-scenario] scenario is empty');
  process.exit(13);
}

const startedAt = Date.now();
let settled = false;
let sent = 0;
let received = 0;

function elapsed() {
  return Date.now() - startedAt;
}

function done(code, message) {
  if (settled) return;
  settled = true;
  console.log(`[bot-scenario] ${message} (sent=${sent} received=${received} elapsed=${elapsed()}ms)`);
  process.exit(code);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

console.log(`[bot-scenario] connecting host=${host} port=${port} username=${username} auth=${auth} scenario=${scenarioPath}`);

const bot = mineflayer.createBot({
  host,
  port,
  username,
  auth,
  version,
  connectTimeout: timeoutMs,
});

bot.on('messagestr', (msg) => {
  received += 1;
  console.log(`[server] ${msg}`);
});

bot.on('chat', (name, msg) => {
  received += 1;
  console.log(`[chat] <${name}> ${msg}`);
});

bot.once('login', () => {
  console.log('[bot-scenario] login event');
});

bot.once('spawn', async () => {
  console.log('[bot-scenario] spawn event');
  try {
    for (let i = 0; i < actions.length; i += 1) {
      const action = actions[i] || {};
      const type = String(action.type || 'chat').toLowerCase();
      const delay = Number(action.delayMs || action.delay || actionDelayMs);

      if (type === 'wait') {
        const ms = Number(action.ms || delay || actionDelayMs);
        console.log(`[bot-scenario] step=${i + 1}/${actions.length} wait ${ms}ms`);
        await sleep(ms);
        continue;
      }

      if (type !== 'chat') {
        console.log(`[bot-scenario] step=${i + 1}/${actions.length} skip unsupported type=${type}`);
        await sleep(delay);
        continue;
      }

      const text = String(action.text || '').trim();
      if (!text) {
        console.log(`[bot-scenario] step=${i + 1}/${actions.length} skip empty chat text`);
        await sleep(delay);
        continue;
      }

      console.log(`[bot-scenario] step=${i + 1}/${actions.length} chat: ${text}`);
      bot.chat(text);
      sent += 1;
      await sleep(delay);
    }

    await sleep(settleMs);
    try {
      bot.quit('scenario complete');
    } catch (err) {
      console.log(`[bot-scenario] quit error: ${String(err && err.message ? err.message : err)}`);
    }
    done(0, 'scenario complete');
  } catch (err) {
    done(20, `scenario execution failed: ${String(err && err.message ? err.message : err)}`);
  }
});

bot.on('kicked', (reason) => {
  done(2, `kicked: ${typeof reason === 'string' ? reason : JSON.stringify(reason)}`);
});

bot.on('end', (reason) => {
  if (!settled) {
    done(3, `connection ended before scenario complete: ${String(reason || 'unknown')}`);
  }
});

bot.on('error', (err) => {
  done(4, `error: ${String(err && err.message ? err.message : err)}`);
});

setTimeout(() => {
  done(5, 'timeout waiting for scenario completion');
}, timeoutMs + Math.max(settleMs, actions.length * actionDelayMs) + 15000);
