
--------------------------------------------------------------------------------
-- SETUP: CREATE BACKUP TABLE FIRST
--------------------------------------------------------------------------------
-- RUN THIS FIRST TO ENSURE PRODUCTION DATA IS NOT MODIFIED
CREATE TABLE hr_emp_backup AS SELECT * FROM hr.employees;


--------------------------------------------------------------------------------
-- PART 2: SELF-PRACTICE
--------------------------------------------------------------------------------

-- 1. Write a script that performs two separate UPDATEs on your backup table, then performs one ROLLBACK (no savepoint). What happens to both updates?
UPDATE hr_emp_backup 
SET salary = salary + 500 
WHERE department_id = 50;

UPDATE hr_emp_backup 
SET job_id = 'IT_PROG' 
WHERE employee_id = 100;
ROLLBACK;

-- 2. List the object privileges a user would need to be able to query hr.employees (e.g. SELECT). If you cannot grant, describe what you would run as the table owner.
GRANT SELECT ON hr.employees TO target_user;


--------------------------------------------------------------------------------
-- PART 3: 20 MEDIUM QUESTIONS WITH ANSWERS
--------------------------------------------------------------------------------

-- M1. After updating one row in hr_emp_backup, issue COMMIT. Then run a SELECT to verify.
-- Hint: UPDATE ... ; COMMIT; SELECT * FROM hr_emp_backup WHERE ... ;
UPDATE hr_emp_backup 
SET salary = 7000 
WHERE employee_id = 100;
COMMIT;
SELECT * FROM hr_emp_backup WHERE employee_id = 100;

-- M2. Update two different rows in hr_emp_backup, then ROLLBACK. Verify both changes are undone.
-- Hint: Two UPDATEs; ROLLBACK; SELECT to confirm original values.
UPDATE hr_emp_backup SET salary = 9000 WHERE employee_id = 101;
UPDATE hr_emp_backup SET salary = 9500 WHERE employee_id = 102;
ROLLBACK;
SELECT employee_id, salary FROM hr_emp_backup WHERE employee_id IN (101, 102);

-- M3. Create a savepoint after one UPDATE, then do another UPDATE, then ROLLBACK TO SAVEPOINT. What is the state before COMMIT?
-- Hint: First update remains in transaction; second is undone.
UPDATE hr_emp_backup SET salary = 8000 WHERE employee_id = 103;
SAVEPOINT sp1;
UPDATE hr_emp_backup SET salary = 8500 WHERE employee_id = 104;
ROLLBACK TO SAVEPOINT sp1;
-- At this point: Employee 103 has salary 8000 (pending commit); Employee 104 retains original salary.

-- M4. Write the SQL to GRANT SELECT on hr.employees to a role named hr_select_role (run as HR if you have access).
-- Hint: CREATE ROLE hr_select_role; GRANT SELECT ON hr.employees TO hr_select_role;
CREATE ROLE hr_select_role;
GRANT SELECT ON hr.employees TO hr_select_role;

-- M5. Revoke SELECT on hr.departments from a user (use a placeholder user name).
-- Hint: REVOKE SELECT ON hr.departments FROM some_user;
REVOKE SELECT ON hr.departments FROM app_user;

-- M6. In one transaction, update salary for employee_id 100, create savepoint sp1, update salary for employee_id 101, then ROLLBACK TO sp1, then COMMIT. Who has the new salary?
-- Hint: Only employee 100; 101's update was rolled back.
UPDATE hr_emp_backup SET salary = 25000 WHERE employee_id = 100;
SAVEPOINT sp1;

UPDATE hr_emp_backup SET salary = 18000 WHERE employee_id = 101;

ROLLBACK TO SAVEPOINT sp1;
COMMIT;
-- M7. Grant INSERT and UPDATE on hr_emp_backup to a role (your own backup table in your schema).
-- Hint: GRANT INSERT, UPDATE ON hr_emp_backup TO your_role;
CREATE ROLE hr_writer_role;
GRANT INSERT, UPDATE ON hr_emp_backup TO hr_writer_role;


-- M8. Run UPDATE on hr_emp_backup for 3 rows, then ROLLBACK. Check SQL%ROWCOUNT after UPDATE (in PL/SQL) and after ROLLBACK.
-- Hint: After UPDATE, SQL%ROWCOUNT = 3; after ROLLBACK, the updates are undone.
BEGIN
    UPDATE hr_emp_backup 
    SET salary = salary * 1.10 
    WHERE department_id = 90;
    DBMS_OUTPUT.PUT_LINE('Rows Updated: ' || SQL%ROWCOUNT);
    ROLLBACK;
END;
/
-- M9. Create a role hr_report and grant it SELECT on hr.employees and hr.departments.
-- Hint: CREATE ROLE hr_report; GRANT SELECT ON hr.employees TO hr_report; GRANT SELECT ON hr.departments TO hr_report;
CREATE ROLE hr_report;
GRANT SELECT ON hr.employees TO hr_report;
GRANT SELECT ON hr.departments TO hr_report;
-- M10. After a DELETE from hr_emp_backup, do not COMMIT. In another session (or same), can you see the deleted rows before COMMIT?
-- Hint: In the same session, the rows are gone; in another session with read consistency, they may still be visible until the first session commits.
DELETE FROM hr_emp_backup WHERE department_id = 60;
-- Session 1: Rows are invisible (deleted).
-- Session 2: Rows remain VISIBLE due to Oracle Read Consistency (Undo segments).
ROLLBACK; 

-- M11. Write a script: UPDATE one row, SAVEPOINT a, UPDATE another row, SAVEPOINT b, UPDATE a third row, ROLLBACK TO SAVEPOINT a, then COMMIT. Which rows are updated permanently?
-- Hint: Only the first update; second and third are rolled back.
UPDATE hr_emp_backup SET salary = 5000 WHERE employee_id = 105;
SAVEPOINT a;
UPDATE hr_emp_backup SET salary = 6000 WHERE employee_id = 106;
SAVEPOINT b;
UPDATE hr_emp_backup SET salary = 7000 WHERE employee_id = 107;
ROLLBACK TO SAVEPOINT a;
COMMIT;

-- M12. Grant SELECT on hr.employees to a user. Then revoke it.
-- Hint: GRANT SELECT ON hr.employees TO user1; REVOKE SELECT ON hr.employees FROM user1;
GRANT SELECT ON hr.employees TO dev_user;
REVOKE SELECT ON hr.employees FROM dev_user;


-- M13. In a single transaction, run two UPDATEs on hr_emp_backup (different departments). Then COMMIT. How many rows are committed?
-- Hint: All rows updated by both UPDATEs are committed together.
UPDATE hr_emp_backup SET salary = salary * 1.05 WHERE department_id = 10;
UPDATE hr_emp_backup SET salary = salary * 1.05 WHERE department_id = 20;
COMMIT;

-- M14. Create a role and grant it only SELECT on hr.departments (no other tables).
-- Hint: CREATE ROLE dept_reader; GRANT SELECT ON hr.departments TO dept_reader;
CREATE ROLE dept_reader;
GRANT SELECT ON hr.departments TO dept_reader;


-- M15. After an UPDATE, run SELECT to verify, then ROLLBACK. Why is ROLLBACK useful here?
-- Hint: To discard the change if the SELECT showed something wrong.
UPDATE hr_emp_backup SET salary = 99999 WHERE department_id = 50;
SELECT * FROM hr_emp_backup WHERE department_id = 50;
ROLLBACK;

-- M16. Use two savepoints: after first UPDATE (sp1), after second UPDATE (sp2). Then ROLLBACK TO sp1. What happens to the second update?
-- Hint: The second update is undone; first remains in the transaction.
UPDATE hr_emp_backup SET salary = 3000 WHERE employee_id = 108;
SAVEPOINT sp1;

UPDATE hr_emp_backup SET salary = 4000 WHERE employee_id = 109;
SAVEPOINT sp2;
ROLLBACK TO SAVEPOINT sp1;
ROLLBACK;

-- M17. List the privileges you would need (as DBA) to allow a user to create a table and insert into hr.employees (conceptual).
-- Hint: CREATE TABLE (system), INSERT on hr.employees (object), and possibly quota on tablespace.
GRANT CREATE TABLE TO test_user;
GRANT INSERT ON hr.employees TO test_user;

-- M18. Run UPDATE on hr_emp_backup, then COMMIT. Run another UPDATE, then ROLLBACK. Is the first update still committed?
-- Hint: Yes; ROLLBACK only undoes the second update.
UPDATE hr_emp_backup SET salary = 12000 WHERE employee_id = 110;
COMMIT;

UPDATE hr_emp_backup SET salary = 15000 WHERE employee_id = 110;
ROLLBACK;

-- M19. Grant a role to a user: GRANT hr_reader TO app_user; What can app_user do?
-- Hint: Whatever privileges were granted to hr_reader (e.g. SELECT on hr.employees and hr.departments).
GRANT hr_reader TO app_user;

-- M20. In one transaction, DELETE 5 rows from hr_emp_backup, then ROLLBACK. Verify the 5 rows are back.
-- Hint: DELETE ... WHERE ... ; ROLLBACK; SELECT COUNT(*) should show rows restored.
DELETE FROM hr_emp_backup WHERE department_id = 30;
ROLLBACK;
SELECT COUNT(*) FROM hr_emp_backup WHERE department_id = 30;


--------------------------------------------------------------------------------
-- PART 3: 20 HARD QUESTIONS WITH ANSWERS
--------------------------------------------------------------------------------

-- H1. Implement a "try and undo" pattern: UPDATE 10 rows, check SQL%ROWCOUNT, if not 10 then ROLLBACK else COMMIT (in PL/SQL).
-- Hint: BEGIN UPDATE ... ; IF SQL%ROWCOUNT != 10 THEN ROLLBACK; ELSE COMMIT; END IF; END;
BEGIN
    UPDATE hr_emp_backup 
    SET salary = salary + 1000 
    WHERE department_id = 80;
    
    IF SQL%ROWCOUNT != 10 THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('Expected 10 rows, but updated ' || SQL%ROWCOUNT || '. Transaction rolled back.');
    ELSE
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Successfully updated 10 rows and committed.');
    END IF;
END;
/


-- H2. Create two savepoints. After three UPDATEs (one after each savepoint), ROLLBACK TO the first savepoint. Then COMMIT. Which updates are permanent?
-- Hint: Only the first update (before first savepoint) is committed; the other two are rolled back.
UPDATE hr_emp_backup SET salary = 5000 WHERE employee_id = 111; -- Update 1
SAVEPOINT sp1;

UPDATE hr_emp_backup SET salary = 6000 WHERE employee_id = 112; -- Update 2
SAVEPOINT sp2;

UPDATE hr_emp_backup SET salary = 7000 WHERE employee_id = 113; -- Update 3

ROLLBACK TO SAVEPOINT sp1;
COMMIT;

-- H3. Write a script that grants SELECT, INSERT, UPDATE on hr.employees to role hr_hrw (read and write), then revokes UPDATE only.
-- Hint: GRANT SELECT, INSERT, UPDATE ON hr.employees TO hr_hrw; REVOKE UPDATE ON hr.employees FROM hr_hrw;
CREATE ROLE hr_hrw;
GRANT SELECT, INSERT, UPDATE ON hr.employees TO hr_hrw;
REVOKE UPDATE ON hr.employees FROM hr_hrw;


-- H4. In a transaction, update salary for department 50, savepoint, update salary for department 60, rollback to savepoint, update salary for department 70, commit. Which departments are updated?
-- Hint: 50 and 70; 60 is rolled back.
UPDATE hr_emp_backup SET salary = salary * 1.02 WHERE department_id = 50;
SAVEPOINT sp_dept;

UPDATE hr_emp_backup SET salary = salary * 1.02 WHERE department_id = 60;
ROLLBACK TO SAVEPOINT sp_dept;

UPDATE hr_emp_backup SET salary = salary * 1.02 WHERE department_id = 70;
COMMIT;

-- H5. Explain: Session A updates a row and does not commit. Session B updates the same row. What happens?
-- Hint: Session B blocks (waits) until A commits or rolls back; then B proceeds or gets a conflict depending on isolation.
UPDATE hr_emp_backup 
SET salary = 30000 
WHERE employee_id = 100;
-- STEP 2: SESSION B ATTEMPTS TO UPDATE THE SAME ROW
UPDATE hr_emp_backup 
SET salary = 25000 
WHERE employee_id = 100;
COMMIT;
ROLLBACK;

-- H6. Create a role that has SELECT on hr.employees and hr.departments, and grant that role to two different users (placeholder names).
-- Hint: CREATE ROLE r; GRANT SELECT ON hr.employees TO r; GRANT SELECT ON hr.departments TO r; GRANT r TO u1; GRANT r TO u2;
CREATE ROLE hr_reader_role;
GRANT SELECT ON hr.employees TO hr_reader_role;
GRANT SELECT ON hr.departments TO hr_reader_role;
GRANT hr_reader_role TO user_alpha;
GRANT hr_reader_role TO user_beta;


-- H7. Run UPDATE on hr_emp_backup, then create savepoint, then DELETE 1 row, then ROLLBACK TO SAVEPOINT, then COMMIT. Is the row deleted?
-- Hint: No; the DELETE was rolled back. Only the UPDATE is committed.
UPDATE hr_emp_backup SET salary = salary + 100 WHERE employee_id = 114;
SAVEPOINT sp_del;

DELETE FROM hr_emp_backup WHERE employee_id = 115;

ROLLBACK TO SAVEPOINT sp_del;
COMMIT;

-- H8. What object privilege is needed to allow a user to run SELECT * FROM hr.employees?
-- Hint: SELECT on hr.employees (and possibly on schema/table if qualified).

GRANT SELECT ON hr.employees TO target_user;

-- H9. In one transaction, INSERT one row, SAVEPOINT, INSERT another row, ROLLBACK TO SAVEPOINT, COMMIT. How many rows are in the table?
-- Hint: One (the first insert); the second insert was rolled back.
INSERT INTO hr_emp_backup (employee_id, last_name, email, hire_date, job_id) 
VALUES (995, 'Test1', 'T1@mail.com', SYSDATE, 'IT_PROG');
SAVEPOINT sp_ins;

INSERT INTO hr_emp_backup (employee_id, last_name, email, hire_date, job_id) 
VALUES (996, 'Test2', 'T2@mail.com', SYSDATE, 'IT_PROG');

ROLLBACK TO SAVEPOINT sp_ins;
COMMIT;

-- H10. Grant SELECT on hr.employees to a role, then grant that role to a user. Then revoke the role from the user. Can the user still query hr.employees?
-- Hint: No; revoking the role removes the privilege.
CREATE ROLE hr_temp_role;
GRANT SELECT ON hr.employees TO hr_temp_role;
GRANT hr_temp_role TO analyst_user;

REVOKE hr_temp_role FROM analyst_user;

-- H11. Write a transaction that updates 3 rows in hr_emp_backup, then rolls back only the last update using a savepoint.
-- Hint: UPDATE row1; UPDATE row2; SAVEPOINT s; UPDATE row3; ROLLBACK TO s; COMMIT;
UPDATE hr_emp_backup SET salary = 5000 WHERE employee_id = 116;
UPDATE hr_emp_backup SET salary = 6000 WHERE employee_id = 117;
SAVEPOINT sp_third;

UPDATE hr_emp_backup SET salary = 7000 WHERE employee_id = 118;

ROLLBACK TO SAVEPOINT sp_third;
COMMIT;


-- H12. If you REVOKE SELECT ON hr.employees FROM a role, do users who were granted that role lose access immediately?
-- Hint: Yes (or at next reconnection depending on DB); the role no longer has the privilege.
REVOKE SELECT ON hr.employees FROM hr_temp_role;

-- H13. Run DELETE from hr_emp_backup where department_id = 50, then SAVEPOINT, then DELETE where department_id = 60, then ROLLBACK TO SAVEPOINT, then COMMIT. Which departments' rows are deleted?
-- Hint: Only department 50; department 60 delete was rolled back.
DELETE FROM hr_emp_backup WHERE department_id = 50;
SAVEPOINT sp_dept_del;

DELETE FROM hr_emp_backup WHERE department_id = 60;

ROLLBACK TO SAVEPOINT sp_dept_del;
COMMIT;

-- H14. Create a role with SELECT on hr.employees. Grant the role to user A. Grant the role to role B. Grant role B to user C. Can user C query hr.employees?
-- Hint: Yes, if role B was granted the first role (role chain); or grant SELECT to role B and grant B to C.
CREATE ROLE role_a;
CREATE ROLE role_b;

GRANT SELECT ON hr.employees TO role_a;
GRANT role_a TO role_b; -- Role inheritance / Role chaining
GRANT role_b TO user_c;

-- H15. In a single transaction, run five UPDATEs with savepoints between each. Roll back to the second savepoint. How many UPDATEs are still in the transaction?
-- Hint: Two (the first two updates); the third, fourth, fifth are undone.
UPDATE hr_emp_backup SET salary = 1000 WHERE employee_id = 119;
SAVEPOINT s1;
UPDATE hr_emp_backup SET salary = 2000 WHERE employee_id = 120;
SAVEPOINT s2;
UPDATE hr_emp_backup SET salary = 3000 WHERE employee_id = 121;
SAVEPOINT s3;
UPDATE hr_emp_backup SET salary = 4000 WHERE employee_id = 122;
SAVEPOINT s4;
UPDATE hr_emp_backup SET salary = 5000 WHERE employee_id = 123;

ROLLBACK TO SAVEPOINT s2;

ROLLBACK;


-- H16. Revoke INSERT on hr.employees from a role. Does this affect users who have the role?
-- Hint: Yes; they lose INSERT on hr.employees through that role.
REVOKE INSERT ON hr.employees FROM hr_writer_role;

-- H17. Update hr_emp_backup in a transaction but do not commit. Open another session and try to SELECT the same rows. Explain read consistency.
-- Hint: The second session sees the old values until the first commits; Oracle read consistency.
UPDATE hr_emp_backup SET salary = 99999 WHERE employee_id = 100;
ROLLBACK;


-- H18. Write a script that uses a savepoint before a risky UPDATE, then checks a condition (e.g. SQL%ROWCOUNT), and rolls back to the savepoint if the condition is not met.
-- Hint: SAVEPOINT before; UPDATE; IF condition THEN COMMIT; ELSE ROLLBACK TO SAVEPOINT; END IF;
DECLARE
    v_updated_count NUMBER;
BEGIN
    SAVEPOINT pre_update_check;
    
    UPDATE hr_emp_backup 
    SET salary = salary * 1.50 
    WHERE department_id = 10;
    
    v_updated_count := SQL%ROWCOUNT;
    
    IF v_updated_count > 5 THEN
        -- Safety check: don't update if more than 5 rows are affected
        ROLLBACK TO SAVEPOINT pre_update_check;
        DBMS_OUTPUT.PUT_LINE('Safety breach: Too many rows affected (' || v_updated_count || '). Rolled back.');
    ELSE
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Update successful: ' || v_updated_count || ' rows modified.');
    END IF;
END;
/


-- H19. Grant SELECT ON hr.employees to user X. User X creates a view on hr.employees. Can user X grant SELECT on that view to user Y without having GRANT OPTION on hr.employees?
-- Hint: Typically yes for the view (user X owns the view); Y can query the view. X cannot grant Y direct SELECT on hr.employees unless X has GRANT OPTION.
-- 1. Executed as HR
GRANT SELECT ON hr.employees TO user_x WITH GRANT OPTION;

-- 2. Executed as USER_X (Now this will succeed!)
GRANT SELECT ON user_x.emp_view TO user_y;

-- H20. In one transaction: INSERT row 1, SAVEPOINT a, INSERT row 2, SAVEPOINT b, DELETE row 1, ROLLBACK TO SAVEPOINT b, COMMIT. What rows exist?
-- Hint: Both rows (row 1 and row 2); the DELETE was rolled back when we rolled back to b. So after COMMIT we have both inserts.
INSERT INTO hr_emp_backup (employee_id, last_name, email, hire_date, job_id) 
VALUES (997, 'Row1', 'R1@mail.com', SYSDATE, 'IT_PROG');
SAVEPOINT a;

INSERT INTO hr_emp_backup (employee_id, last_name, email, hire_date, job_id) 
VALUES (998, 'Row2', 'R2@mail.com', SYSDATE, 'IT_PROG');
SAVEPOINT b;

DELETE FROM hr_emp_backup WHERE employee_id = 997;

ROLLBACK TO SAVEPOINT b;
COMMIT;

--------------------------------------------------------------------------------
-- COMMIT ALL PENDING CHANGES
--------------------------------------------------------------------------------
COMMIT;