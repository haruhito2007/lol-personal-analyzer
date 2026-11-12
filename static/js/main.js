"use strict";

const form = document.getElementById("search-form");
const gameNameInput = document.getElementById("game-name");
const taglineInput = document.getElementById("tag-line");
const searchButton = document.getElementById("search-button");

const initialState = document.getElementById("initial-state");
const loadingState = document.getElementById("loading-state");
const messageState = document.getElementById("message-state");
const messageText = document.getElementById("message-text");
const noMatchState = document.getElementById("no-match-state");
const noMatchRiotId = document.getElementById("no-match-riot-id");
const resultSection = document.getElementById("result-section");

const resultRiotId = document.getElementById("result-riot-id");
const resultOutcome = document.getElementById("result-outcome");
const resultChampion = document.getElementById("result-champion");
const resultKills = document.getElementById("result-kills");
const resultDeaths = document.getElementById("result-deaths");
const resultAssists = document.getElementById("result-assists");
const resultKda = document.getElementById("result-kda");
const kdaNote = document.getElementById("kda-note");
let isSearchInProgress = false;

class UserFacingError extends Error {}

function showOnly(targetState) {
  const states = [
    initialState,
    loadingState,
    messageState,
    noMatchState,
    resultSection
  ];

  states.forEach(function(state) {
    state.hidden = state !== targetState;
  });
}

function clearResult() {
  resultRiotId.textContent = "";
  resultOutcome.textContent = "";
  resultOutcome.classList.remove("outcome--win", "outcome--lose");
  resultChampion.textContent = "";
  resultKills.textContent = "";
  resultDeaths.textContent = "";
  resultAssists.textContent = "";
  resultKda.textContent = "";
  kdaNote.textContent = "";
  kdaNote.hidden = true;
  noMatchRiotId.textContent = "";
}

function setLoading(isLoading) {
  searchButton.disabled = isLoading;
  searchButton.textContent = isLoading ? "検索中…" : "検索";
  form.setAttribute("aria-busy", String(isLoading));
}

function showError(message) {
  clearResult();
  messageText.textContent = message;
  showOnly(messageState);
}

function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isNonNegativeInteger(value) {
  return Number.isInteger(value) && value >= 0;
}

function readSafeErrorMessage(data, status) {
  if (
    isRecord(data)
    && isRecord(data.error)
    && typeof data.error.message === "string"
    && data.error.message.length > 0
  ) {
    return data.error.message;
  }

  if (status === 429) {
    return "Riot APIの利用上限に達しました。時間をおいて再度お試しください。";
  }
  if (status === 504) {
    return "Riot APIから時間内に応答がありませんでした。";
  }
  if (status >= 500) {
    return "サーバーまたはRiot APIで一時的な問題が発生しました。";
  }
  return "検索条件を確認して、もう一度お試しください。";
}

function validateSearchResult(data) {
  if (
    !isRecord(data)
    || typeof data.gameName !== "string"
    || typeof data.tagline !== "string"
  ) {
    throw new UserFacingError("検索結果の形式を確認できませんでした。");
  }

  if (data.latestMatch === null) {
    return;
  }

  const match = data.latestMatch;
  if (
    !isRecord(match)
    || typeof match.championName !== "string"
    || typeof match.win !== "boolean"
    || !isNonNegativeInteger(match.kills)
    || !isNonNegativeInteger(match.deaths)
    || !isNonNegativeInteger(match.assists)
    || typeof match.kda !== "number"
    || !Number.isFinite(match.kda)
    || match.kda < 0
    || typeof match.zeroDeaths !== "boolean"
  ) {
    throw new UserFacingError("戦績データの形式を確認できませんでした。");
  }
}

function riotIdText(data) {
  return data.gameName + "#" + data.tagline;
}

function renderSearchResult(data) {
  validateSearchResult(data);
  clearResult();

  if (data.latestMatch === null) {
    noMatchRiotId.textContent = riotIdText(data);
    showOnly(noMatchState);
    return;
  }

  const match = data.latestMatch;
  resultRiotId.textContent = riotIdText(data);
  resultOutcome.textContent = match.win ? "WIN" : "LOSE";
  resultOutcome.classList.add(
    match.win ? "outcome--win" : "outcome--lose"
  );
  resultChampion.textContent = match.championName;
  resultKills.textContent = String(match.kills);
  resultDeaths.textContent = String(match.deaths);
  resultAssists.textContent = String(match.assists);
  resultKda.textContent = match.kda.toFixed(2);

  if (match.zeroDeaths) {
    kdaNote.textContent = (
      "0デスのため、KDAはKills + Assistsの値として表示しています。"
    );
    kdaNote.hidden = false;
  }

  showOnly(resultSection);
}

form.addEventListener("submit", async function(event) {
  event.preventDefault();

  if (isSearchInProgress) {
    return;
  }

  const gameName = gameNameInput.value.trim();
  const tagline = taglineInput.value.trim();

  if (!gameName || !tagline) {
    showError("ゲーム名とタグラインを入力してください。");
    return;
  }

  isSearchInProgress = true;
  clearResult();
  showOnly(loadingState);
  setLoading(true);

  try {
    const response = await fetch("/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        gameName: gameName,
        tagline: tagline
      })
    });

    let data;
    try {
      data = await response.json();
    } catch (error) {
      throw new UserFacingError(
        "サーバーから検索結果を読み取れませんでした。"
      );
    }

    if (!response.ok) {
      throw new UserFacingError(
        readSafeErrorMessage(data, response.status)
      );
    }

    renderSearchResult(data);
  } catch (error) {
    if (error instanceof UserFacingError) {
      showError(error.message);
    } else {
      showError(
        "サーバーへ接続できませんでした。通信状態を確認してください。"
      );
    }
  } finally {
    isSearchInProgress = false;
    setLoading(false);
  }
});
