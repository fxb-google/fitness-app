// TODO: Replace this with the URL output by Terraform after deploying
const API_URL = "YOUR_API_URL_HERE";

document.addEventListener("DOMContentLoaded", () => {
    fetchWorkouts();
});

async function fetchWorkouts() {
    const container = document.getElementById("workouts-container");
    const loader = document.getElementById("loader");

    if (API_URL === "YOUR_API_URL_HERE") {
        loader.style.display = "none";
        container.innerHTML = `
            <div class="workout-card" style="text-align: center;">
                <p style="color: #fca5a5;">Configuration Error: Please update the <strong>API_URL</strong> in <code>app.js</code> with your Cloud Function URL and push the changes.</p>
            </div>
        `;
        return;
    }

    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const workouts = await response.json();
        
        // Remove loader
        loader.style.display = "none";
        
        if (workouts.length === 0) {
            container.innerHTML = `<p style="text-align: center; color: var(--text-secondary);">No workouts found in history yet.</p>`;
            return;
        }

        // Render workouts
        workouts.forEach((workout, index) => {
            const card = document.createElement("div");
            card.className = "workout-card";
            card.style.animationDelay = `${index * 0.1}s`; // Staggered animation
            
            // Format date if available
            let dateStr = "Recent Workout";
            if (workout.timestamp) {
                const date = new Date(workout.timestamp);
                dateStr = date.toLocaleDateString(undefined, { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                });
            }

            card.innerHTML = `
                <div class="workout-date">${dateStr}</div>
                <div class="workout-routine">${escapeHTML(workout.routine)}</div>
            `;
            container.appendChild(card);
        });
        
    } catch (error) {
        console.error("Failed to fetch workouts:", error);
        loader.style.display = "none";
        container.innerHTML = `
            <div class="workout-card" style="text-align: center;">
                <p style="color: #fca5a5;">Failed to load workouts. Make sure the API is deployed and accessible.</p>
            </div>
        `;
    }
}

// Utility to prevent XSS if routine text contains HTML characters
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
