"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const ELEMENT_IDS = [
  "search-form",
  "game-name",
  "tag-line",
  "search-button",
  "initial-state",
  "loading-state",
  "message-state",
  "message-text",
  "no-match-state",
  "no-match-riot-id",
  "result-section",
  "result-riot-id",
  "result-outcome",
  "result-champion",
  "result-kills",
  "result-deaths",
  "result-assists",
  "result-kda",
  "kda-note"
];

class FakeClassList {
  constructor() {
    this.values = new Set();
  }

  add(...names) {
    names.forEach((name) => this.values.add(name));
  }

  remove(...names) {
    names.forEach((name) => this.values.delete(name));
  }

  contains(name) {
    return this.values.has(name);
  }
}

class FakeElement {
  constructor() {
    this.attributes = new Map();
    this.classList = new FakeClassList();
    this.disabled = false;
    this.hidden = false;
    this.listeners = new Map();
    this.textContent = "";
    this.value = "";
  }

  addEventListener(type, listener) {
    this.listeners.set(type, listener);
  }

  setAttribute(name, value) {
    this.attributes.set(name, value);
  }

  async dispatch(type) {
    const listener = this.listeners.get(type);
    assert.ok(listener, `Missing ${type} listener`);
    await listener({preventDefault() {}});
  }
}

function createResponse({ok = true, status = 200, data}) {
  return {
    ok,
    status,
    async json() {
      return data;
    }
  };
}

function createUi(fetchMock) {
  const elements = Object.fromEntries(
    ELEMENT_IDS.map((id) => [id, new FakeElement()])
  );
  elements["loading-state"].hidden = true;
  elements["message-state"].hidden = true;
  elements["no-match-state"].hidden = true;
  elements["result-section"].hidden = true;
  elements["kda-note"].hidden = true;

  const document = {
    getElementById(id) {
      return elements[id];
    }
  };
  const context = vm.createContext({
    document,
    fetch: fetchMock
  });
  const scriptPath = path.join(
    __dirname,
    "..",
    "static",
    "js",
    "main.js"
  );
  const source = fs.readFileSync(scriptPath, "utf8");
  vm.runInContext(source, context, {filename: scriptPath});

  return {
    elements,
    async submit() {
      await elements["search-form"].dispatch("submit");
    }
  };
}

function setRiotId(ui) {
  ui.elements["game-name"].value = "TestPlayer";
  ui.elements["tag-line"].value = "JP1";
}

function matchResult(overrides = {}) {
  return {
    gameName: "TestPlayer",
    tagline: "JP1",
    latestMatch: {
      championName: "Ahri",
      win: true,
      kills: 10,
      deaths: 2,
      assists: 8,
      kda: 9,
      zeroDeaths: false,
      ...overrides
    }
  };
}

test("initial state is visible before the first search", () => {
  const ui = createUi(async () => createResponse({data: matchResult()}));

  assert.equal(ui.elements["initial-state"].hidden, false);
  assert.equal(ui.elements["loading-state"].hidden, true);
  assert.equal(ui.elements["message-state"].hidden, true);
  assert.equal(ui.elements["no-match-state"].hidden, true);
  assert.equal(ui.elements["result-section"].hidden, true);
});

test("success renders the match card and safely formats KDA", async () => {
  const requests = [];
  const ui = createUi(async (url, options) => {
    requests.push({url, options});
    return createResponse({data: matchResult()});
  });
  setRiotId(ui);

  await ui.submit();

  assert.equal(requests.length, 1);
  assert.equal(requests[0].url, "/search");
  assert.equal(ui.elements["result-section"].hidden, false);
  assert.equal(ui.elements["result-riot-id"].textContent, "TestPlayer#JP1");
  assert.equal(ui.elements["result-outcome"].textContent, "WIN");
  assert.equal(ui.elements["result-champion"].textContent, "Ahri");
  assert.equal(ui.elements["result-kda"].textContent, "9.00");
  assert.equal(ui.elements["search-button"].disabled, false);
});

test("no match and zero deaths use their dedicated states", async (t) => {
  await t.test("no match", async () => {
    const ui = createUi(async () => createResponse({
      data: {
        gameName: "TestPlayer",
        tagline: "JP1",
        latestMatch: null
      }
    }));
    setRiotId(ui);

    await ui.submit();

    assert.equal(ui.elements["no-match-state"].hidden, false);
    assert.equal(ui.elements["result-section"].hidden, true);
  });

  await t.test("zero deaths", async () => {
    const ui = createUi(async () => createResponse({
      data: matchResult({deaths: 0, kda: 18, zeroDeaths: true})
    }));
    setRiotId(ui);

    await ui.submit();

    assert.equal(ui.elements["result-kda"].textContent, "18.00");
    assert.equal(ui.elements["kda-note"].hidden, false);
    assert.match(ui.elements["kda-note"].textContent, /0デス/);
  });
});

test("input and API errors show safe messages", async (t) => {
  await t.test("empty input does not call fetch", async () => {
    let fetchCalls = 0;
    const ui = createUi(async () => {
      fetchCalls += 1;
      return createResponse({data: matchResult()});
    });

    await ui.submit();

    assert.equal(fetchCalls, 0);
    assert.equal(ui.elements["message-state"].hidden, false);
    assert.match(ui.elements["message-text"].textContent, /入力/);
  });

  const errors = [
    [429, "Riot APIの利用上限に達しました。"],
    [504, "Riot APIから時間内に応答がありませんでした。"]
  ];
  for (const [status, message] of errors) {
    await t.test(`HTTP ${status}`, async () => {
      const ui = createUi(async () => createResponse({
        ok: false,
        status,
        data: {error: {message}}
      }));
      setRiotId(ui);

      await ui.submit();

      assert.equal(ui.elements["message-state"].hidden, false);
      assert.equal(ui.elements["message-text"].textContent, message);
      assert.equal(ui.elements["result-section"].hidden, true);
    });
  }

  await t.test("network error", async () => {
    const ui = createUi(async () => {
      throw new Error("network unavailable");
    });
    setRiotId(ui);

    await ui.submit();

    assert.equal(ui.elements["message-state"].hidden, false);
    assert.match(ui.elements["message-text"].textContent, /接続できません/);
    assert.equal(ui.elements["search-button"].disabled, false);
  });
});

test("a second submission is ignored and stale results are cleared", async () => {
  let fetchCalls = 0;
  let finishFetch;
  const ui = createUi(() => {
    fetchCalls += 1;
    return new Promise((resolve) => {
      finishFetch = resolve;
    });
  });
  setRiotId(ui);
  ui.elements["result-section"].hidden = false;
  ui.elements["result-champion"].textContent = "OldChampion";

  const firstSubmission = ui.submit();
  await Promise.resolve();
  const secondSubmission = ui.submit();
  await Promise.resolve();

  assert.equal(fetchCalls, 1);
  assert.equal(ui.elements["search-button"].disabled, true);
  assert.equal(ui.elements["loading-state"].hidden, false);
  assert.equal(ui.elements["result-section"].hidden, true);
  assert.equal(ui.elements["result-champion"].textContent, "");

  finishFetch(createResponse({data: matchResult()}));
  await Promise.all([firstSubmission, secondSubmission]);
  assert.equal(ui.elements["search-button"].disabled, false);
});

test("invalid JSON and HTML-like API text do not break the UI", async (t) => {
  await t.test("invalid JSON", async () => {
    const ui = createUi(async () => ({
      ok: true,
      status: 200,
      async json() {
        throw new Error("invalid JSON");
      }
    }));
    setRiotId(ui);

    await ui.submit();

    assert.equal(ui.elements["message-state"].hidden, false);
    assert.match(ui.elements["message-text"].textContent, /読み取れません/);
  });

  await t.test("HTML-like champion name", async () => {
    const unsafeText = "<img src=x onerror=alert(1)>";
    const ui = createUi(async () => createResponse({
      data: matchResult({championName: unsafeText})
    }));
    setRiotId(ui);

    await ui.submit();

    assert.equal(ui.elements["result-champion"].textContent, unsafeText);
  });
});
