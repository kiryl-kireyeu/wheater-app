const startDateInput = document.querySelector("#start-date");
const endDateInput = document.querySelector("#end-date");
const getDataButton = document.querySelector("#get-data");
const statusMessage = document.querySelector("#status-message");
const tableBody = document.querySelector("#scores-table-body");

getDataButton.addEventListener("click", () => {
  void fetchScores();
});

async function fetchScores() {
  setLoadingState();

  try {
    const response = await fetch(buildScoresUrl());
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "Could not load weather scores.");
    }

    renderScores(payload);
  } catch (error) {
    renderError(error);
  }
}

function buildScoresUrl() {
  const params = new URLSearchParams();

  // Empty date inputs intentionally defer to the API default: yesterday.
  appendDateParam(params, "start_date", startDateInput.value);
  appendDateParam(params, "end_date", endDateInput.value);

  const query = params.toString();
  return query ? `/api/v1/cities-scores?${query}` : "/api/v1/cities-scores";
}

function appendDateParam(params, name, value) {
  if (value) {
    params.set(name, value);
  }
}

function setLoadingState() {
  getDataButton.disabled = true;
  statusMessage.textContent = "Loading weather scores...";
  tableBody.innerHTML = '<tr><td colspan="8" class="empty-state">Loading...</td></tr>';
}

function renderScores(payload) {
  getDataButton.disabled = false;
  statusMessage.textContent = `Showing scores for ${payload.start_date} to ${payload.end_date}.`;

  if (!payload.cities.length) {
    tableBody.innerHTML = '<tr><td colspan="8" class="empty-state">No cities returned.</td></tr>';
    return;
  }

  tableBody.innerHTML = payload.cities.map(renderScoreRow).join("");
}

function renderScoreRow(city) {
  return `
    <tr>
      <td>${city.rank}</td>
      <td>${escapeHtml(city.city)}</td>
      <td>${escapeHtml(city.country)}</td>
      <td><strong>${formatNumber(city.scores.total)}</strong></td>
      <td>${formatNumber(city.averages.temperature_2m)}°C</td>
      <td>${formatNumber(city.averages.wind_speed_10m)} m/s</td>
      <td>${formatNumber(city.averages.relative_humidity_2m)}%</td>
      <td>${formatNumber(city.averages.cloud_cover)}%</td>
    </tr>
  `;
}

function renderError(error) {
  getDataButton.disabled = false;
  statusMessage.textContent = error.message;
  tableBody.innerHTML =
    '<tr><td colspan="8" class="empty-state">Weather scores could not be loaded.</td></tr>';
}

function formatNumber(value) {
  return Number(value).toFixed(2);
}

function escapeHtml(value) {
  const element = document.createElement("span");
  element.textContent = value;
  return element.innerHTML;
}
