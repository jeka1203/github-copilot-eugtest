document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const participantsList = document.getElementById("participants-list");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Show participants for the selected activity (default: first activity)
      const selectedActivity = activitySelect.value || Object.keys(activities)[0];
      if (selectedActivity) {
        renderParticipants(selectedActivity, activities[selectedActivity].participants);
      } else {
        renderParticipants(null, []);
      }

      activitySelect.addEventListener('change', () => {
        const act = activitySelect.value;
        if (act && activities[act]) {
          renderParticipants(act, activities[act].participants);
        } else {
          renderParticipants(null, []);
        }
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  function renderParticipants(activity, participants) {
    participantsList.innerHTML = '';
    if (!activity || !participants || participants.length === 0) {
      participantsList.innerHTML = '<li>Keine Teilnehmer</li>';
      return;
    }
    participants.forEach(email => {
      const li = document.createElement('li');
      li.style.display = 'flex';
      li.style.alignItems = 'center';
      const nameSpan = document.createElement('span');
      nameSpan.textContent = email;
      const deleteBtn = document.createElement('button');
      deleteBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M5.5 5.5a.5.5 0 0 1 .5.5v5a.5.5 0 0 1-1 0v-5a.5.5 0 0 1 .5-.5zm2.5.5a.5.5 0 0 0-1 0v5a.5.5 0 0 0 1 0v-5zm2 .5a.5.5 0 0 1 .5-.5.5.5 0 0 1 .5.5v5a.5.5 0 0 1-1 0v-5z"/><path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1 0-2h3.5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1H14a1 1 0 0 1 1 1zm-3-1a.5.5 0 0 0-.5-.5h-2a.5.5 0 0 0-.5.5H2.5a.5.5 0 0 0-.5.5V4h12V2.5a.5.5 0 0 0-.5-.5H11.5z"/></svg>';
      deleteBtn.title = 'Teilnehmer entfernen';
      deleteBtn.style.background = 'none';
      deleteBtn.style.border = 'none';
      deleteBtn.style.cursor = 'pointer';
      deleteBtn.style.marginLeft = '8px';
      deleteBtn.addEventListener('click', () => {
        unregisterParticipant(activity, email);
      });
      li.appendChild(nameSpan);
      li.appendChild(deleteBtn);
      participantsList.appendChild(li);
    });
  }

  async function unregisterParticipant(activity, email) {
    try {
      const response = await fetch(`/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`, {
        method: 'POST',
      });
      const result = await response.json();
      if (response.ok && result.success) {
        fetchActivities();
      } else {
        alert(result.detail || 'Teilnehmer konnte nicht entfernt werden.');
      }
    } catch (error) {
      alert('Fehler beim Entfernen des Teilnehmers.');
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
        fetchActivities();
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
