-- this database evolution changes the SQL type of label colors from 
-- VARCHAR(6) to VARCHAR(9)
BEGIN;
-- rename old table
ALTER TABLE tasks_label RENAME TO tasks_label_old;
-- create new table 
CREATE TABLE "tasks_label" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "name" varchar(48) NOT NULL,
    "created" datetime NOT NULL,
    "edited" datetime NOT NULL,
    "color" varchar(9) NOT NULL,
    "hidden" bool NOT NULL,
    "active" bool NOT NULL
)
;
-- copy over data
INSERT INTO tasks_label (id, user_id, name, created, edited, color, hidden, active)
SELECT id, user_id, name, created, edited, color, hidden, active
FROM tasks_label_old;
-- drop old table
DROP TABLE tasks_label_old;
COMMIT;
