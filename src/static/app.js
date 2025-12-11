const API_BASE = "";

async function loadActivities() {
  try {
    const response = await fetch(`${API_BASE}/activities`);
    const activities = await response.json();
    displayActivities(activities);
    populateActivitySelect(activities);
  } catch (error) {
    console.error("Error loading activities:", error);
    document.getElementById("activities-list").innerHTML =
      "<p>Error loading activities. Please try again later.</p>";
  }
}

function displayActivities(activities) {
  const container = document.getElementById("activities-list");
  container.innerHTML = "";

  Object.entries(activities).forEach(([name, details]) => {
    if (typeof details !== "object" || !details.description) return;

    const card = document.createElement("div");
    card.className = "activity-card";

    const participants = details.participants || [];
    const participantsList =
      participants.length > 0
        ? participants.map((p) => `<li>${p}</li>`).join("")
        : "<li><em>No participants yet</em></li>";

    card.innerHTML = `
      <h4>${name}</h4>
      <p><strong>Description:</strong> ${details.description}</p>
      <p><strong>Schedule:</strong> ${details.schedule}</p>
      <p><strong>Capacity:</strong> ${participants.length}/${details.max_participants}</p>
      <div class="participants-section">
        <strong>Participants:</strong>
        <ul>
          ${participantsList}
        </ul>
      </div>
    `;
    container.appendChild(card);
  });
}

function populateActivitySelect(activities) {
  const select = document.getElementById("activity");
  Object.keys(activities).forEach((name) => {
    if (
      typeof activities[name] === "object" &&
      activities[name].description
    ) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      select.appendChild(option);
    }
  });
}

document.getElementById("signup-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value;
  const activity = document.getElementById("activity").value;
  const messageDiv = document.getElementById("message");

  if (!activity) {
    showMessage("Please select an activity", "error");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
      { method: "POST" }
    );
    const data = await response.json();

    if (response.ok) {
      showMessage("Successfully signed up!", "success");
      document.getElementById("signup-form").reset();
      loadActivities();
    } else {
      showMessage(data.detail || "Sign up failed", "error");
    }
  } catch (error) {
    showMessage("An error occurred. Please try again.", "error");
    console.error("Error:", error);
  }
});

function showMessage(text, type) {
  const messageDiv = document.getElementById("message");
  messageDiv.textContent = text;
  messageDiv.className = `message ${type}`;
}

loadActivities();
