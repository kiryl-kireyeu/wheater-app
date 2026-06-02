const startDateInput = document.querySelector("#start-date");
const endDateInput = document.querySelector("#end-date");
const getDataButton = document.querySelector("#get-data");
const statusMessage = document.querySelector("#status-message");
const tableBody = document.querySelector("#scores-table-body");

getDataButton.addEventListener("click", () => {
  void fetchScores();
});

/** Fetch ranked scores from the API and update the table state. */
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

/** Build the API URL from optional date inputs. */
function buildScoresUrl() {
  const params = new URLSearchParams();

  // Empty date inputs intentionally defer to the API default: yesterday.
  appendDateParam(params, "start_date", startDateInput.value);
  appendDateParam(params, "end_date", endDateInput.value);

  const query = params.toString();
  return query ? `/api/v1/cities-scores?${query}` : "/api/v1/cities-scores";
}

/** Append a date query parameter only when the user provided a value. */
function appendDateParam(params, name, value) {
  if (value) {
    params.set(name, value);
  }
}

/** Disable the form and show a temporary loading table row. */
function setLoadingState() {
  getDataButton.disabled = true;
  statusMessage.textContent = "Loading weather scores...";
  tableBody.innerHTML = '<tr><td colspan="8" class="empty-state">Loading...</td></tr>';
}

/** Render a successful API response into the weather scores table. */
function renderScores(payload) {
  getDataButton.disabled = false;
  statusMessage.textContent = `Showing scores for ${payload.start_date} to ${payload.end_date}.`;

  if (!payload.cities.length) {
    tableBody.innerHTML = '<tr><td colspan="8" class="empty-state">No cities returned.</td></tr>';
    return;
  }

  tableBody.innerHTML = payload.cities.map(renderScoreRow).join("");
}

/** Render one city score row. */
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

/** Render a user-facing error state without clearing the page shell. */
function renderError(error) {
  getDataButton.disabled = false;
  statusMessage.textContent = error.message;
  tableBody.innerHTML =
    '<tr><td colspan="8" class="empty-state">Weather scores could not be loaded.</td></tr>';
}

/** Format numeric API values consistently for table display. */
function formatNumber(value) {
  return Number(value).toFixed(2);
}

/** Escape API-provided strings before inserting table HTML. */
function escapeHtml(value) {
  const element = document.createElement("span");
  element.textContent = value;
  return element.innerHTML;
}
