const API_BASE = "http://127.0.0.1:5000/api";

const taskForm = document.getElementById("taskForm");
const taskList = document.getElementById("taskList");
const generateBtn = document.getElementById("generateBtn");

let calendar; // will hold the FullCalendar instance

// ---------- INITIAL LOAD ----------

document.addEventListener("DOMContentLoaded", () => {
  initCalendar();
  loadTasks();
});

function initCalendar() {
  const calendarEl = document.getElementById("calendar");
  calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "timeGridWeek",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "timeGridWeek,dayGridMonth"
    },
    events: []
  });
  calendar.render();
}

// ---------- LOAD + RENDER TASKS ----------

async function loadTasks() {
  const res = await fetch(`${API_BASE}/tasks`);
  const tasks = await res.json();

  taskList.innerHTML = "";
  const calendarEvents = [];

  tasks.forEach(task => {
    const li = document.createElement("li");
    li.className = `priority-${task.priority}`;
    li.innerHTML = `
      <span>${task.title} — ${task.status}</span>
      <span class="task-actions">
        <button onclick="markDone(${task.id})">Done</button>
        <button onclick="deleteTask(${task.id})">Delete</button>
      </span>
    `;
    taskList.appendChild(li);

    if (task.scheduled_start && task.scheduled_end) {
      calendarEvents.push({
        id: String(task.id),
        title: task.title,
        start: task.scheduled_start,
        end: task.scheduled_end
      });
    }
  });

  calendar.removeAllEvents();
  calendarEvents.forEach(ev => calendar.addEvent(ev));
}

// ---------- ADD TASK ----------

taskForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const newTask = {
    title: document.getElementById("title").value,
    description: document.getElementById("description").value,
    category: document.getElementById("category").value,
    priority: document.getElementById("priority").value,
    energy_level: document.getElementById("energy_level").value,
    duration_minutes: Number(document.getElementById("duration_minutes").value),
    deadline: document.getElementById("deadline").value || null,
    status: "Not Started"
  };

  await fetch(`${API_BASE}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(newTask)
  });

  taskForm.reset();
  loadTasks();
});

// ---------- MARK DONE (also logs behavior) ----------

async function markDone(taskId) {
  const focusScore = prompt("Rate your focus on this task (1-5):", "3");
  if (focusScore === null) return;

  const now = new Date();

  await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: "Done" })
  });

  await fetch(`${API_BASE}/behavior`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      task_id: taskId,
      start_time: now.toISOString(),
      end_time: now.toISOString(),
      completion_status: "completed",
      focus_score: Number(focusScore),
      day_of_week: now.toLocaleDateString("en-US", { weekday: "long" }),
      hour_of_day: now.getHours()
    })
  });

  loadTasks();
}

// ---------- DELETE TASK ----------

async function deleteTask(taskId) {
  await fetch(`${API_BASE}/tasks/${taskId}`, { method: "DELETE" });
  loadTasks();
}

// ---------- GENERATE AI SCHEDULE ----------

generateBtn.addEventListener("click", async () => {
  generateBtn.textContent = "Thinking...";
  generateBtn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/generate-schedule`, { method: "POST" });
    const data = await res.json();
    console.log("AI schedule reasoning:", data.schedule);
    await loadTasks();
  } catch (err) {
    alert("Could not generate schedule. Is the backend running?");
    console.error(err);
  }

  generateBtn.textContent = "Generate Smart Schedule";
  generateBtn.disabled = false;
});