-- Run this once to create the database and all tables
CREATE DATABASE IF NOT EXISTS ai_task_assistant DEFAULT CHARACTER SET utf8mb4;
USE ai_task_assistant;

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    priority ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
    energy_level ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
    duration_minutes INT DEFAULT 30,
    deadline DATETIME,
    status ENUM('Not Started', 'In Progress', 'Done') DEFAULT 'Not Started',
    scheduled_start DATETIME,
    scheduled_end DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE behavior_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT,
    start_time DATETIME,
    end_time DATETIME,
    completion_status VARCHAR(50),
    focus_score INT,
    day_of_week VARCHAR(20),
    hour_of_day INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
);

CREATE TABLE preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    work_start TIME DEFAULT '09:00:00',
    work_end TIME DEFAULT '18:00:00',
    break_minutes INT DEFAULT 15
);

INSERT INTO preferences (work_start, work_end, break_minutes) VALUES ('09:00:00', '18:00:00', 15);