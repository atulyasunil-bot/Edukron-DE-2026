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

### Part 3: 20 Medium + 20 Hard Questions (Complete Solutions)

All queries use **hr.employees** and **hr.departments** only.

---

## 20 Medium Questions — Answers

**M1.** Total salary for the whole company.

SELECT SUM(salary) AS total_salary
FROM hr.employees;

---

**M2.** Count employees per job_id.

SELECT job_id, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY job_id;

---

**M3.** Average salary per department_id.

SELECT department_id, AVG(salary) AS avg_salary
FROM hr.employees
GROUP BY department_id;

---

**M4.** Min and max salary per department.

SELECT department_id, MIN(salary) AS min_salary, MAX(salary) AS max_salary
FROM hr.employees
GROUP BY department_id;

---

**M5.** Count employees per department_id.

SELECT department_id, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY department_id;

---

**M6.** Total salary per job_id.

SELECT job_id, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY job_id;

---

**M7.** Employees with non-null commission_pct, per department.

SELECT department_id, COUNT(commission_pct) AS commissioned_count
FROM hr.employees
GROUP BY department_id;

---

**M8.** Min and max hire_date per job_id.

SELECT job_id, MIN(hire_date) AS earliest_hire, MAX(hire_date) AS latest_hire
FROM hr.employees
GROUP BY job_id;

---

**M9.** Total employee count.

SELECT COUNT(*) AS total_employees
FROM hr.employees;

---

**M10.** Department_id, avg salary, and count — all three together.

SELECT department_id, AVG(salary) AS avg_salary, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY department_id;

---

**M11.** Job_id and avg salary, ordered descending.

SELECT job_id, AVG(salary) AS avg_salary
FROM hr.employees
GROUP BY job_id
ORDER BY AVG(salary) DESC;

---

**M12.** Total salary for departments 50, 60, 80.

SELECT department_id, SUM(salary) AS total_salary
FROM hr.employees
WHERE department_id IN (50, 60, 80)
GROUP BY department_id;

---

**M13.** Count of direct reports per manager (excluding null manager_id).

SELECT manager_id, COUNT(*) AS report_count
FROM hr.employees
WHERE manager_id IS NOT NULL
GROUP BY manager_id;

---

**M14.** Min salary per job.

SELECT job_id, MIN(salary) AS min_salary
FROM hr.employees
GROUP BY job_id;

---

**M15.** Max hire_date per department.

SELECT department_id, MAX(hire_date) AS latest_hire
FROM hr.employees
GROUP BY department_id;

---

**M16.** Total salary for department 90 only.
```sql
SELECT SUM(salary) AS total_salary
FROM hr.employees
WHERE department_id = 90;
```

---

**M17.** Count of distinct job_id values.

SELECT COUNT(DISTINCT job_id) AS distinct_jobs
FROM hr.employees;

---

**M18.** Count per (department_id, job_id) combination.

SELECT department_id, job_id, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY department_id, job_id;

---

**M19.** Avg salary per department, rounded.

SELECT department_id, ROUND(AVG(salary), 2) AS avg_salary
FROM hr.employees
GROUP BY department_id;

---

**M20.** Job_id + count, only where count >= 2.

SELECT job_id, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY job_id
HAVING COUNT(*) >= 2;

---

## 20 Hard Questions — Answers

**H1.** Department name + total salary (joined).

SELECT d.department_id, d.department_name, SUM(e.salary) AS total_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name;

---

**H2.** Job_id + avg salary, only jobs with more than 3 employees.

SELECT job_id, AVG(salary) AS avg_salary
FROM hr.employees
GROUP BY job_id
HAVING COUNT(*) > 3;

---

**H3.** Employee count + count hired after 2000, per department.

SELECT department_id,
       COUNT(*) AS total_employees,
       SUM(CASE WHEN EXTRACT(YEAR FROM hire_date) > 2000 THEN 1 ELSE 0 END) AS hired_after_2000
FROM hr.employees
GROUP BY department_id;

---

**H4.** Departments with total salary > 100000.

SELECT department_id, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY department_id
HAVING SUM(salary) > 100000;

---

**H5.** Jobs where max−min salary spread exceeds 5000.

SELECT job_id, MAX(salary) AS max_salary, MIN(salary) AS min_salary
FROM hr.employees
GROUP BY job_id
HAVING MAX(salary) - MIN(salary) > 5000;

---

**H6.** Department name + count, ordered by count descending (joined).

SELECT d.department_id, d.department_name, COUNT(*) AS emp_count
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
ORDER BY COUNT(*) DESC;

---

**H7.** Average tenure (in years) per department.

SELECT department_id,
       AVG(MONTHS_BETWEEN(SYSDATE, hire_date) / 12) AS avg_tenure_years
FROM hr.employees
GROUP BY department_id;

---

**H8.** Total salary for jobs containing 'MAN'.
```sql
SELECT job_id, SUM(salary) AS total_salary
FROM hr.employees
WHERE job_id LIKE '%MAN%'
GROUP BY job_id;
```

---

**H9.** Department stats, only where avg salary > 7000.

SELECT department_id, COUNT(*) AS emp_count, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY department_id
HAVING AVG(salary) > 7000;

---

**H10.** Department name + min/max salary (joined).

SELECT d.department_id, d.department_name,
       MIN(e.salary) AS min_salary, MAX(e.salary) AS max_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name;

---

**H11.** Managers with more than 2 direct reports.

SELECT manager_id, COUNT(*) AS report_count
FROM hr.employees
WHERE manager_id IS NOT NULL
GROUP BY manager_id
HAVING COUNT(*) > 2;

---

**H12.** Count of distinct jobs per department.

SELECT department_id, COUNT(DISTINCT job_id) AS distinct_jobs
FROM hr.employees
GROUP BY department_id;

---

**H13.** Avg salary per job, restricted to departments 50/80/90.

SELECT job_id, AVG(salary) AS avg_salary
FROM hr.employees
WHERE department_id IN (50, 80, 90)
GROUP BY job_id;

---

**H14.** Departments with > 5 employees AND total salary > 200000.

SELECT department_id, COUNT(*) AS emp_count, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY department_id
HAVING COUNT(*) > 5 AND SUM(salary) > 200000;

---

**H15.** Department name + total salary, only where at least one employee has commission.
`
SELECT d.department_id, d.department_name, SUM(e.salary) AS total_salary
FROM hr.employees e
JOIN hr.departments d ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(e.commission_pct) > 0;

---

**H16.** Job_id + count, ordered by count desc then job_id.

SELECT job_id, COUNT(*) AS emp_count
FROM hr.employees
GROUP BY job_id
ORDER BY COUNT(*) DESC, job_id;

---

**H17.** Sum and rounded avg salary per department.

SELECT department_id, SUM(salary) AS total_salary, ROUND(AVG(salary), 2) AS avg_salary
FROM hr.employees
GROUP BY department_id;

---

**H18.** Department(s) with the single highest total salary.

SELECT department_id, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY department_id
HAVING SUM(salary) = (
    SELECT MAX(dept_total)
    FROM (
        SELECT SUM(salary) AS dept_total
        FROM hr.employees
        GROUP BY department_id
    )
);

---

**H19.** Department/job breakdown with subtotals — ROLLUP.

SELECT department_id, job_id, COUNT(*) AS emp_count, SUM(salary) AS total_salary
FROM hr.employees
GROUP BY ROLLUP(department_id, job_id);

ROLLUP produces the normal (department_id, job_id) detail rows, **plus** a subtotal row per department_id (with job_id = NULL), **plus** one grand-total row (both columns NULL) at the very end. This is the key thing to point out to students — the NULLs in the output aren't missing data, they're rollup markers. You can distinguish them from genuine NULL job_ids using `GROUPING(job_id)` if needed:

SELECT department_id, job_id, COUNT(*) AS emp_count, SUM(salary) AS total_salary,
       GROUPING(department_id) AS is_dept_total,
       GROUPING(job_id) AS is_job_total
FROM hr.employees
GROUP BY ROLLUP(department_id, job_id);
---

**H20.** Department name + employee count, including 0-employee departments.

SELECT d.department_id, d.department_name, COUNT(e.employee_id) AS emp_count
FROM hr.departments d
LEFT JOIN hr.employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;

---

