create table employees(
  emp_id number, --> 1234
  emp_name varchar(20),
  city varchar(10),
  dept varchar(10),
  salary number(15, 2)  --> 5678.75 
);
insert into employees values(1, 'hari', 'Bangalore', 'IT', 5000.00);
insert into employees values(2, 'ram', 'Bangalore',NULL,  5500.00);
insert into employees(emp_id, emp_name, city, salary) 
values(2, 'ram', 'Bangalore', 5000.00);
insert into employees
 values(3, 'rahul', 'HR', 'Chennai', 6000);
insert into employees(emp_id, emp_name, dept, city, salary) 
 values(3, 'rahul', 'hr', 'Chennai', 6000);
insert into employees values(4, 'arun', 'Bangalore', 'Hr', 5000.76),
                            (5, 'sanjay', 'Bangalore','IT',  5500.50);
select * from employees;
select count(*) as row_count from employees;
select count(*) row_count from employees;
-- display only HR employees data
SELECT * FROM Employees WHERE upper(DEPT)='HR';  this is the table


## 20 Medium Questions — Answers

**M1.** All employees + department_name, including no-department employees.

SELECT e.employee_id, e.first_name, e.last_name, d.department_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id;

---

**M2.** Employee + manager name (self-join).

SELECT e.first_name, e.last_name,
       m.first_name AS mgr_first_name, m.last_name AS mgr_last_name
FROM hr.employees e
LEFT JOIN hr.employees m ON e.manager_id = m.employee_id;
---

**M3.** Departments + employee count, including 0-employee departments.

SELECT d.department_id, d.department_name, COUNT(e.employee_id) AS emp_count
FROM hr.departments d
LEFT JOIN hr.employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;

COUNT(e.employee_id) ignores NULLs, so unmatched departments correctly show 0.
---

**M4.** Employees with no department.

SELECT e.employee_id, e.first_name, e.last_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id
WHERE d.department_id IS NULL;
---

**M5.** Employee + department_name with default text.

SELECT e.first_name, e.last_name,
       COALESCE(d.department_name, 'No Dept') AS department_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id;
---

**M6.** Departments + total salary, including 0 for empty departments.
SELECT d.department_id, d.department_name, NVL(SUM(e.salary), 0) AS total_salary
FROM hr.departments d
LEFT JOIN hr.employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;
---

**M7.** Employee + manager name (manager optional).
SELECT e.first_name, e.last_name, m.first_name AS mgr_first, m.last_name AS mgr_last
FROM hr.employees e
LEFT JOIN hr.employees m ON e.manager_id = m.employee_id;
---

**M8.** Departments with no employees.
SELECT d.department_id, d.department_name
FROM hr.departments d
LEFT JOIN hr.employees e ON d.department_id = e.department_id
WHERE e.employee_id IS NULL;
---

**M9.** Employee_id, name, department_id, department_name — including null department_id.
SELECT e.employee_id, e.first_name, e.department_id, d.department_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id;
---

**M10.** Departments + employee count (0 shown where none).
SELECT d.department_id, d.department_name, COUNT(e.employee_id) AS emp_count
FROM hr.departments d
LEFT JOIN hr.employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;
---

**M11.** Employee + manager, with explicit aliasing.
SELECT e.employee_id, e.first_name, e.last_name,
       m.first_name AS mgr_first_name, m.last_name AS mgr_last_name
FROM hr.employees e
LEFT JOIN hr.employees m ON e.manager_id = m.employee_id;
---

**M12.** Employees + department_name, no filtering on department match.
SELECT e.first_name, e.last_name, d.department_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id;
---

**M13.** Department_id, name, employee count.
SELECT d.department_id, d.department_name, COUNT(e.employee_id) AS emp_count
FROM hr.departments d
LEFT JOIN hr.employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;
---

**M14.** Employee_id, salary, department_name with NVL default.
SELECT e.employee_id, e.salary,
       NVL(d.department_name, 'Unassigned') AS department_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id;
---

**M15.** Employee + manager's employee_id and last_name.
SELECT e.employee_id, e.first_name, e.last_name,
       m.employee_id AS mgr_emp_id, m.last_name AS mgr_last_name
FROM hr.employees e
LEFT JOIN hr.employees m ON e.manager_id = m.employee_id;
---

**M16.** Departments + min salary.
SELECT d.department_id, d.department_name, MIN(e.salary) AS min_salary
FROM hr.departments d
LEFT JOIN hr.employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;
---

**M17.** Employees who have a manager, + manager's first_name.
SELECT e.first_name, e.last_name, m.first_name AS mgr_first_name
FROM hr.employees e
JOIN hr.employees m ON e.manager_id = m.employee_id;
---

**M18.** Employee_id, name, department_name, including no-department employees.
SELECT e.employee_id, e.first_name, d.department_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id;
---

**M19.** Departments + average salary, including empty departments.
SELECT d.department_id, d.department_name, AVG(e.salary) AS avg_salary
FROM hr.departments d
LEFT JOIN hr.employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;
---

**M20.** Employee + department_name, default 'N/A'.
SELECT e.first_name, e.last_name,
       COALESCE(d.department_name, 'N/A') AS department_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id;

---

## 20 Hard Questions — Answers

**H1.** Two-level hierarchy: employee → manager → manager's manager.

SELECT e.first_name AS emp_name,
       m.first_name AS mgr_name,
       m2.first_name AS mgr_mgr_name
FROM hr.employees e
LEFT JOIN hr.employees m ON e.manager_id = m.employee_id
LEFT JOIN hr.employees m2 ON m.manager_id = m2.employee_id;

---

**H2.** Departments with no employees, via NOT EXISTS.

SELECT d.department_id, d.department_name
FROM hr.departments d
WHERE NOT EXISTS (
    SELECT 1 FROM hr.employees e WHERE e.department_id = d.department_id
);
---

**H3.** All employees and all departments — FULL OUTER JOIN.
SELECT e.employee_id, e.first_name, d.department_id, d.department_name
FROM hr.employees e
FULL OUTER JOIN hr.departments d ON e.department_id = d.department_id;
---

**H4.** Employee + own department_name + manager's department_name.

SELECT e.first_name, e.last_name,
       d.department_name AS emp_dept,
       dm.department_name AS mgr_dept
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
LEFT JOIN hr.employees m ON e.manager_id = m.employee_id
LEFT JOIN hr.departments dm ON m.department_id = dm.department_id;

---

**H5.** Employees earning more than their manager.

SELECT e.first_name, e.last_name, e.salary, d.department_name
FROM hr.employees e
JOIN hr.employees m ON e.manager_id = m.employee_id
JOIN hr.departments d ON e.department_id = d.department_id
WHERE e.salary > m.salary;

---

**H6.** Departments + employee count + count of employees with commission.

SELECT d.department_id, d.department_name,
       COUNT(e.employee_id) AS emp_count,
       COUNT(e.commission_pct) AS commissioned_count
FROM hr.departments d
LEFT JOIN hr.employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;

---

**H7.** Employees sharing the same manager as employee 104.

SELECT employee_id, first_name, last_name, manager_id
FROM hr.employees
WHERE manager_id = (SELECT manager_id FROM hr.employees WHERE employee_id = 104)
  AND employee_id <> 104;
  
---

**H8.** Employee + department + manager, all optional.

SELECT e.first_name, e.last_name, d.department_name,
       m.first_name AS mgr_first_name, m.last_name AS mgr_last_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id
LEFT JOIN hr.employees m ON e.manager_id = m.employee_id;

---

**H9.** Departments whose manager_id doesn't correspond to a valid employee.

SELECT d.department_id, d.department_name
FROM hr.departments d
LEFT JOIN hr.employees mgr ON d.manager_id = mgr.employee_id
WHERE mgr.employee_id IS NULL;

---

**H10.** Employee + department_name + manager's last_name, all optional.

SELECT e.employee_id, e.first_name, e.last_name,
       d.department_name, m.last_name AS mgr_last_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id
LEFT JOIN hr.employees m ON e.manager_id = m.employee_id;

---

**H11.** Employees earning more than their manager (repeat of H5 pattern).

SELECT e.first_name, e.last_name, e.salary
FROM hr.employees e
JOIN hr.employees m ON e.manager_id = m.employee_id
WHERE e.salary > m.salary;

---

**H12.** Departments + total salary, including 0-employee departments.

SELECT d.department_id, d.department_name, NVL(SUM(e.salary), 0) AS total_salary
FROM hr.departments d
LEFT JOIN hr.employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;

---

**H13.** Employee + department_name + department headcount (window function).

SELECT e.employee_id, e.first_name, d.department_name,
       COUNT(*) OVER (PARTITION BY e.department_id) AS dept_count
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id;

---

**H14.** Managers + how many people they manage.

SELECT m.employee_id, m.first_name, m.last_name, c.cnt AS team_size
FROM hr.employees m
JOIN (
    SELECT manager_id, COUNT(*) AS cnt
    FROM hr.employees
    GROUP BY manager_id
) c ON m.employee_id = c.manager_id;

---

**H15.** Employee + department_name + manager name, all optional.

SELECT e.first_name, e.last_name, d.department_name,
       m.first_name AS mgr_first_name, m.last_name AS mgr_last_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id
LEFT JOIN hr.employees m ON e.manager_id = m.employee_id;

---

**H16.** Departments with at least one employee earning > 10000.

SELECT DISTINCT d.department_name
FROM hr.departments d
JOIN hr.employees e ON d.department_id = e.department_id
WHERE e.salary > 10000;

---

**H17.** Employee + department_name + manager first_name, with default text.

SELECT e.employee_id, e.first_name, e.last_name, d.department_name,
       COALESCE(m.first_name, 'No Manager') AS mgr_first_name
FROM hr.employees e
LEFT JOIN hr.departments d ON e.department_id = d.department_id
LEFT JOIN hr.employees m ON e.manager_id = m.employee_id;

---

**H18.** All employees + all departments (FULL OUTER JOIN) with a source label.

SELECT
    e.employee_id, e.first_name,
    d.department_id, d.department_name,
    CASE
        WHEN e.employee_id IS NOT NULL AND d.department_id IS NOT NULL THEN 'Matched'
        WHEN e.employee_id IS NOT NULL THEN 'Emp Only'
        ELSE 'Dept Only'
    END AS row_source
FROM hr.employees e
FULL OUTER JOIN hr.departments d ON e.department_id = d.department_id;

---

**H19.** Highest-paid employee per department.

SELECT d.department_name, top_emp.first_name, top_emp.last_name, top_emp.salary
FROM hr.departments d
JOIN (
    SELECT employee_id, department_id, first_name, last_name, salary,
           ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
    FROM hr.employees
) top_emp ON d.department_id = top_emp.department_id
WHERE top_emp.rn = 1;

---

**H20.** Employees hired before their manager.

SELECT e.first_name, e.last_name, d.department_name
FROM hr.employees e
JOIN hr.employees m ON e.manager_id = m.employee_id
JOIN hr.departments d ON e.department_id = d.department_id
WHERE e.hire_date < m.hire_date;
