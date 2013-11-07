-- add notes to tasks 
BEGIN;
ALTER TABLE tasks_task ADD COLUMN "notes" text;
COMMIT;
