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

# Day 10 Assignment — Full Answer Key
### Part 3: 20 Medium + 20 Hard Questions (Complete Solutions)

All queries use **hr.employees** and **hr.departments** only.

---

## 20 Medium Questions — Answers

**M1.** Departments with average salary > 8000.

SELECT department_id, AVG(salary) AS avg_salary
FROM hr.employees
GROUP BY department_id
HAVING AVG(salary) > 8000;

---

**M2.** Job_ids with more than 3 employees.

SELECT job_id, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY job_id
HAVING COUNT(*) > 3;

---

**M3.** Department name + total salary (joined).

SELECT d.department_id, d.department_name, SUM(e.salary) AS total_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name;

---

**M4.** Departments with total salary > 150000.

SELECT department_id, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY department_id
HAVING SUM(salary) > 150000;

---

**M5.** Job_ids where min salary < 4000.

SELECT job_id, MIN(salary) AS min_salary
FROM hr.employees
GROUP BY job_id
HAVING MIN(salary) < 4000;

---

**M6.** Departments with more than 5 employees.

SELECT department_id, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY department_id
HAVING COUNT(*) > 5;

---

**M7.** Department name + avg salary (joined).

SELECT d.department_id, d.department_name, AVG(e.salary) AS avg_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name;


---

**M8.** Job_ids with more than 2 employees + total salary.

SELECT job_id, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY job_id
HAVING COUNT(*) > 2;

---

**M9.** Departments where max salary > 12000.

SELECT department_id, MAX(salary) AS max_salary
FROM hr.employees
GROUP BY department_id
HAVING MAX(salary) > 12000;

---

**M10.** Department name + count, only departments with >= 3 employees (joined).

SELECT d.department_id, d.department_name, COUNT(e.employee_id) AS emp_count
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(e.employee_id) >= 3;

---

**M11.** Job_id + avg salary, only jobs with total salary > 50000.

SELECT job_id, AVG(salary) AS avg_salary
FROM hr.employees
GROUP BY job_id
HAVING SUM(salary) > 50000;

---

**M12.** Departments with average salary between 6000 and 10000.

SELECT department_id, AVG(salary) AS avg_salary
FROM hr.employees
GROUP BY department_id
HAVING AVG(salary) BETWEEN 6000 AND 10000;

---

**M13.** Department name + min/max salary (joined).

SELECT d.department_id, d.department_name,
       MIN(e.salary) AS min_salary, MAX(e.salary) AS max_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name;

---

**M14.** Job_ids with exactly 2 employees.

SELECT job_id, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY job_id
HAVING COUNT(*) = 2;

---

**M15.** Departments with avg salary < 7000 + total salary.

SELECT department_id, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY department_id
HAVING AVG(salary) < 7000;

---

**M16.** Department name + total salary, only departments with more than 10 employees (joined).

SELECT d.department_id, d.department_name, SUM(e.salary) AS total_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(*) > 10;

---

**M17.** Job_id + count, for job_ids starting with 'SA'.

SELECT job_id, COUNT(*) AS emp_count
FROM hr.employees
WHERE job_id LIKE 'SA%'
GROUP BY job_id;

---

**M18.** Departments where min hire_date is after 2005-01-01.

SELECT department_id, MIN(hire_date) AS earliest_hire
FROM hr.employees
GROUP BY department_id
HAVING MIN(hire_date) > DATE '2005-01-01';

---

**M19.** Department name + count, only departments with total salary > 200000 (joined).

SELECT d.department_id, d.department_name, COUNT(e.employee_id) AS emp_count
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING SUM(e.salary) > 200000;

---

**M20.** Job_id + avg salary, ordered descending.

SELECT job_id, AVG(salary) AS avg_salary
FROM hr.employees
GROUP BY job_id
HAVING COUNT(*) >= 1
ORDER BY AVG(salary) DESC;

---

## 20 Hard Questions — Answers

**H1.** Department/job breakdown with ROLLUP.
```sql
SELECT department_id, job_id, COUNT(*) AS emp_count, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY ROLLUP(department_id, job_id);
```
Produces detail rows per (department_id, job_id), a subtotal row per department_id (job_id = NULL), and one grand-total row (both NULL).

---

**H2.** Department name + total salary, only where avg > 8000 AND count > 3.

SELECT d.department_id, d.department_name, SUM(e.salary) AS total_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING AVG(e.salary) > 8000 AND COUNT(*) > 3;

---

**H3.** Job_id + count, restricted to departments 50, 60, 80.

SELECT job_id, COUNT(*) AS emp_count
FROM hr.employees
WHERE department_id IN (50, 60, 80)
GROUP BY job_id;

---

**H4.** Departments with top-3 total salary.

SELECT department_id, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY department_id
HAVING SUM(salary) IN (
    SELECT total
    FROM (
        SELECT SUM(salary) AS total
        FROM hr.employees
        GROUP BY department_id
        ORDER BY total DESC
        FETCH FIRST 3 ROWS ONLY
    )
);

---

**H5.** Department name + stats, only departments with at least one commissioned employee.

SELECT d.department_id, d.department_name, COUNT(*) AS emp_count, SUM(e.salary) AS total_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(e.commission_pct) > 0;

---

**H6.** Job_id + avg salary, only where salary spread > 5000.

SELECT job_id, AVG(salary) AS avg_salary
FROM hr.employees
GROUP BY job_id
HAVING MAX(salary) - MIN(salary) > 5000;

---

**H7.** Full department stats, only count > 2 AND avg > 6000.

SELECT d.department_id, d.department_name,
       COUNT(*) AS emp_count, SUM(e.salary) AS total_salary, AVG(e.salary) AS avg_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(*) > 2 AND AVG(e.salary) > 6000;

---

**H8.** Department name + count of employees earning > 5000.

SELECT d.department_id, d.department_name,
       SUM(CASE WHEN e.salary > 5000 THEN 1 ELSE 0 END) AS high_earners
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name;

---

**H9.** Job_id + total salary, jobs with >= 2 employees AND total > 20000.

SELECT job_id, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY job_id
HAVING COUNT(*) >= 2 AND SUM(salary) > 20000;

---

**H10.** Departments with >= 3 employees AND avg salary < 9000.

SELECT department_id
FROM hr.employees
GROUP BY department_id
HAVING COUNT(*) >= 3 AND AVG(salary) < 9000;

---

**H11.** Department name + rounded avg salary, only where total > 100000.

SELECT d.department_id, d.department_name, ROUND(AVG(e.salary), 2) AS avg_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING SUM(e.salary) > 100000;

---

**H12.** Job_id + count + total salary, count > 1 AND sum > 30000.

SELECT job_id, COUNT(*) AS emp_count, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY job_id
HAVING COUNT(*) > 1 AND SUM(salary) > 30000;

---

**H13.** GROUPING SETS for two independent grouping levels.

SELECT department_id, job_id, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY GROUPING SETS ((department_id), (job_id));

---

**H14.** Department name + total salary, excluding single-employee departments.

SELECT d.department_id, d.department_name, SUM(e.salary) AS total_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(*) > 1;

---

**H15.** Departments where min salary > 3000 AND max salary < 15000.

SELECT department_id
FROM hr.employees
GROUP BY department_id
HAVING MIN(salary) > 3000 AND MAX(salary) < 15000;

---

**H16.** Job_id + avg salary, employees hired after 2000.
```sql
SELECT job_id, AVG(salary) AS avg_salary
FROM hr.employees
WHERE hire_date > DATE '2000-12-31'
GROUP BY job_id;
```

---

**H17.** Full department stats, count between 2 and 10.

SELECT d.department_id, d.department_name,
       COUNT(*) AS emp_count, SUM(e.salary) AS total_salary, AVG(e.salary) AS avg_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(*) BETWEEN 2 AND 10;

---

**H18.** Department with the single highest average salary.

SELECT department_id, AVG(salary) AS avg_salary
FROM hr.employees
GROUP BY department_id
HAVING AVG(salary) = (
    SELECT MAX(av)
    FROM (
        SELECT AVG(salary) AS av
        FROM hr.employees
        GROUP BY department_id
    )
);

---

**H19.** CUBE for all combinations of subtotals.

SELECT department_id, job_id, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY CUBE(department_id, job_id);

---

**H20.** Department name + total salary, only departments with at least one 'SA_REP'.

SELECT d.department_id, d.department_name, SUM(e.salary) AS total_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING MAX(CASE WHEN e.job_id = 'SA_REP' THEN 1 ELSE 0 END) = 1;

---
