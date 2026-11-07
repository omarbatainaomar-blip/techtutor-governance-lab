<!-- topics: databases -->
# SQL Worked Examples With Real Results

## The practice database
All examples in this note use one small university database with three tables. The students table has student_id (primary key), name, city and birth_year. The courses table has course_id (primary key), title, credits and dept. The enrollments table links them: it has student_id, course_id and grade, with the pair (student_id, course_id) as a composite primary key, because a student can take a course only once. This is the standard many-to-many pattern: students and courses are linked through the junction table enrollments.
```sql
CREATE TABLE students(student_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT, birth_year INTEGER);
CREATE TABLE courses(course_id INTEGER PRIMARY KEY, title TEXT NOT NULL, credits INTEGER, dept TEXT);
CREATE TABLE enrollments(
  student_id INTEGER REFERENCES students(student_id),
  course_id INTEGER REFERENCES courses(course_id),
  grade INTEGER,
  PRIMARY KEY(student_id, course_id));
```
The data: six students (Lina, Omar, Sara, Yazan, Huda, Khaled), five courses (101 Intro to Python, 102 Databases, 103 Computer Networks, 201 Statistics, 202 Linear Algebra) and twelve enrollment rows. Khaled has no enrollments at all, which is useful for demonstrating LEFT JOIN. The results shown below were produced by actually running the queries in SQLite 3.45.

## Filtering and sorting
To list the students from Amman in alphabetical order:
```sql
SELECT name, city FROM students WHERE city = 'Amman' ORDER BY name;
```
Result: Khaled, Lina, Sara. WHERE filters individual rows before anything is grouped. ORDER BY sorts the final result, ascending by default and descending with DESC. LIKE matches patterns: WHERE name LIKE 'S%' finds names that start with S (percent means any number of characters, underscore means exactly one character), and it returns Sara.

## Joining three tables
Question: which students scored 90 or more in a CS course, and in which course? The information is spread over three tables, so we join them along the foreign keys.
```sql
SELECT s.name, c.title, e.grade
FROM enrollments e
JOIN students s ON s.student_id = e.student_id
JOIN courses c ON c.course_id = e.course_id
WHERE c.dept = 'CS' AND e.grade >= 90
ORDER BY e.grade DESC;
```
Result: Sara in Intro to Python with 95, Lina in Intro to Python with 92, Sara in Databases with 91. Reading a join: start from the table that holds the facts you want to count or list (enrollments), then attach the descriptive tables (students, courses) using the key columns. Short aliases such as s, c and e make long queries readable. Forgetting the ON condition produces a cross join, where every row is paired with every row, and the result explodes in size. This is the most common join mistake.

## LEFT JOIN and finding missing relationships
An INNER JOIN drops students who have no enrollments. A LEFT JOIN keeps every row from the left table and fills the right-side columns with NULL when nothing matches. This gives a classic pattern: to find students who have not enrolled in anything, LEFT JOIN and then keep only the rows where the right side is NULL.
```sql
SELECT s.name
FROM students s
LEFT JOIN enrollments e ON e.student_id = s.student_id
WHERE e.student_id IS NULL;
```
Result: Khaled. Note the use of IS NULL and not = NULL, because comparing anything to NULL with an equals sign never gives true. The same question can be written with NOT EXISTS, which many people find clearer, and the performance is usually similar on modern databases.

## Aggregation: GROUP BY, HAVING and counting correctly
Aggregate functions (COUNT, SUM, AVG, MIN, MAX) collapse many rows into one value per group. For each student, the number of courses and the average grade:
```sql
SELECT s.name, COUNT(e.course_id) AS n_courses, ROUND(AVG(e.grade), 1) AS avg_grade
FROM students s
LEFT JOIN enrollments e USING(student_id)
GROUP BY s.student_id
ORDER BY avg_grade DESC;
```
Result: Sara 4 courses with 89.8, Lina 3 with 85.0, Huda 1 with 77.0, Omar 2 with 74.0, Yazan 2 with 64.0, Khaled 0 with NULL. Two details matter. First, COUNT(e.course_id) counts only non-NULL values, so Khaled gets 0, while COUNT(*) would wrongly give 1 for him because the LEFT JOIN produced one row. Second, AVG over no rows is NULL, not 0. Where NULL values appear in a descending sort differs between databases: SQLite treats NULL as the smallest value so it appears last in DESC order, while PostgreSQL puts NULLs first in DESC order unless you write NULLS LAST.
HAVING filters groups after aggregation, while WHERE filters rows before it. Courses with at least three enrollments:
```sql
SELECT c.title, COUNT(*) AS n
FROM enrollments e JOIN courses c USING(course_id)
GROUP BY c.course_id
HAVING COUNT(*) >= 3
ORDER BY n DESC;
```
Result: Computer Networks 3, Databases 3, Intro to Python 3. You cannot put COUNT(*) >= 3 in WHERE, because the count does not exist yet at that stage.
Overall statistics: SELECT AVG(grade), COUNT(*), COUNT(DISTINCT student_id) FROM enrollments returns an average of about 80.58, 12 rows and 5 distinct students. COUNT(DISTINCT column) counts unique values.

## Subqueries and EXISTS
A subquery is a query inside another query. To find students who have any grade below 60:
```sql
SELECT name FROM students
WHERE student_id IN (SELECT student_id FROM enrollments WHERE grade < 60);
```
Result: Yazan. To find students enrolled in course 101, EXISTS checks whether at least one matching row is present:
```sql
SELECT name FROM students s
WHERE EXISTS (SELECT 1 FROM enrollments e WHERE e.student_id = s.student_id AND e.course_id = 101);
```
Result: Lina, Omar, Sara. This is a correlated subquery, because the inner query refers to the outer row s. Be careful with NOT IN: if the subquery returns even one NULL, NOT IN returns no rows at all, which surprises many people. NOT EXISTS does not have this problem, so prefer it.

## Common table expressions (WITH)
A CTE gives a name to an intermediate result and makes long queries readable, like defining a variable. Students whose average grade is above the overall average of all grades:
```sql
WITH avg_by_student AS (
  SELECT student_id, AVG(grade) AS avg_grade FROM enrollments GROUP BY student_id)
SELECT s.name, ROUND(a.avg_grade, 1)
FROM avg_by_student a JOIN students s USING(student_id)
WHERE a.avg_grade > (SELECT AVG(grade) FROM enrollments)
ORDER BY 2 DESC;
```
Result: Sara 89.8 and Lina 85.0, because the overall average is about 80.58. Build the CTE first, test it alone, then use it.

## Window functions
Window functions compute a value across a set of related rows without collapsing them, which GROUP BY cannot do. RANK() OVER (PARTITION BY ... ORDER BY ...) ranks rows inside each partition. Ranking students inside each course:
```sql
SELECT c.title, s.name, e.grade,
       RANK() OVER (PARTITION BY c.course_id ORDER BY e.grade DESC) AS rnk
FROM enrollments e
JOIN students s USING(student_id)
JOIN courses c USING(course_id)
WHERE c.course_id IN (101, 103)
ORDER BY c.title, rnk;
```
Result: in Computer Networks, Sara 89 is rank 1, Omar 81 is rank 2, Huda 77 is rank 3. In Intro to Python, Sara 95 is rank 1, Lina 92 is rank 2, Omar 67 is rank 3. Related functions: ROW_NUMBER gives unique numbers even for ties, RANK leaves gaps after ties, DENSE_RANK does not leave gaps, LAG and LEAD read the previous or next row, and SUM(...) OVER (ORDER BY ...) gives running totals. Window functions need SQLite 3.25 or newer, and they are standard in PostgreSQL and MySQL 8.

## CASE expressions
CASE adds if-else logic inside a query. Converting numeric grades to letters for the Databases course:
```sql
SELECT name, grade,
  CASE WHEN grade >= 90 THEN 'A' WHEN grade >= 80 THEN 'B' WHEN grade >= 70 THEN 'C' ELSE 'F' END AS letter
FROM enrollments JOIN students USING(student_id)
WHERE course_id = 102 ORDER BY grade DESC;
```
Result: Sara 91 is A, Lina 88 is B, Yazan 58 is F. The conditions are checked from top to bottom and the first true one wins, so the order matters.

## Counting per group with ordering
Students per city: SELECT city, COUNT(*) FROM students GROUP BY city ORDER BY 2 DESC, city. Result: Amman 3, Irbid 2, Zarqa 1. ORDER BY 2 means sort by the second selected column. Total credits per department for one student, for example Sara (id 3), uses GROUP BY on c.dept with SUM(c.credits) and gives CS 9 and MATH 3.

## Changing data safely
INSERT adds rows, UPDATE changes rows and DELETE removes rows. Always test the WHERE clause with a SELECT first.
```sql
INSERT INTO students(student_id, name, city, birth_year) VALUES (7, 'Rama', 'Aqaba', 2004);
UPDATE students SET city = 'Amman' WHERE student_id = 7;
DELETE FROM students WHERE student_id = 7;
```
An UPDATE or DELETE without WHERE changes every row in the table. Use a transaction when several statements must succeed together:
```sql
BEGIN;
UPDATE enrollments SET grade = grade + 5 WHERE course_id = 101 AND grade < 70;
COMMIT;
```
If something looks wrong before COMMIT, run ROLLBACK to undo everything since BEGIN. Foreign keys are not enforced in SQLite unless you run PRAGMA foreign_keys = ON for each connection, which is an easy thing to forget.

## Indexes and reading the query plan
EXPLAIN QUERY PLAN shows how SQLite will run a query. Before creating an index, the query SELECT * FROM enrollments WHERE grade > 90 shows SCAN enrollments, which means a full table scan that reads every row. After CREATE INDEX idx_enr_grade ON enrollments(grade), the plan becomes SEARCH enrollments USING INDEX idx_enr_grade (grade>?), which uses the index. On 12 rows the difference does not matter, but on millions of rows it is the difference between milliseconds and seconds. Primary keys are indexed automatically. Other databases use EXPLAIN or EXPLAIN ANALYZE with different output formats, but the idea is identical: look for sequential or full scans on big tables.

## Using SQL safely from Python
Never build SQL by joining strings with user input. Use placeholders so the driver sends the values separately from the command, which prevents SQL injection.
```python
import sqlite3
con = sqlite3.connect("university.db")
name = input("Student name: ")
rows = con.execute("SELECT * FROM students WHERE name = ?", (name,)).fetchall()
```
With name equal to Lina this returns the row (1, 'Lina', 'Amman', 2003). With the unsafe version, f"SELECT * FROM students WHERE name = '{name}'", an input such as ' OR '1'='1 would return every row. Placeholders differ by driver: sqlite3 uses a question mark, psycopg for PostgreSQL uses %s, and some libraries use named parameters like :name. Also remember that placeholders can only replace values, not table or column names.

## Practice questions
Try these on the practice database and compare with the patterns above. List the courses that nobody takes (LEFT JOIN from courses and keep rows where the enrollment side is NULL). In this data every course has at least one student, so the result is empty until you insert a new course, which is a good way to see the pattern work. Find the highest grade in each course (GROUP BY with MAX). Find students who took both course 101 and course 102 (self-join, or GROUP BY with HAVING COUNT(DISTINCT course_id) = 2 on a filtered set). Find the second highest grade in the whole table (ORDER BY with LIMIT and OFFSET, or DENSE_RANK). Writing the query yourself and checking the result is how SQL is learned.
