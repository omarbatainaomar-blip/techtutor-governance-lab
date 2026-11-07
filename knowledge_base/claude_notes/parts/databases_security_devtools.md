<!-- topics: databases,web_security,dev_tools -->
# Databases, Security and Developer Tools: Practical Notes

## SQL essentials and common mistakes
SELECT chooses columns, FROM names the table, WHERE filters rows before grouping, GROUP BY groups rows, HAVING filters groups after aggregation, ORDER BY sorts, LIMIT restricts the number of rows. The logical order of evaluation is FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT, which explains why you cannot use a SELECT alias inside WHERE.
Joins: INNER JOIN keeps only rows that match in both tables. LEFT JOIN keeps all rows of the left table and fills missing right-side columns with NULL. RIGHT JOIN is the mirror image. FULL OUTER JOIN keeps all rows of both. CROSS JOIN produces every combination.
NULL means unknown. NULL = NULL is not true, so use IS NULL and IS NOT NULL. Aggregates such as SUM and AVG ignore NULL values, while COUNT(*) counts rows and COUNT(column) counts non-NULL values.
Avoid SELECT * in application code. Always use a WHERE clause in UPDATE and DELETE statements, and run a SELECT with the same WHERE first to check which rows will change.

## Keys, relationships and normalisation
A primary key uniquely identifies each row and cannot be NULL. A foreign key is a column that refers to the primary key of another table and enforces referential integrity. One-to-many is modelled with a foreign key on the "many" side. Many-to-many needs a junction table that holds two foreign keys, for example enrollments linking students and courses.
Normalisation reduces redundancy. First normal form: each column holds one atomic value and there are no repeating groups. Second normal form: no column depends on only part of a composite key. Third normal form: no non-key column depends on another non-key column. A simple memory phrase says every non-key attribute depends on the key, the whole key and nothing but the key. Denormalisation on purpose is sometimes used for read speed in reporting systems.

## Indexes and query performance
An index is a separate structure, usually a B-tree, that lets the database find rows without scanning the entire table. It speeds up reads that filter, join or sort on the indexed columns, and slows down writes a little and uses disk space. Index columns used often in WHERE and JOIN conditions, but not every column. A function applied to a column in WHERE, such as WHERE LOWER(name) = 'x', can stop a plain index from being used.
Use EXPLAIN (or EXPLAIN ANALYZE) to see the query plan and spot full table scans. The N+1 query problem happens when code runs one query for a list and then one more query per item, and the fix is a join or a batched query.

## Transactions and ACID
A transaction groups statements so they succeed or fail together. ACID: Atomicity (all or nothing), Consistency (rules and constraints stay valid), Isolation (concurrent transactions do not see each other's half-done work), Durability (committed data survives a crash). The classic example is a bank transfer: subtract from one account and add to another inside one transaction. Use COMMIT to save and ROLLBACK to undo.
Isolation levels trade safety for speed: read committed, repeatable read and serializable are common. Lower levels allow anomalies such as dirty reads, non-repeatable reads and phantom reads.

## SQL versus NoSQL
Relational databases (PostgreSQL, MySQL, SQLite) store tables with a fixed schema and support joins and transactions. NoSQL is a family: document stores (MongoDB) keep JSON-like documents, key-value stores (Redis) give very fast lookups, column-family stores (Cassandra) scale writes across many machines, graph databases (Neo4j) model relationships. For most beginner and medium projects a relational database is the right default. SQLite is a file-based database that needs no server, which makes it excellent for learning and small apps, and it is what this project uses for its knowledge base.
The CAP theorem says that during a network partition a distributed system must choose between consistency and availability.

## Web security: the core ideas
Authentication proves who you are. Authorisation decides what you may do. Encryption hides data and can be reversed with a key. Hashing is one-way and cannot be reversed. Never store passwords in plain text or with a fast hash such as plain SHA-256 or MD5. Use a slow password hashing algorithm built for the job: Argon2, bcrypt or scrypt, which add a unique random salt for each password.
Principle of least privilege: give each user, program and database account only the access it needs. Defence in depth: use several layers so one failure does not break everything. Never trust input from the client, validate on the server. Keep dependencies updated, because many breaches use known vulnerabilities in old libraries. Do not commit secrets such as API keys to Git. Keep them in environment variables or a secrets manager, and rotate any key that has leaked.
Turn on multi-factor authentication for important accounts.

## Common web vulnerabilities and fixes
SQL injection: user input is concatenated into a SQL string, so an attacker can change the query. Fix: parameterised queries (placeholders) or an ORM, never string formatting. In Python with sqlite3 use cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).
Cross-site scripting (XSS): attacker-controlled script runs in another user's browser. Types are stored, reflected and DOM-based. Fix: escape output for the context where it is shown, use a Content-Security-Policy, and avoid innerHTML with untrusted data.
Cross-site request forgery (CSRF): a malicious site makes the victim's browser send an authenticated request. Fix: anti-CSRF tokens and SameSite cookies.
Broken access control: a user changes an ID in a URL and sees someone else's data (insecure direct object reference). Fix: check on the server that the logged-in user owns the resource. This category is at the top of the OWASP Top 10 list in recent versions.
Security misconfiguration: default passwords, debug mode in production, open cloud storage. Sensitive data exposure: no HTTPS, secrets in logs. Vulnerable and outdated components: unpatched libraries.
CORS is a browser rule that restricts which web pages may read responses from your API. It does not protect your server from other kinds of clients, so it is not an authentication mechanism.

## Cookies, sessions and tokens
A session stores the login state on the server and gives the browser an identifier in a cookie. Mark session cookies HttpOnly (not readable by JavaScript), Secure (sent only over HTTPS) and SameSite. A JSON Web Token (JWT) is a signed token that carries claims such as the user id. The server must always verify the signature and expiry. JWT contents are encoded, not encrypted, so never put secrets in them. Short-lived access tokens plus refresh tokens are a common design.

## HTTPS and certificates
HTTPS protects against eavesdropping and tampering. A certificate links a domain name to a public key and is signed by a certificate authority. Free certificates are available from Let's Encrypt. A padlock in the browser means the connection is encrypted and the certificate matches the domain, it does not prove that the site is trustworthy.

## Git recipes that people search for
Undo changes in a file that are not committed: git restore file (older versions of Git use git checkout -- file). Unstage a file: git restore --staged file. Fix the last commit message or add a forgotten file: git commit --amend, but only before pushing.
Undo a commit that is already shared: git revert <commit>, which creates a new commit that reverses the old one and keeps history safe. Move the branch back and discard later commits locally: git reset --hard <commit>, which is destructive for uncommitted work. git reset --soft keeps the changes staged and git reset --mixed (the default) keeps them unstaged.
If you think you lost commits, git reflog lists where HEAD has been, and you can usually recover by checking out or resetting to an older entry.
Save unfinished work temporarily: git stash, then git stash pop to bring it back.
Merge versus rebase: merge joins two histories with a merge commit and preserves the real history. Rebase replays your commits on top of another branch for a linear history but rewrites commits, so never rebase commits that others already have. When a merge conflict appears, open the files, find the markers <<<<<<<, ======= and >>>>>>>, choose the correct final content, remove the markers, git add the file, then continue with git commit (or git rebase --continue).
A .gitignore file lists files Git should not track, such as .venv, node_modules and .env. Adding a file to .gitignore does not remove it if it was already committed, use git rm --cached file for that.
Good commit messages have a short summary line in the imperative mood, such as "Fix login redirect", followed by a blank line and a description of why when needed.

## Branching and collaboration
A simple workflow: keep main always working, create a branch for each feature or fix, open a pull request, get a review, run automated tests, then merge. Small, frequent pull requests are easier to review. Protect the main branch so that nobody pushes broken code directly. A good README states what the project does, how to install and run it, and how to contribute. Choose an open-source licence deliberately, because code without a licence is not free to reuse by default.

## CI/CD in brief
Continuous integration runs tests and checks automatically on every push or pull request, for example with GitHub Actions. Continuous delivery keeps the code always ready to release, and continuous deployment releases automatically after checks pass. A workflow file in .github/workflows describes triggers, a runner and steps.
