<!-- topics: programming -->
# Programming Practices: What Textbooks Often Skip

## Big-O cheat sheet
Big-O describes how running time grows with input size n. O(1) constant, O(log n) logarithmic, O(n) linear, O(n log n) linearithmic, O(n squared) quadratic, O(2 to the n) exponential.
Typical examples: reading a list element by index is O(1). Binary search on a sorted list is O(log n). Scanning a list is O(n). Good sorting algorithms such as merge sort and the sort used by Python (Timsort) are O(n log n). Bubble sort and insertion sort are O(n squared) in the worst case. Looking up a key in a hash table (Python dict or set) is O(1) on average.
In Python, "x in my_list" is O(n) but "x in my_set" is O(1) on average, so converting a list to a set before many membership tests is a common easy speed-up. list.append is amortised O(1), list.insert(0, x) is O(n), and collections.deque gives O(1) at both ends.
Big-O ignores constants, so an O(n) algorithm with a huge constant can lose to an O(n log n) one on small inputs. Measure before optimising.

## Reading a Python traceback
Read it from the bottom. The last line gives the exception type and message. The lines above give the call stack, with the most recent call last. Find the deepest line that is in your own code, because the bug is usually there or just before it.
Common exceptions and typical causes:
NameError: a variable is used before it is defined or is misspelled. TypeError: an operation on the wrong type, such as adding a string to an integer, or calling something that is not a function. ValueError: the type is right but the value is not, such as int("abc"). IndexError: list index out of range. KeyError: dictionary key does not exist, use dict.get(key) or check with "in". AttributeError: the object has no such attribute, often because a variable is None. ModuleNotFoundError: the package is not installed in the active environment. IndentationError: mixed tabs and spaces or wrong indentation. ZeroDivisionError: division by zero. RecursionError: recursion without a base case, or too deep, since the default limit is about 1000 frames.

## Debugging method
Reproduce the bug reliably first. Shrink the example until the smallest input that still fails. Form a hypothesis, then test it with print statements, a debugger breakpoint or a failing test, instead of changing code at random. Change one thing at a time. Explain the problem aloud or in writing (rubber duck debugging), which often reveals the mistake. After the fix, add a test so the bug cannot return.

## Python pitfalls
Mutable default arguments: def add(x, items=[]) shares one list across all calls. Use items=None and create the list inside the function.
"is" checks identity, "==" checks equality. Use "is" only for None, True and False.
Copying: b = a for a list makes both names point to the same list. Use a.copy() or list(a) for a shallow copy, and copy.deepcopy for nested data.
Integer division: / always gives a float, // gives floor division. Floating-point numbers cannot represent 0.1 exactly, so compare with math.isclose instead of ==.
Modifying a list while looping over it skips items. Build a new list with a comprehension instead.
Strings are immutable. Building a long string with += in a loop is slow, so collect pieces and use "".join(pieces).
Reading files: use "with open(path, encoding='utf-8') as f" so the file closes automatically and Arabic text is read correctly on every operating system.

## Virtual environments and dependencies
A virtual environment keeps the packages of one project separate from others. Create one with python -m venv .venv, activate it (source .venv/bin/activate on Linux and macOS, .venv\Scripts\activate on Windows), then install packages with pip. Record dependencies in requirements.txt with pip freeze or write them by hand. Never commit the .venv folder. Always check which Python and pip you are running with "which python" or "python -m pip --version" when installs do not seem to work.

## Testing
A unit test checks one small piece of code in isolation. With pytest, a test is a function whose name starts with test_ and that uses plain assert statements. Run all tests with pytest. Good tests cover normal cases, edge cases (empty input, zero, negative, very large) and error cases. Mocks replace slow or external things such as network calls. Test-driven development writes the failing test first, then the code. Aim for useful tests, not just a high coverage number.

## Clean code habits
Use meaningful names. Keep functions short and focused on one job. Avoid copying and pasting code, and extract a function instead (the DRY principle). Prefer returning values over changing global state. Write comments to explain why, not what. Handle errors explicitly instead of catching every exception and ignoring it. Format code automatically with tools such as black and check it with a linter such as ruff or flake8.

## OOP, SOLID and common patterns in one page
Four OOP ideas: encapsulation (hide internal state behind methods), abstraction (expose a simple interface), inheritance (reuse behaviour from a parent class) and polymorphism (different classes respond to the same method call in their own way). Prefer composition over inheritance when classes only share some behaviour.
SOLID: Single responsibility (a class has one reason to change), Open-closed (extend behaviour without editing old code), Liskov substitution (subclasses can replace their parent safely), Interface segregation (small focused interfaces), Dependency inversion (depend on abstractions, not concrete details).
Patterns you will meet: Singleton (one instance), Factory (create objects without naming the class), Observer (notify subscribers of changes), Strategy (swap algorithms at run time), Decorator (add behaviour by wrapping).

## APIs, REST and JSON
An API lets programs talk to each other. A REST API uses HTTP methods on resources: GET reads, POST creates, PUT replaces, PATCH updates part of a resource, DELETE removes. GET, PUT and DELETE are meant to be idempotent, which means repeating the request has the same effect as sending it once.
Status codes: 200 OK, 201 Created, 204 No Content, 301 and 302 redirects, 400 Bad Request, 401 Unauthorized (not authenticated), 403 Forbidden (authenticated but not allowed), 404 Not Found, 409 Conflict, 422 Unprocessable Entity (validation failed, used by FastAPI), 429 Too Many Requests, 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable.
JSON is the usual data format: objects with key-value pairs, arrays, strings, numbers, booleans and null. In Python, json.loads parses text into dicts and lists, and json.dumps does the reverse. Use ensure_ascii=False in json.dumps to keep Arabic characters readable.

## Concurrency in one page
A process has its own memory. Threads share the memory of a process. Concurrency means handling many tasks by interleaving them, and parallelism means running tasks at the same instant on several cores. In CPython the global interpreter lock (GIL) lets only one thread run Python bytecode at a time, so threads help for waiting on I/O (network, disk) but not for CPU-heavy work. For CPU-heavy work use multiprocessing, or libraries written in C such as NumPy. asyncio runs many I/O tasks in one thread using async and await.
A race condition happens when the result depends on the unpredictable order of operations on shared data. A deadlock happens when tasks wait for each other forever. Protect shared data with locks, or better, avoid sharing it by passing messages through queues.

## Unicode and Arabic text
Computers store text as code points encoded in bytes. UTF-8 is the standard encoding and handles Arabic and English together. Always read and write files as UTF-8. Arabic is written right to left, and letters change shape depending on position, which the display layer handles, not your string data. Python stores Arabic strings in logical order, so len() counts code points, not visible letters. Diacritics (tashkeel) are separate code points, so removing them is often useful before searching or comparing text. When a terminal shows Arabic letters disconnected or reversed, that is usually a display limitation, not corrupted data.

## Linux command line essentials
pwd shows the current folder, ls lists files (ls -la shows details and hidden files), cd changes folder, mkdir creates a folder, cp copies, mv moves or renames, rm deletes (rm -r deletes folders, and there is no recycle bin, so be careful), cat prints a file, less views it page by page, grep searches text (grep -r "word" . searches recursively), find locates files, head and tail show the start and end of a file (tail -f follows a log), chmod changes permissions, sudo runs a command as administrator.
Pipes send the output of one command into another: cat log.txt | grep ERROR | wc -l counts error lines. Redirection writes output to a file: command > out.txt overwrites, command >> out.txt appends. Permissions are shown as rwx for owner, group and others, and chmod 755 means the owner can read, write and execute, while others can read and execute.

## Docker in one page
An image is a read-only template that contains an application and its dependencies. A container is a running instance of an image. A Dockerfile lists the steps to build an image: FROM chooses the base image, COPY adds files, RUN executes a command at build time, CMD sets the default command at run time.
Key commands: docker build -t name . builds an image, docker run -p 8000:8000 name starts a container and maps host port 8000 to container port 8000 (the order is host:container), docker ps lists running containers, docker logs shows output, docker exec -it id sh opens a shell inside, docker stop and docker rm stop and remove. Data inside a container is lost when it is removed unless you mount a volume with -v. Docker Compose describes several containers (for example an app and a database) in one docker-compose.yml file and starts them together.

## How to study programming effectively
Write code every day, even for twenty minutes. Type examples instead of only reading them. Build small projects that you care about, because they force you to meet real problems. Read error messages carefully before searching. Learn to search with the exact error text. Review old code after a few weeks and improve it. Explain concepts to someone else. Use version control from the first project.
