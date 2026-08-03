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
List employees who were hired after their manager.

SELECT e.employee_id, e.first_name, e.last_name, e.hire_date, e.manager_id
FROM hr.employees e
WHERE e.hire_date > (
  SELECT m.hire_date 
  FROM hr.employees m 
  WHERE m.employee_id = e.manager_id
);

Question 2
List departments where every employee has a non-NULL commission_pct.

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE EXISTS (
  SELECT 1 FROM hr.employees e WHERE e.department_id = d.department_id
)
AND NOT EXISTS (
  SELECT 1 FROM hr.employees e 
  WHERE e.department_id = d.department_id 
    AND e.commission_pct IS NULL
);

Part 3: Solutions to 20 Medium Questions

M1. Employees whose salary > department average

SELECT e.employee_id, e.first_name, e.salary, e.department_id
FROM hr.employees e
WHERE e.salary > (
  SELECT AVG(salary) 
  FROM hr.employees 
  WHERE department_id = e.department_id
);

M2. Departments with at least one employee

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE EXISTS (
  SELECT 1 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
);

M3. Departments with no employees

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE NOT EXISTS (
  SELECT 1 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
);

M4. Employees who earn more than their manager

SELECT e.employee_id, e.first_name, e.salary, e.manager_id
FROM hr.employees e
WHERE e.salary > (
  SELECT m.salary 
  FROM hr.employees m 
  WHERE m.employee_id = e.manager_id
);

M5. Departments where employee count equals 0

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT COUNT(*) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) = 0;

M6. Employees hired after their manager

SELECT e.employee_id, e.first_name, e.hire_date, e.manager_id
FROM hr.employees e
WHERE e.hire_date > (
  SELECT m.hire_date 
  FROM hr.employees m 
  WHERE m.employee_id = e.manager_id
);

M7. Departments where average salary is between 5000 and 10000

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT AVG(salary) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) BETWEEN 5000 AND 10000;

M8. Employees in a department that has more than 5 people

SELECT e.employee_id, e.first_name, e.department_id
FROM hr.employees e
WHERE (
  SELECT COUNT(*) 
  FROM hr.employees e2 
  WHERE e2.department_id = e.department_id
) > 5;

M9. Departments with at least one employee earning > 10000

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE EXISTS (
  SELECT 1 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id AND e.salary > 10000
);

M10. Employees with the lowest salary in their department

SELECT e.employee_id, e.first_name, e.salary, e.department_id
FROM hr.employees e
WHERE e.salary = (
  SELECT MIN(salary) 
  FROM hr.employees e2 
  WHERE e2.department_id = e.department_id
);

M11. Departments where the maximum salary is under 15000

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT MAX(salary) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) < 15000;

M12. Employees whose manager_id is not in hr.employees (manager left)

SELECT e.employee_id, e.first_name, e.manager_id
FROM hr.employees e
WHERE e.manager_id IS NOT NULL 
  AND NOT EXISTS (
    SELECT 1 
    FROM hr.employees m 
    WHERE m.employee_id = e.manager_id
  );
  
M13. Employees holding the same job_id as their manager

SELECT e.employee_id, e.first_name, e.job_id, e.manager_id
FROM hr.employees e
WHERE e.job_id = (
  SELECT m.job_id 
  FROM hr.employees m 
  WHERE m.employee_id = e.manager_id
);

M14. Departments with at least one commissioned employee

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT COUNT(*) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id AND e.commission_pct IS NOT NULL
) > 0;

M15. Employees earning within 80% of their department's maximum salary

SELECT e.employee_id, e.first_name, e.salary, e.department_id
FROM hr.employees e
WHERE e.salary >= (
  SELECT MAX(salary) * 0.8 
  FROM hr.employees e2 
  WHERE e2.department_id = e.department_id
);

M16. Departments with no employees hired before Jan 1, 2000

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE NOT EXISTS (
  SELECT 1 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id 
    AND e.hire_date < DATE '2000-01-01'
);

M17. Employees belonging to the 'Sales' department

SELECT e.employee_id, e.first_name, e.department_id
FROM hr.employees e
WHERE 'Sales' = (
  SELECT d.department_name 
  FROM hr.departments d 
  WHERE d.department_id = e.department_id
);

M18. Departments where total salary payout exceeds 100,000

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT SUM(salary) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) > 100000;

M19. Employees who are the only person in their department

SELECT e.employee_id, e.first_name, e.department_id
FROM hr.employees e
WHERE (
  SELECT COUNT(*) 
  FROM hr.employees e2 
  WHERE e2.department_id = e.department_id
) = 1;

M20. Departments with at least one employee missing a manager

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE EXISTS (
  SELECT 1 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id AND e.manager_id IS NULL
);

Part 4: Solutions to 20 Hard Questions

H1. Employees hired strictly after their manager

SELECT e.employee_id, e.first_name, e.hire_date, e.manager_id
FROM hr.employees e
WHERE e.hire_date > (
  SELECT m.hire_date 
  FROM hr.employees m 
  WHERE m.employee_id = e.manager_id
);

H2. Departments where every employee has a non-NULL commission_pct

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE EXISTS (
  SELECT 1 FROM hr.employees e WHERE e.department_id = d.department_id
)
AND NOT EXISTS (
  SELECT 1 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id AND e.commission_pct IS NULL
);

H3. Employees with the second-highest salary in their department

SELECT e.employee_id, e.first_name, e.salary, e.department_id
FROM hr.employees e
WHERE (
  SELECT COUNT(DISTINCT e2.salary) 
  FROM hr.employees e2 
  WHERE e2.department_id = e.department_id AND e2.salary > e.salary
) = 1;

H4. Departments whose average salary exceeds the overall company average

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT AVG(salary) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) > (
  SELECT AVG(salary) 
  FROM hr.employees
);

H5. Employees earning the exact same salary as their manager

SELECT e.employee_id, e.first_name, e.salary, e.manager_id
FROM hr.employees e
WHERE e.salary = (
  SELECT m.salary 
  FROM hr.employees m 
  WHERE m.employee_id = e.manager_id
);

H6. Departments with at least 2 employees earning > 8000

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT COUNT(*) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id AND e.salary > 8000
) >= 2;

H7. Employees belonging to the department with the highest total salary

SELECT e.employee_id, e.first_name, e.salary, e.department_id
FROM hr.employees e
WHERE e.department_id IN (
  SELECT department_id 
  FROM (
    SELECT department_id, SUM(salary) AS total_sal
    FROM hr.employees 
    GROUP BY department_id 
    ORDER BY total_sal DESC
  ) 
  WHERE ROWNUM = 1
);

H8. Departments containing at least 3 distinct job positions

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT COUNT(DISTINCT job_id) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) >= 3;

H9. Employees ranked in the top 3 salaries of their department

SELECT e.employee_id, e.first_name, e.salary, e.department_id
FROM hr.employees e
WHERE (
  SELECT COUNT(DISTINCT e2.salary) 
  FROM hr.employees e2 
  WHERE e2.department_id = e.department_id AND e2.salary > e.salary
) < 3;

H10. Departments with zero assigned employees

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE NOT EXISTS (
  SELECT 1 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
);

H11. Employees whose manager is in a different department

SELECT e.employee_id, e.first_name, e.department_id, e.manager_id
FROM hr.employees e
WHERE e.manager_id IS NOT NULL 
  AND e.department_id <> (
    SELECT m.department_id 
    FROM hr.employees m 
    WHERE m.employee_id = e.manager_id
  );
  
H12. Departments where the minimum salary is strictly above 4000

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT MIN(salary) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) > 4000;

H13. The earliest hired employee(s) in each department

SELECT e.employee_id, e.first_name, e.hire_date, e.department_id
FROM hr.employees e
WHERE (
  SELECT COUNT(*) 
  FROM hr.employees e2 
  WHERE e2.department_id = e.department_id AND e2.hire_date < e.hire_date
) = 0;

H14. Departments containing exactly 5 employees

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT COUNT(*) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) = 5;

H15. Employees earning above the average salary for their job_id

SELECT e.employee_id, e.first_name, e.job_id, e.salary
FROM hr.employees e
WHERE e.salary > (
  SELECT AVG(salary) 
  FROM hr.employees e2 
  WHERE e2.job_id = e.job_id
);

H16. Departments with at least one hire on or after Jan 1, 2005

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT MAX(hire_date) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) >= DATE '2005-01-01';

H17. Managers who supervise more than 2 direct reports

SELECT e.employee_id, e.first_name, e.last_name
FROM hr.employees e
WHERE e.employee_id IN (
  SELECT manager_id 
  FROM hr.employees 
  WHERE manager_id IS NOT NULL 
  GROUP BY manager_id 
  HAVING COUNT(*) > 2
);

H18. Departments matching the highest total salary among all departments

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT SUM(salary) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) = (
  SELECT MAX(SUM(salary)) 
  FROM hr.employees 
  GROUP BY department_id
);

H19. Employees belonging to 'Sales' or 'IT' departments

SELECT e.employee_id, e.first_name, e.department_id
FROM hr.employees e
WHERE (
  SELECT d.department_name 
  FROM hr.departments d 
  WHERE d.department_id = e.department_id
) IN ('Sales', 'IT');

H20. Departments where every employee earns a commission (min 1 employee)

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE (
  SELECT COUNT(*) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id AND e.commission_pct IS NOT NULL
) = (
  SELECT COUNT(*) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) 
AND (
  SELECT COUNT(*) 
  FROM hr.employees e 
  WHERE e.department_id = d.department_id
) > 0;
