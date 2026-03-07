document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Store activities data
  let activities = {};

  // Function to render activities from data
  function renderActivities() {
    // Clear loading message
    activitiesList.innerHTML = "";
    // Reset select dropdown
    activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

    // Populate activities list
    Object.entries(activities).forEach(([name, details]) => {
      const activityCard = document.createElement("div");
      activityCard.className = "activity-card";

      const spotsLeft = details.max_participants - details.participants.length;

      const participantsList = details.participants.length > 0 
        ? details.participants.map(p => `<li><span>${p}</span><button class="delete-participant" data-activity="${name}" data-email="${p}" title="Remove participant">✕</button></li>`).join('') 
        : '<li><em>No participants yet</em></li>';

      activityCard.innerHTML = `
        <h4>${name}</h4>
        <p>${details.description}</p>
        <p><strong>Schedule:</strong> ${details.schedule}</p>
        <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        <div class="participants-section">
          <h5>Participants</h5>
          <ul class="participants-list">
            ${participantsList}
          </ul>
        </div>
      `;

      activitiesList.appendChild(activityCard);

      // Add option to select dropdown
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      activitySelect.appendChild(option);
    });

    // Add event delegation for delete buttons
    activitiesList.addEventListener("click", handleDeleteParticipant);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      activities = await response.json();
      renderActivities();
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle participant deletion
  async function handleDeleteParticipant(event) {
    if (event.target.classList.contains("delete-participant")) {
      const activityName = event.target.getAttribute("data-activity");
      const email = event.target.getAttribute("data-email");

      try {
        const response = await fetch(
          `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
          {
            method: "DELETE",
          }
        );

        const result = await response.json();

        if (response.ok) {
          // Update activities array
          activities[activityName].participants = activities[activityName].participants.filter(p => p !== email);
          renderActivities();
        } else {
          alert(result.detail || "Failed to unregister participant");
        }
      } catch (error) {
        alert("Failed to unregister participant. Please try again.");
        console.error("Error unregistering participant:", error);
      }
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Update activities array
        activities[activity].participants.push(email);
        renderActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
