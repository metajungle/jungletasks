-- this database evolution changes the SQL type of tasks from TEXT to VARCHAR(1024)
BEGIN;
-- rename old table
ALTER TABLE tasks_task RENAME TO tasks_task_old;
-- create new table
CREATE TABLE "tasks_task" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "task" varchar(1024) NOT NULL,
    "completed" bool NOT NULL,
    "priority" varchar(3) NOT NULL,
    "date_created" datetime NOT NULL,
    "date_edited" datetime NOT NULL,
    "date_completed" datetime,
    "date_due" datetime
)
;
-- copy over data
INSERT INTO tasks_task (id, user_id, task, completed, priority, date_created, date_edited, date_completed, date_due)
SELECT id, user_id, task, done, priority, created, edited, finished, due
FROM tasks_task_old;
-- drop old table
DROP TABLE tasks_task_old;
COMMIT;
