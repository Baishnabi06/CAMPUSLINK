const API_BASE_URL = "http://127.0.0.1:8000";

async function callApi(path) {
  const resultEl = document.getElementById("result");
  resultEl.textContent = "Loading...";
  try {
    const response = await fetch(`${API_BASE_URL}${path}`);
    const data = await response.json();
    resultEl.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    resultEl.textContent = `Request failed: ${error.message}`;
  }
}

document.getElementById("checkBackendBtn").addEventListener("click", () => {
  callApi("/api/health");
});

document.getElementById("checkDbBtn").addEventListener("click", () => {
  callApi("/api/health/db");
});