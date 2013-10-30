-- this database evolution changes the SQL type of tasks from TEXT to VARCHAR(1024)
BEGIN;
-- rename old table
ALTER TABLE tasks_task RENAME TO tasks_task_old;
-- create new table
CREATE TABLE "tasks_task" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "task" varchar(1024) NOT NULL,
    "done" bool NOT NULL,
    "priority" varchar(3) NOT NULL,
    "created" datetime NOT NULL,
    "edited" datetime NOT NULL,
    "finished" datetime NOT NULL,
    "due" datetime
)
;
-- copy over data
INSERT INTO tasks_task (id, user_id, task, done, priority, created, edited, finished, due)
SELECT id, user_id, task, done, priority, created, edited, finished, due
FROM tasks_task_old;
-- drop old table
DROP TABLE tasks_task_old;
COMMIT;
