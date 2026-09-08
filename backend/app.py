from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database import get_connection
from ai_scheduler import generate_schedule

load_dotenv()

app = Flask(__name__)
CORS(app)  # allows the frontend (served separately) to call this API


# ---------- TASKS ----------

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks ORDER BY deadline IS NULL, deadline ASC")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO tasks (title, description, category, priority, energy_level,
           duration_minutes, deadline, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            data.get("title"),
            data.get("description"),
            data.get("category"),
            data.get("priority", "Medium"),
            data.get("energy_level", "Medium"),
            data.get("duration_minutes", 30),
            data.get("deadline"),
            data.get("status", "Not Started"),
        )
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Task created"}), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE tasks SET title=%s, description=%s, category=%s, priority=%s,
           energy_level=%s, duration_minutes=%s, deadline=%s, status=%s,
           scheduled_start=%s, scheduled_end=%s WHERE id=%s""",
        (
            data.get("title"),
            data.get("description"),
            data.get("category"),
            data.get("priority"),
            data.get("energy_level"),
            data.get("duration_minutes"),
            data.get("deadline"),
            data.get("status"),
            data.get("scheduled_start"),
            data.get("scheduled_end"),
            task_id,
        )
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Task updated"})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Task deleted"})


# ---------- BEHAVIOR LOGGING ----------

@app.route("/api/behavior", methods=["POST"])
def log_behavior():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO behavior_logs (task_id, start_time, end_time, completion_status,
           focus_score, day_of_week, hour_of_day)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (
            data.get("task_id"),
            data.get("start_time"),
            data.get("end_time"),
            data.get("completion_status"),
            data.get("focus_score"),
            data.get("day_of_week"),
            data.get("hour_of_day"),
        )
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Behavior logged"}), 201


# ---------- AI SCHEDULING ----------

@app.route("/api/generate-schedule", methods=["POST"])
def generate_schedule_route():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks WHERE status != 'Done'")
    tasks = cursor.fetchall()

    cursor.execute("SELECT * FROM behavior_logs ORDER BY created_at DESC LIMIT 100")
    behavior_logs = cursor.fetchall()

    cursor.execute("SELECT * FROM preferences LIMIT 1")
    preferences = cursor.fetchone()

    cursor.close()

    if not tasks:
        conn.close()
        return jsonify({"message": "No pending tasks to schedule", "schedule": []})

    schedule = generate_schedule(tasks, behavior_logs, preferences)

    # Write the AI's suggested times back onto each task
    update_cursor = conn.cursor()
    for item in schedule:
        update_cursor.execute(
            "UPDATE tasks SET scheduled_start=%s, scheduled_end=%s WHERE id=%s",
            (item["suggested_start"], item["suggested_end"], item["task_id"])
        )
    conn.commit()
    update_cursor.close()
    conn.close()

    return jsonify({"message": "Schedule generated", "schedule": schedule})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
