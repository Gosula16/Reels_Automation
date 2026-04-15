const resultBox = document.getElementById("resultBox");
const automationStatus = document.getElementById("automationStatus");
const manualForm = document.getElementById("manualForm");
const runDailyButton = document.getElementById("runDailyButton");
const refreshStatusButton = document.getElementById("refreshStatusButton");

async function loadStatus() {
  automationStatus.textContent = "Loading status...";
  const response = await fetch("/automation/status");
  const data = await response.json();
  automationStatus.innerHTML = `
    <div><strong>Enabled:</strong> ${data.enabled}</div>
    <div><strong>Timezone:</strong> ${data.timezone}</div>
    <div><strong>Post times:</strong> ${data.post_times.join(", ") || "Not set"}</div>
    <div><strong>Topic seeds:</strong> ${data.topic_seeds.join(", ") || "Not set"}</div>
    <div><strong>Recent runs:</strong></div>
    <div>${data.recent_runs.length ? data.recent_runs.map(run =>
      `<div><strong>${run.status}</strong> ${run.scheduled_for}<br>${run.topic}<br>${run.detail}</div>`
    ).join("<hr>") : "No runs yet."}</div>
  `;
}

async function showJsonResponse(response) {
  const data = await response.json();
  resultBox.textContent = JSON.stringify(data, null, 2);
}

manualForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultBox.textContent = "Running manual reel pipeline...";
  const formData = new FormData(manualForm);
  const payload = {
    topic: formData.get("topic"),
    goal: formData.get("goal"),
    style: formData.get("style"),
    call_to_action: formData.get("call_to_action"),
    duration_seconds: Number(formData.get("duration_seconds")),
  };
  const response = await fetch("/pipelines/reels/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await showJsonResponse(response);
  await loadStatus();
});

runDailyButton.addEventListener("click", async () => {
  resultBox.textContent = "Running today’s scheduled batch...";
  const response = await fetch("/automation/run-daily", { method: "POST" });
  await showJsonResponse(response);
  await loadStatus();
});

refreshStatusButton.addEventListener("click", loadStatus);

loadStatus().catch((error) => {
  automationStatus.textContent = `Failed to load status: ${error.message}`;
});
