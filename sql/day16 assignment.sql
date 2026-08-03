-- Create the employee table
CREATE TABLE employees (
    emp_id NUMBER PRIMARY KEY,
    emp_name VARCHAR2(10) NOT NULL,
    manager_id NUMBER
);

-- Insert 10 rows of data (including top manager, middle managers, and employees)
INSERT INTO employees (emp_id, emp_name, manager_id) VALUES (100, 'King', NULL);
INSERT INTO employees (emp_id, emp_name, manager_id) VALUES (101, 'Kochhar', 100);
INSERT INTO employees (emp_id, emp_name, manager_id) VALUES (102, 'De Haan', 100);
INSERT INTO employees (emp_id, emp_name, manager_id) VALUES (103, 'Hunold', 102);
INSERT INTO employees (emp_id, emp_name, manager_id) VALUES (104, 'Ernst', 103);
INSERT INTO employees (emp_id, emp_name, manager_id) VALUES (105, 'Austin', 103);
INSERT INTO employees (emp_id, emp_name, manager_id) VALUES (106, 'Pataballa', 103);
INSERT INTO employees (emp_id, emp_name, manager_id) VALUES (107, 'Lorentz', 103);
INSERT INTO employees (emp_id, emp_name, manager_id) VALUES (108, 'Greenberg', 101);
INSERT INTO employees (emp_id, emp_name, manager_id) VALUES (109, 'Faviet', 108);

-- display emp_id, emp_name, manager_id, manager_name


select e1.emp_id, e1.emp_name, e1.manager_id, e2.emp_name as manager_name from 
employees e1 left join employees e2
on e1.manager_id = e2.emp_id;

-- removing duplicates

create table managers (id NUMBER, name varchar(10));
insert into managers values(1, 'charan'), (1, 'charan'), (1, 'charan'),
                            (2, 'rahul'), (2, 'rahul'), (3, 'sanjay');
-- method1

create table managers_new as 
select distinct id, name from managers;


-- select * from managers_new;
drop table managers;
rename managers_new to managers;
select * from managers;


--method2
delete from managers m where rowid not in (
select min(rowid) from managers group by id, name);

select * from managers;

Part 2: Self-Practice Solutions

Question 1
Add a UNIQUE constraint on (department_id, job_id) to a copy table of hr.employees.

CREATE TABLE hr_emp_copy AS SELECT * FROM hr.employees;
ALTER TABLE hr_emp_copy 
ADD CONSTRAINT uk_dept_job UNIQUE (department_id, job_id);

Question 2
Disable a constraint on your copy table, then enable it again.

ALTER TABLE hr_emp_copy 
DISABLE CONSTRAINT uk_dept_job;

ALTER TABLE hr_emp_copy 
ENABLE CONSTRAINT uk_dept_job;

Part 3: Solutions to 20 Medium Questions

M1. Create a table with PRIMARY KEY on employee_id

CREATE TABLE hr_emp_copy (
  employee_id NUMBER(6) PRIMARY KEY,
  first_name  VARCHAR2(20),
  last_name   VARCHAR2(25)
);

M2. Add FOREIGN KEY (department_id) REFERENCES hr.departments(department_id)

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT fk_dept 
FOREIGN KEY (department_id) REFERENCES hr.departments(department_id);

M3. Add CHECK constraint: salary > 0

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT chk_sal CHECK (salary > 0);

M4. Add NOT NULL to first_name

ALTER TABLE hr_emp_copy 
MODIFY first_name NOT NULL;

M5. Add UNIQUE constraint on email column

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT uk_email UNIQUE (email);

M6. Name the primary key constraint pk_emp_copy

CREATE TABLE hr_emp_copy (
  employee_id NUMBER(6),
  first_name  VARCHAR2(20),
  CONSTRAINT pk_emp_copy PRIMARY KEY (employee_id)
);

M7. Drop a CHECK constraint by name

ALTER TABLE hr_emp_copy 
DROP CONSTRAINT chk_sal;

M8. Create table with composite PRIMARY KEY (department_id, employee_id)

CREATE TABLE hr_emp_dept_copy (
  department_id NUMBER(4),
  employee_id   NUMBER(6),
  first_name    VARCHAR2(20),
  CONSTRAINT pk_dept_emp PRIMARY KEY (department_id, employee_id)
);

M9. Add CHECK: hire_date <= SYSDATE (using DATE literal for deterministic constraint)

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT chk_hire_date CHECK (hire_date >= DATE '1900-01-01');

M10. Add FK manager_id REFERENCES hr.employees(employee_id)

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT fk_mgr 
FOREIGN KEY (manager_id) REFERENCES hr.employees(employee_id);

M11. List constraint names on hr.employees

SELECT constraint_name, constraint_type 
FROM user_constraints 
WHERE table_name = 'EMPLOYEES';

M12. Add CHECK: commission_pct BETWEEN 0 AND 1

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT chk_comm CHECK (commission_pct BETWEEN 0 AND 1);

M13. Add UNIQUE (first_name, last_name)

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT uk_fullname UNIQUE (first_name, last_name);

M14. Modify column to NOT NULL

ALTER TABLE hr_emp_copy 
MODIFY last_name NOT NULL;

M15. Create table with PK and two FKs (department_id, manager_id)

CREATE TABLE hr_emp_copy (
  employee_id   NUMBER(6) PRIMARY KEY,
  department_id NUMBER(4),
  manager_id    NUMBER(6),
  CONSTRAINT fk_emp_dept FOREIGN KEY (department_id) REFERENCES hr.departments(department_id),
  CONSTRAINT fk_emp_mgr  FOREIGN KEY (manager_id) REFERENCES hr.employees(employee_id)
);

M16. Drop foreign key constraint by name

ALTER TABLE hr_emp_copy 
DROP CONSTRAINT fk_emp_dept;

M17. Add CHECK: employee_id > 0

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT chk_emp_id CHECK (employee_id > 0);

M18. Find constraint type (P/R/U/C) for hr.departments

SELECT constraint_name, constraint_type 
FROM user_constraints 
WHERE table_name = 'DEPARTMENTS';

M19. Add DEFAULT 0 for a numeric column and add NOT NULL

ALTER TABLE hr_emp_copy 
MODIFY salary DEFAULT 0 NOT NULL;

M20. Add named CHECK constraint

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT chk_salary_min CHECK (salary >= 1000);

Part 4: Solutions to 20 Hard Questions

H1. Create table with PK, FK to departments, CHECK salary > 0, and commission_pct BETWEEN 0 AND 1

CREATE TABLE hr_emp_copy (
  employee_id    NUMBER(6) PRIMARY KEY,
  salary         NUMBER(8,2),
  commission_pct NUMBER(2,2),
  department_id  NUMBER(4),
  CONSTRAINT fk_dept_h1 FOREIGN KEY (department_id) REFERENCES hr.departments(department_id),
  CONSTRAINT chk_sal_h1 CHECK (salary > 0),
  CONSTRAINT chk_comm_h1 CHECK (commission_pct BETWEEN 0 AND 1)
);

H2. Add FK with ON DELETE SET NULL

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT fk_dept_null 
FOREIGN KEY (department_id) REFERENCES hr.departments(department_id) 
ON DELETE SET NULL;
H3. Disable constraint, do DML, re-enable constraint

ALTER TABLE hr_emp_copy DISABLE CONSTRAINT chk_sal;
UPDATE hr_emp_copy SET salary = 5000 WHERE salary IS NULL;
ALTER TABLE hr_emp_copy ENABLE CONSTRAINT chk_sal;

H4. Add CHECK referencing two columns: salary >= commission_pct * 1000
ALTER TABLE hr_emp_copy 
ADD CONSTRAINT chk_sal_comm CHECK (salary >= NVL(commission_pct, 0) * 1000);

H5. Create table with DEFERRABLE constraint
CREATE TABLE hr_emp_copy (
  employee_id NUMBER(6),
  CONSTRAINT pk_emp_def PRIMARY KEY (employee_id) DEFERRABLE INITIALLY DEFERRED
);

H6. List all constraints and their columns for hr.employees

SELECT c.constraint_name, c.constraint_type, cc.column_name, cc.position
FROM user_constraints c
JOIN user_cons_columns cc ON c.constraint_name = cc.constraint_name
WHERE c.table_name = 'EMPLOYEES'
ORDER BY c.constraint_name, cc.position;

H7. Add FK from copy table to hr.employees(employee_id) for manager_id (handling NULLs)

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT fk_mgr_nullable 
FOREIGN KEY (manager_id) REFERENCES hr.employees(employee_id);

H8. Add CHECK: hire_date >= DATE '1990-01-01'

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT chk_hire_1990 CHECK (hire_date >= DATE '1990-01-01');

H9. Create unique constraint on (department_id, job_id) for a copy table

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT uk_dept_job UNIQUE (department_id, job_id);

H10. Drop all CHECK constraints on a table

SELECT 'ALTER TABLE ' || table_name || ' DROP CONSTRAINT ' || constraint_name || ';' AS drop_script
FROM user_constraints
WHERE table_name = 'HR_EMP_COPY' AND constraint_type = 'C';

H11. Add NOT NULL to a column containing NULLs

UPDATE hr_emp_copy SET department_id = 10 WHERE department_id IS NULL;
ALTER TABLE hr_emp_copy MODIFY department_id NOT NULL;

H12. Add FK to self (manager_id references employee_id)
ALTER TABLE hr_emp_copy 
ADD CONSTRAINT fk_self_mgr 
FOREIGN KEY (manager_id) REFERENCES hr_emp_copy(employee_id);

H13. Create table with PK, two FKs, and one CHECK
CREATE TABLE hr_emp_copy (
  employee_id   NUMBER(6) PRIMARY KEY,
  department_id NUMBER(4),
  manager_id    NUMBER(6),
  salary        NUMBER(8,2),
  CONSTRAINT fk_dept_h13 FOREIGN KEY (department_id) REFERENCES hr.departments(department_id),
  CONSTRAINT fk_mgr_h13  FOREIGN KEY (manager_id) REFERENCES hr.employees(employee_id),
  CONSTRAINT chk_sal_h13 CHECK (salary > 0)
);

H14. Find tables that reference hr.departments via Foreign Keys

SELECT table_name, constraint_name 
FROM user_constraints 
WHERE r_constraint_name IN (
  SELECT constraint_name 
  FROM user_constraints 
  WHERE table_name = 'DEPARTMENTS' AND constraint_type = 'P'
);

H15. Add CHECK using a function: LENGTH(first_name) >= 2

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT chk_fname_len CHECK (LENGTH(first_name) >= 2);

H16. Enable constraint with VALIDATE (check existing data)

ALTER TABLE hr_emp_copy 
ENABLE VALIDATE CONSTRAINT chk_sal;

H17. Create composite UNIQUE (department_id, job_id) and composite FK (department_id references departments)

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT uk_dept_job UNIQUE (department_id, job_id);

ALTER TABLE hr_emp_copy 
ADD CONSTRAINT fk_dept_ref FOREIGN KEY (department_id) REFERENCES hr.departments(department_id);

H18. Enforce maximum salary rule using a trigger (since subqueries aren't allowed in CHECK constraints)

CREATE OR REPLACE TRIGGER trg_chk_max_salary
BEFORE INSERT OR UPDATE OF salary ON hr_emp_copy
FOR EACH ROW
DECLARE
  v_max_sal NUMBER;
BEGIN
  SELECT MAX(salary) INTO v_max_sal FROM hr.employees;
  IF :NEW.salary > v_max_sal THEN
    RAISE_APPLICATION_ERROR(-20001, 'Salary exceeds maximum company salary.');
  END IF;
END;

H19. Rename a constraint

ALTER TABLE hr_emp_copy 
RENAME CONSTRAINT chk_sal TO chk_emp_salary;

H20. List constraint type and search_condition for CHECK constraints

SELECT constraint_name, constraint_type, search_condition 
FROM user_constraints 
WHERE table_name = 'HR_EMP_COPY' AND constraint_type = 'C';
