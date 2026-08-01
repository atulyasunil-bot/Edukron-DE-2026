create table employees(
  emp_id number, --> 1234
  emp_name varchar(20),
  city varchar(10),
  dept varchar(10),
  salary number(15, 2)  --> 5678.75 
);

insert into employees values(1, 'hari', 'Bangalore', 'IT', 5000.00);
insert into employees values(2, 'ram', 'Bangalore',NULL,  5500.00);

insert into employees(emp_id, emp_name, city, salary) 
values(2, 'ram', 'Bangalore', 5000.00);

insert into employees
 values(3, 'rahul', 'HR', 'Chennai', 6000);

insert into employees(emp_id, emp_name, dept, city, salary) 
 values(3, 'rahul', 'hr', 'Chennai', 6000);

insert into employees values(4, 'arun', 'Bangalore', 'Hr', 5000.76),
                            (5, 'sanjay', 'Bangalore','IT',  5500.50);
select * from employees;


select count(*) as row_count from employees;

select count(*) row_count from employees;

-- display only HR employees data
SELECT * FROM Employees WHERE upper(DEPT)='HR';

--------------------------------------------------------------------------------
-- SETUP: CREATE BACKUP TABLE FIRST
--------------------------------------------------------------------------------
-- RUN THIS BEFORE PROCEEDING TO ENSURE PRODUCTION DATA IS NOT MODIFIED
CREATE TABLE hr_emp_backup AS SELECT * FROM hr.employees;


--------------------------------------------------------------------------------
-- PART 2: SELF-PRACTICE
--------------------------------------------------------------------------------

-- 1. Bulk insert into your backup table from hr.employees only for employees whose salary is greater than 10000.
INSERT INTO hr_emp_backup 
SELECT * 
FROM hr.employees 
WHERE salary > 10000;

-- 2. Update job_id for a specific employee_id in your backup table (choose an id and a valid job_id).
UPDATE hr_emp_backup 
SET job_id = 'IT_PROG' 
WHERE employee_id = 100;

-- 3. Delete rows from your backup table that you inserted for testing (e.g. where employee_id = 999).
DELETE FROM hr_emp_backup 
WHERE employee_id = 999;


--------------------------------------------------------------------------------
-- PART 3: 20 MEDIUM QUESTIONS WITH ANSWERS
--------------------------------------------------------------------------------

-- M1. Insert one row into hr_emp_backup with employee_id 990, first_name 'Test', last_name 'User', salary 4000, department_id 50.
-- Hint: INSERT INTO hr_emp_backup (employee_id, first_name, last_name, salary, department_id) VALUES (990, 'Test', 'User', 4000, 50);
INSERT INTO hr_emp_backup (employee_id, first_name, last_name, salary, department_id) 
VALUES (990, 'Test', 'User', 4000, 50);

-- M2. Update salary to 6000 for employee_id 990 in hr_emp_backup.
-- Hint: UPDATE hr_emp_backup SET salary = 6000 WHERE employee_id = 990;
UPDATE hr_emp_backup 
SET salary = 6000 
WHERE employee_id = 990;

-- M3. Delete the row where employee_id = 990 from hr_emp_backup.
-- Hint: DELETE FROM hr_emp_backup WHERE employee_id = 990;
DELETE FROM hr_emp_backup 
WHERE employee_id = 990;

-- M4. Insert into hr_emp_backup from hr.employees only for department_id 80.
-- Hint: INSERT INTO hr_emp_backup SELECT * FROM hr.employees WHERE department_id = 80;
INSERT INTO hr_emp_backup 
SELECT * FROM hr.employees 
WHERE department_id = 80;

-- M5. Update first_name to 'Updated' for employee_id 100 in hr_emp_backup.
-- Hint: UPDATE hr_emp_backup SET first_name = 'Updated' WHERE employee_id = 100;
UPDATE hr_emp_backup 
SET first_name = 'Updated' 
WHERE employee_id = 100;

-- M6. Delete all rows from hr_emp_backup where department_id = 90.
-- Hint: DELETE FROM hr_emp_backup WHERE department_id = 90;
DELETE FROM hr_emp_backup 
WHERE department_id = 90;

-- M7. Insert two rows into hr_emp_backup (e.g. employee_id 991 and 992) using two separate INSERT statements.
-- Hint: Two INSERT INTO ... VALUES ... statements.
INSERT INTO hr_emp_backup (employee_id, first_name, last_name, email, hire_date, job_id, salary) 
VALUES (991, 'Alex', 'Green', 'AGREEN', SYSDATE, 'IT_PROG', 4500);

INSERT INTO hr_emp_backup (employee_id, first_name, last_name, email, hire_date, job_id, salary) 
VALUES (992, 'Jane', 'White', 'JWHITE', SYSDATE, 'IT_PROG', 4800);

-- M8. Update salary by 5% for all employees in hr_emp_backup in department 50.
-- Hint: UPDATE hr_emp_backup SET salary = salary * 1.05 WHERE department_id = 50;
UPDATE hr_emp_backup 
SET salary = salary * 1.05 
WHERE department_id = 50;

-- M9. Delete rows from hr_emp_backup where salary is NULL.
-- Hint: DELETE FROM hr_emp_backup WHERE salary IS NULL;
DELETE FROM hr_emp_backup 
WHERE salary IS NULL;

-- M10. Insert into hr_emp_backup from hr.employees where job_id = 'SA_REP' (all columns that exist in backup).
-- Hint: INSERT INTO hr_emp_backup SELECT * FROM hr.employees WHERE job_id = 'SA_REP';
INSERT INTO hr_emp_backup 
SELECT * FROM hr.employees 
WHERE job_id = 'SA_REP';

-- M11. Update department_id to 60 for employee_id 105 in hr_emp_backup.
-- Hint: UPDATE hr_emp_backup SET department_id = 60 WHERE employee_id = 105;
UPDATE hr_emp_backup 
SET department_id = 60 
WHERE employee_id = 105;

-- M12. Delete the single row with employee_id 999 from hr_emp_backup (if it exists).
-- Hint: DELETE FROM hr_emp_backup WHERE employee_id = 999;
DELETE FROM hr_emp_backup 
WHERE employee_id = 999;

-- M13. Insert one row with employee_id 993, last_name 'Lee', first_name 'Amy', salary 5500, department_id 60.
-- Hint: INSERT with columns in any order but VALUES in same order as columns.
INSERT INTO hr_emp_backup (employee_id, last_name, first_name, salary, department_id) 
VALUES (993, 'Lee', 'Amy', 5500, 60);

-- M14. Update last_name to 'Smith' for all employees in hr_emp_backup with first_name 'John'.
-- Hint: UPDATE hr_emp_backup SET last_name = 'Smith' WHERE first_name = 'John';
UPDATE hr_emp_backup 
SET last_name = 'Smith' 
WHERE first_name = 'John';

-- M15. Delete rows from hr_emp_backup where hire_date is before 2000.
-- Hint: DELETE FROM hr_emp_backup WHERE hire_date < DATE '2000-01-01';
DELETE FROM hr_emp_backup 
WHERE hire_date < DATE '2000-01-01';

-- M16. Insert from hr.employees where salary between 5000 and 7000 into hr_emp_backup.
-- Hint: INSERT INTO hr_emp_backup SELECT * FROM hr.employees WHERE salary BETWEEN 5000 AND 7000;
INSERT INTO hr_emp_backup 
SELECT * FROM hr.employees 
WHERE salary BETWEEN 5000 AND 7000;

-- M17. Update job_id to 'IT_PROG' for one specific employee (e.g. employee_id 200) in hr_emp_backup.
-- Hint: UPDATE hr_emp_backup SET job_id = 'IT_PROG' WHERE employee_id = 200;
UPDATE hr_emp_backup 
SET job_id = 'IT_PROG' 
WHERE employee_id = 200;

-- M18. Delete rows from hr_emp_backup where commission_pct is not null.
-- Hint: DELETE FROM hr_emp_backup WHERE commission_pct IS NOT NULL;
DELETE FROM hr_emp_backup 
WHERE commission_pct IS NOT NULL;

-- M19. Insert a row with hire_date = SYSDATE for a new employee in hr_emp_backup.
-- Hint: Include hire_date in INSERT and use SYSDATE in VALUES.
INSERT INTO hr_emp_backup (employee_id, first_name, last_name, email, hire_date, job_id, salary) 
VALUES (994, 'David', 'Miller', 'DMILLER', SYSDATE, 'SA_REP', 6200);

-- M20. Update salary to 10000 for the employee with the highest employee_id in hr_emp_backup.
-- Hint: UPDATE hr_emp_backup SET salary = 10000 WHERE employee_id = (SELECT MAX(employee_id) FROM hr_emp_backup);
UPDATE hr_emp_backup 
SET salary = 10000 
WHERE employee_id = (SELECT MAX(employee_id) FROM hr_emp_backup);


--------------------------------------------------------------------------------
-- PART 3: 20 HARD QUESTIONS WITH ANSWERS
--------------------------------------------------------------------------------

-- H1. Use MERGE to sync hr_emp_backup with hr.employees: when employee_id matches, update salary and hire_date; when not matched, insert the row from hr.employees.
-- Hint: MERGE INTO hr_emp_backup t USING hr.employees s ON (t.employee_id = s.employee_id) WHEN MATCHED THEN UPDATE SET t.salary = s.salary, t.hire_date = s.hire_date WHEN NOT MATCHED THEN INSERT (...) VALUES (s....);
MERGE INTO hr_emp_backup t
USING hr.employees s
ON (t.employee_id = s.employee_id)
WHEN MATCHED THEN
  UPDATE SET t.salary = s.salary, 
             t.hire_date = s.hire_date
WHEN NOT MATCHED THEN
  INSERT (employee_id, first_name, last_name, email, phone_number, hire_date, job_id, salary, commission_pct, manager_id, department_id)
  VALUES (s.employee_id, s.first_name, s.last_name, s.email, s.phone_number, s.hire_date, s.job_id, s.salary, s.commission_pct, s.manager_id, s.department_id);

-- H2. Update hr_emp_backup so that salary equals the salary from hr.employees for the same employee_id (only for employees in department 60).
-- Hint: UPDATE hr_emp_backup e SET e.salary = (SELECT salary FROM hr.employees WHERE employee_id = e.employee_id) WHERE e.employee_id IN (SELECT employee_id FROM hr.employees WHERE department_id = 60);
UPDATE hr_emp_backup e 
SET e.salary = (SELECT salary FROM hr.employees WHERE employee_id = e.employee_id) 
WHERE e.employee_id IN (SELECT employee_id FROM hr.employees WHERE department_id = 60);

-- H3. Delete from hr_emp_backup all employees who do not exist in hr.employees (e.g. test rows).
-- Hint: DELETE FROM hr_emp_backup WHERE employee_id NOT IN (SELECT employee_id FROM hr.employees); or use NOT EXISTS.
DELETE FROM hr_emp_backup 
WHERE employee_id NOT IN (
    SELECT employee_id FROM hr.employees WHERE employee_id IS NOT NULL
);

-- H4. Insert into hr_emp_backup only employees from hr.employees whose employee_id is not already in hr_emp_backup.
-- Hint: INSERT INTO hr_emp_backup SELECT * FROM hr.employees e WHERE NOT EXISTS (SELECT 1 FROM hr_emp_backup b WHERE b.employee_id = e.employee_id);
INSERT INTO hr_emp_backup 
SELECT * FROM hr.employees e 
WHERE NOT EXISTS (
    SELECT 1 FROM hr_emp_backup b WHERE b.employee_id = e.employee_id
);

-- H5. Update hr_emp_backup: set salary to the average salary of the department (from hr.employees) for that employee's department_id.
-- Hint: SET salary = (SELECT AVG(salary) FROM hr.employees WHERE department_id = hr_emp_backup.department_id); use table alias in subquery.
UPDATE hr_emp_backup e 
SET salary = (
    SELECT AVG(salary) 
    FROM hr.employees 
    WHERE department_id = e.department_id
) 
WHERE department_id IS NOT NULL;

-- H6. Delete from hr_emp_backup the single row with the smallest employee_id.
-- Hint: DELETE FROM hr_emp_backup WHERE employee_id = (SELECT MIN(employee_id) FROM hr_emp_backup);
DELETE FROM hr_emp_backup 
WHERE employee_id = (SELECT MIN(employee_id) FROM hr_emp_backup);

-- H7. Insert into a backup table one row per department from hr.departments with department_id, department_name, and a column emp_count = 0. Then (separately) update emp_count using a subquery that counts employees per department.
-- Hint: INSERT from departments with 0; then UPDATE ... SET emp_count = (SELECT COUNT(*) FROM hr.employees e WHERE e.department_id = backup.department_id).
CREATE TABLE dept_summary AS 
SELECT department_id, department_name, 0 AS emp_count 
FROM hr.departments;

UPDATE dept_summary d 
SET emp_count = (
    SELECT COUNT(*) 
    FROM hr.employees e 
    WHERE e.department_id = d.department_id
);

-- H8. Update hr_emp_backup: set first_name and last_name from hr.employees for the same employee_id where department_id = 50.
-- Hint: UPDATE hr_emp_backup e SET (first_name, last_name) = (SELECT first_name, last_name FROM hr.employees WHERE employee_id = e.employee_id) WHERE e.department_id = 50;
UPDATE hr_emp_backup e 
SET (first_name, last_name) = (
    SELECT first_name, last_name 
    FROM hr.employees 
    WHERE employee_id = e.employee_id
) 
WHERE e.department_id = 50;

-- H9. Delete from hr_emp_backup all rows where the employee's salary in hr.employees is less than 3000 (match on employee_id).
-- Hint: DELETE FROM hr_emp_backup WHERE employee_id IN (SELECT employee_id FROM hr.employees WHERE salary < 3000);
DELETE FROM hr_emp_backup 
WHERE employee_id IN (
    SELECT employee_id FROM hr.employees WHERE salary < 3000
);

-- H10. Insert from hr.employees where department_id is in (10, 20, 30) and salary > 5000.
-- Hint: INSERT INTO hr_emp_backup SELECT * FROM hr.employees WHERE department_id IN (10,20,30) AND salary > 5000;
INSERT INTO hr_emp_backup 
SELECT * FROM hr.employees 
WHERE department_id IN (10, 20, 30) AND salary > 5000;

-- H11. Update hr_emp_backup: set department_id to 50 for all employees whose current department_id is NULL.
-- Hint: UPDATE hr_emp_backup SET department_id = 50 WHERE department_id IS NULL;
UPDATE hr_emp_backup 
SET department_id = 50 
WHERE department_id IS NULL;

-- H12. Delete from hr_emp_backup employees who have the same first_name and last_name as another row in hr_emp_backup (keep one; delete duplicates—e.g. keep min(employee_id) per name).
-- Hint: DELETE FROM hr_emp_backup a WHERE employee_id NOT IN (SELECT MIN(employee_id) FROM hr_emp_backup GROUP BY first_name, last_name) AND EXISTS (SELECT 1 FROM hr_emp_backup b WHERE b.first_name = a.first_name AND b.last_name = a.last_name AND b.employee_id < a.employee_id); or use ROW_NUMBER() in subquery.
DELETE FROM hr_emp_backup 
WHERE ROWID IN (
    SELECT rid FROM (
        SELECT ROWID AS rid, 
               ROW_NUMBER() OVER (PARTITION BY first_name, last_name ORDER BY employee_id) AS rn 
        FROM hr_emp_backup
    ) 
    WHERE rn > 1
);

-- H13. MERGE: for rows in hr.employees that exist in hr_emp_backup, update salary; for rows that do not exist, insert. Use department_id 80 only.
-- Hint: MERGE USING (SELECT * FROM hr.employees WHERE department_id = 80) s ON ...
MERGE INTO hr_emp_backup t
USING (SELECT * FROM hr.employees WHERE department_id = 80) s
ON (t.employee_id = s.employee_id)
WHEN MATCHED THEN
  UPDATE SET t.salary = s.salary
WHEN NOT MATCHED THEN
  INSERT (employee_id, first_name, last_name, email, hire_date, job_id, salary, department_id)
  VALUES (s.employee_id, s.first_name, s.last_name, s.email, s.hire_date, s.job_id, s.salary, s.department_id);

-- H14. Update hr_emp_backup so salary is increased by 10% only for employees whose salary in hr.employees is below the company average.
-- Hint: UPDATE hr_emp_backup SET salary = salary * 1.10 WHERE employee_id IN (SELECT employee_id FROM hr.employees WHERE salary < (SELECT AVG(salary) FROM hr.employees));
UPDATE hr_emp_backup 
SET salary = salary * 1.10 
WHERE employee_id IN (
    SELECT employee_id 
    FROM hr.employees 
    WHERE salary < (SELECT AVG(salary) FROM hr.employees)
);

-- H15. Delete from hr_emp_backup where hire_date is the earliest in the table (only one row).
-- Hint: DELETE FROM hr_emp_backup WHERE hire_date = (SELECT MIN(hire_date) FROM hr_emp_backup);
DELETE FROM hr_emp_backup 
WHERE hire_date = (SELECT MIN(hire_date) FROM hr_emp_backup);

-- H16. Insert into hr_emp_backup from hr.employees only for employees who are managers (employee_id in (SELECT manager_id FROM hr.employees)).
-- Hint: INSERT ... SELECT * FROM hr.employees WHERE employee_id IN (SELECT manager_id FROM hr.employees WHERE manager_id IS NOT NULL);
INSERT INTO hr_emp_backup 
SELECT * FROM hr.employees 
WHERE employee_id IN (
    SELECT manager_id FROM hr.employees WHERE manager_id IS NOT NULL
);

-- H17. Update last_name in hr_emp_backup to UPPER(last_name) for all rows.
-- Hint: UPDATE hr_emp_backup SET last_name = UPPER(last_name);
UPDATE hr_emp_backup 
SET last_name = UPPER(last_name);

-- H18. Delete from hr_emp_backup the top 5 highest salary earners (use subquery with ROWNUM or FETCH).
-- Hint: DELETE FROM hr_emp_backup WHERE employee_id IN (SELECT employee_id FROM (SELECT employee_id FROM hr_emp_backup ORDER BY salary DESC FETCH FIRST 5 ROWS ONLY));
DELETE FROM hr_emp_backup 
WHERE employee_id IN (
    SELECT employee_id 
    FROM hr_emp_backup 
    ORDER BY salary DESC 
    FETCH FIRST 5 ROWS ONLY
);

-- H19. Insert from hr.employees where job_id like 'SA%' and commission_pct is not null.
-- Hint: INSERT INTO hr_emp_backup SELECT * FROM hr.employees WHERE job_id LIKE 'SA%' AND commission_pct IS NOT NULL;
INSERT INTO hr_emp_backup 
SELECT * FROM hr.employees 
WHERE job_id LIKE 'SA%' AND commission_pct IS NOT NULL;

-- H20. Update hr_emp_backup: set salary to the max salary in the same department (from hr.employees) for each employee.
-- Hint: UPDATE hr_emp_backup e SET salary = (SELECT MAX(salary) FROM hr.employees WHERE department_id = e.department_id) WHERE department_id IS NOT NULL;
UPDATE hr_emp_backup e 
SET salary = (
    SELECT MAX(salary) 
    FROM hr.employees 
    WHERE department_id = e.department_id
) 
WHERE department_id IS NOT NULL;

--------------------------------------------------------------------------------
-- COMMIT CHANGES
--------------------------------------------------------------------------------
COMMIT;