<!-- Merged study notes (SRC017). Each document starts with an id/topics comment followed by a '# Title' line. -->

<!-- id: programming_practices; topics: programming -->
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

<!-- id: algorithms_with_code; topics: programming -->
# Algorithms and Data Structures With Tested Python Code

## How to approach an algorithm problem
Start by stating the input, the output and the constraints in your own words. Work a tiny example by hand. Write the simplest correct solution first, even if it is slow, because a correct slow solution is a reference to test against. Then estimate the running time in Big-O, find the repeated work, and improve it with a better data structure or a better idea. Test the edge cases: empty input, one element, duplicates, already sorted input, and the largest allowed size. All code in this note was run and checked.

## Linear search and binary search
Linear search checks elements one by one and takes O(n) time. Binary search works only on sorted data. It looks at the middle element and throws away the half that cannot contain the target, so each step halves the problem and the time is O(log n). For one million elements that is about 20 steps instead of one million.
```python
def binary_search(items, target):
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```
For the list [2, 5, 8, 12, 16, 23, 38, 56], binary_search for 23 returns index 5, and for 7 returns -1. The classic bugs are using low < high instead of low <= high (which misses the last candidate) and forgetting the +1 and -1 (which can loop forever). Python already provides the bisect module, where bisect_left(items, x) returns the position where x is or should be inserted, so use it in real code.

## Sorting: the main ideas
Insertion sort builds a sorted prefix by inserting each next element into place. It is O(n squared) in the worst case but very fast on nearly sorted data and on tiny lists. Selection sort repeatedly picks the minimum and is always O(n squared). Merge sort splits the list in half, sorts each half recursively and merges the two sorted halves in linear time, which gives O(n log n) in every case, and it needs O(n) extra memory. Quick sort picks a pivot, partitions the elements into smaller and larger, and sorts each side recursively. It is O(n log n) on average and O(n squared) in the worst case when pivots are chosen badly, but it is fast in practice.
```python
def merge_sort(items):
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid])
    right = merge_sort(items[mid:])
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
```
```python
def quick_sort(items):
    if len(items) <= 1:
        return items
    pivot = items[len(items) // 2]
    less = [x for x in items if x < pivot]
    equal = [x for x in items if x == pivot]
    greater = [x for x in items if x > pivot]
    return quick_sort(less) + equal + quick_sort(greater)
```
Both return [1, 2, 3, 5, 7, 9] for the input [5, 2, 9, 1, 7, 3]. The quick sort above is the readable teaching version, not the in-place version used in libraries. A sort is stable if equal elements keep their original relative order, which matters when sorting by one field after another. Python's built-in sorted() and list.sort() use Timsort, which is stable, runs in O(n log n) and is very fast on partly ordered data. Use the key argument to sort by a field: sorted(students, key=lambda s: s["gpa"], reverse=True). Writing your own sort is a learning exercise, in real projects use the built-in one.

## Recursion and the call stack
A recursive function solves a problem by calling itself on a smaller version of the same problem. It needs a base case that stops the recursion and a recursive step that makes progress toward the base case. Each call gets its own frame on the call stack, and Python limits the depth to about 1000 frames by default, after which it raises RecursionError.
```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```
factorial(5) is 120. Tracing it by hand: factorial(5) waits for factorial(4), which waits for factorial(3), down to factorial(1) which returns 1, and then the results multiply on the way back up.
The naive Fibonacci function calls itself twice per call and recomputes the same values again and again, which makes it exponential, roughly O(2 to the n). fib(35) takes about a second on a typical laptop and fib(45) takes minutes. Memoization stores results already computed, and in Python it takes one line with functools.lru_cache.
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```
Now fib(50) is 12586269025 and the time is O(n). Any recursion can be rewritten as a loop with an explicit stack, which avoids the depth limit. Use recursion when the problem is naturally recursive, such as trees, nested folders, divide and conquer and backtracking.

## Dynamic programming
Dynamic programming applies when a problem has overlapping subproblems (the same smaller problem appears many times) and optimal substructure (the best answer is built from best answers of smaller problems). You can write it top-down with memoization, as for Fibonacci, or bottom-up by filling a table from small cases to large ones.
The coin change problem asks for the minimum number of coins that add up to an amount. A greedy approach that always takes the biggest coin works for normal currency but fails in general. With coins 1, 3 and 4 and amount 6, greedy takes 4+1+1 which is 3 coins, while the best is 3+3 which is 2 coins. Dynamic programming gets it right by computing the best answer for every amount from 0 up to the target.
```python
def min_coins(coins, amount):
    INF = float("inf")
    best = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] + 1 < best[a]:
                best[a] = best[a - c] + 1
    return best[amount] if best[amount] != INF else -1
```
min_coins([1, 5, 10, 25], 63) is 6 (25+25+10+1+1+1), min_coins([1, 3, 4], 6) is 2, and min_coins([4, 5], 7) is -1 because 7 cannot be formed. The time is O(amount times number of coins). The recipe for any dynamic programming problem: define what best[a] means, write the recurrence that links it to smaller values, set the base case, and decide the order in which to fill the table.

## Graphs: representation, BFS and DFS
A graph has nodes (vertices) and edges. Social networks, road maps, web links and network topologies are graphs. The usual Python representation is an adjacency list: a dict that maps each node to the list of its neighbours.
Breadth-first search (BFS) explores level by level using a queue, so in an unweighted graph the first time it reaches a node is along a shortest path in number of edges. Depth-first search (DFS) goes as deep as possible along one branch, using recursion or a stack, then backtracks. Both take O(V + E) time.
```python
from collections import deque

def bfs_shortest_path(graph, start, goal):
    queue = deque([[start]])
    visited = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        for nxt in graph.get(node, []):
            if nxt not in visited:
                visited.add(nxt)
                queue.append(path + [nxt])
    return None
```
```python
def dfs(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    for nxt in graph.get(node, []):
        if nxt not in visited:
            dfs(graph, nxt, visited)
    return visited
```
With graph = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": ["F"], "E": ["F"], "F": []}, bfs_shortest_path(graph, "A", "F") returns ["A", "B", "D", "F"], and dfs(graph, "A") visits all six nodes. Without the visited set, a graph that has a cycle makes the search run forever. Use BFS for shortest paths in unweighted graphs and for level-order traversal. Use DFS for exploring all possibilities, detecting cycles, topological sorting and solving mazes.

## Shortest paths with weights: Dijkstra
When edges have non-negative weights, Dijkstra's algorithm finds the cheapest path from a source to all nodes. It repeatedly takes the unvisited node with the smallest known distance and relaxes its outgoing edges. A priority queue (a heap) makes finding that node fast, and the total time is O((V + E) log V). It does not work with negative edge weights, where Bellman-Ford is used instead. Routing protocols such as OSPF use this algorithm.
```python
import heapq

def dijkstra(graph, source):
    dist = {source: 0}
    heap = [(0, source)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist.get(node, float("inf")):
            continue
        for nxt, w in graph.get(node, []):
            nd = d + w
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                heapq.heappush(heap, (nd, nxt))
    return dist
```
For graph = {"A": [("B", 4), ("C", 1)], "C": [("B", 2), ("D", 7)], "B": [("D", 1)]}, dijkstra(graph, "A") gives A 0, C 1, B 3 and D 4. Notice that the direct edge A to B costs 4 but going through C costs 1 + 2 = 3, which is cheaper.

## Hash tables in everyday problems
A hash table maps keys to values by computing a hash of the key to choose a bucket. Two different keys can land in the same bucket, which is called a collision, and implementations handle it by chaining or by probing for another slot. With a good hash function lookup, insertion and deletion are O(1) on average. Keys must be hashable and immutable, so a Python list cannot be a key but a tuple can.
Counting things is the most common use. collections.Counter does it in one line, and Counter("banana") gives a count of 3 for a, 2 for n and 1 for b. The two-sum problem asks for two numbers in a list that add up to a target. The brute force version checks all pairs in O(n squared). With a dict that remembers the numbers already seen, it takes one pass.
```python
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i
    return None
```
two_sum([2, 7, 11, 15], 9) returns (0, 1). This pattern, trading memory for time with a dict or set, appears in a large share of interview and exam questions.

## Stacks and queues
A stack is last in, first out and a queue is first in, first out. In Python a list works as a stack with append and pop, and collections.deque works as a queue with append and popleft in O(1). Stacks power undo features, the call stack and expression parsing. Queues power task scheduling, buffering and BFS.
Checking balanced brackets is the classic stack problem: push every opening bracket, and for each closing bracket the top of the stack must be its matching opening bracket.
```python
def is_balanced(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
```
is_balanced("{[()]}") is True, is_balanced("([)]") is False and is_balanced("((") is False because the stack is not empty at the end.

## Two pointers and sliding window
Many array problems that look like they need two nested loops can be solved in one pass. With two pointers you move two indexes through the data, usually from both ends of a sorted list or at different speeds. A sliding window keeps a running value for a block of k consecutive items and updates it by adding the new item and removing the oldest instead of recomputing from scratch.
```python
def max_sum_window(nums, k):
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best
```
max_sum_window([2, 1, 5, 1, 3, 2], 3) is 9, from the window 5, 1, 3. The time is O(n) instead of O(n times k).

## Trees and heaps in brief
A binary tree has nodes with at most two children. A binary search tree keeps smaller values on the left and larger on the right, which gives O(log n) search when the tree is balanced, and O(n) when it degenerates into a list, so real systems use self-balancing trees such as AVL and red-black trees. B-trees, which are wide and shallow, are used by databases for indexes because they minimise disk reads. A heap is a tree-shaped structure where the smallest (min-heap) or largest (max-heap) element is always at the top, which makes a priority queue. Python's heapq module provides a min-heap on a list, and heapq.nlargest(3, items) finds the three largest without sorting everything.

## Choosing a data structure
Need fast lookup by key: dict. Need to check membership or remove duplicates: set. Need ordered items you will index and append to: list. Need to add and remove at both ends: deque. Need always the smallest or largest item: heap. Need sorted order with fast insertion and search: balanced tree or the bisect module on a list. Need to model relationships: graph. Need a fixed record of values: tuple or a dataclass. When you are unsure, write the simplest version first and measure, because the most common performance bug is using a list where a set or dict belongs.

<!-- id: javascript_web_fundamentals; topics: programming,web_security -->
# JavaScript and Web Fundamentals Explained

## How a web page is built from three languages
HTML describes the structure and content of a page: headings, paragraphs, links, images, forms. CSS describes the appearance: colours, fonts, spacing and layout. JavaScript describes the behaviour: reacting to clicks, changing the page, and talking to servers. The browser downloads the HTML, builds a tree of elements called the DOM (Document Object Model), applies the CSS, and runs the JavaScript, which can read and change that tree. Seeing the three roles as separate makes debugging easier: if the text is wrong look at HTML, if it looks wrong look at CSS, if it does the wrong thing look at JavaScript.
A minimal page needs the doctype, a head with the character encoding and title, and a body. Always declare UTF-8 with a meta charset tag, and for Arabic pages set the language and direction on the root element, for example html lang="ar" dir="rtl". Right-to-left pages work best with CSS logical properties such as margin-inline-start and padding-inline-end instead of margin-left and padding-right, because the logical versions flip automatically with the direction.

## The CSS box model and layout
Every element is a box made of four layers from inside to outside: content, padding, border and margin. By default the width property sets only the content width, so adding padding and border makes the element wider than you declared. Setting box-sizing: border-box makes width include padding and border, which is what most people expect, and many projects apply it to all elements.
Flexbox lays items out in one dimension, a row or a column. Setting display: flex on the container, then justify-content to distribute space along the main axis and align-items to align on the other axis, solves most centring and navigation-bar problems. Grid lays out in two dimensions with rows and columns. Media queries such as @media (max-width: 600px) apply rules only on narrow screens, which is the basis of responsive design, together with the viewport meta tag.
When several CSS rules compete, the more specific selector wins: an id selector beats a class selector, which beats an element selector, and when specificity is equal the later rule wins. Inline styles beat all of these, and !important overrides almost everything, so avoid it.

## Variables, scope and types
Declare variables with let when the value will change and const when it will not. Avoid var, which has function scope and is hoisted, and which causes surprising bugs. const does not make an object immutable, it only prevents reassigning the variable, so you can still change the properties of a const object.
JavaScript has primitive types string, number, boolean, null, undefined, bigint and symbol, and objects, which include arrays and functions. typeof null returns "object", a historical mistake. All numbers are 64-bit floating point, so 0.1 + 0.2 equals 0.30000000000000004 and the usual advice is to compare with a tolerance or work in integers such as cents.
Use === and !== (strict equality). The loose == converts types and gives surprises such as "5" == 5 being true. Falsy values are false, 0, an empty string, null, undefined and NaN, and everything else is truthy, including the string "0" and an empty array. NaN is not equal to itself, so check with Number.isNaN.

## Functions, closures and array methods
A function can be declared with the function keyword or written as an arrow function, which is shorter and does not have its own this. Functions are values, so they can be stored in variables, passed to other functions and returned. A closure is a function that remembers the variables of the place where it was created, even after that place has finished running. This is how private state is made.
```javascript
function makeCounter() {
  let count = 0;
  return function () {
    count += 1;
    return count;
  };
}
const next = makeCounter();
console.log(next(), next(), next());
```
This prints 1 2 3, because every call to next updates the same hidden count. A different counter created by calling makeCounter again has its own separate count.
The array methods map, filter and reduce replace many loops. map returns a new array by transforming each item, filter keeps the items for which the function returns true, and reduce folds all items into a single value.
```javascript
const nums = [1, 2, 3, 4, 5, 6];
const doubled = nums.map(n => n * 2);
const evens = nums.filter(n => n % 2 === 0);
const total = nums.reduce((sum, n) => sum + n, 0);
console.log(doubled, evens, total);
```
The output is [2, 4, 6, 8, 10, 12] then [2, 4, 6] then 21. Also learn forEach, find, some, every, includes and sort. Careful: sort without a comparison function sorts items as strings, so [10, 9, 1].sort() gives [1, 10, 9]. Use sort((a, b) => a - b) for numbers.

## Objects, destructuring, spread and JSON
Objects store key-value pairs. Destructuring extracts values into variables, and the spread operator copies or merges arrays and objects, which is the usual way to make a modified copy without changing the original.
```javascript
const user = { name: "Lina", city: "Amman", age: 22 };
const { name, city } = user;
const older = { ...user, age: 23 };
console.log(name, city, older.age, user.age);
const text = JSON.stringify(user);
const back = JSON.parse(text);
console.log(text, back.city);
```
This prints Lina Amman 23 22 and then the JSON text {"name":"Lina","city":"Amman","age":22} and Amman. JSON.stringify turns a value into text and JSON.parse turns text back into a value. JSON keys must use double quotes, and functions and undefined values are dropped by stringify. The spread copy is shallow, so nested objects are still shared between the copy and the original.

## Common loop and scope mistake
A classic puzzle: three timers created in a loop with var all print the same number, because they share one variable i, which has reached 3 when the timers finally run. With let each iteration gets its own i.
```javascript
for (var i = 0; i < 3; i++) setTimeout(() => console.log("var", i), 0);
for (let j = 0; j < 3; j++) setTimeout(() => console.log("let", j), 0);
```
The first loop prints var 3 three times and the second prints let 0, let 1, let 2.

## The DOM and events
The DOM exposes the page as objects. document.querySelector("css selector") returns the first matching element and querySelectorAll returns all matches. You can change text with textContent, classes with classList.add and classList.toggle, and attributes with setAttribute. Events such as click, input and submit are handled with addEventListener.
```javascript
const button = document.querySelector("#save");
const list = document.querySelector("#items");
button.addEventListener("click", () => {
  const li = document.createElement("li");
  li.textContent = "New item";
  list.appendChild(li);
});
list.addEventListener("click", (event) => {
  if (event.target.matches("li")) event.target.classList.toggle("done");
});
```
The second listener shows event delegation: one listener on the parent handles clicks on all current and future children, which is more efficient than attaching a listener to every item. Place the script at the end of the body or use the defer attribute so that the elements exist when the code runs. Use textContent, not innerHTML, whenever the text comes from users or from a server, because innerHTML parses the string as HTML and enables cross-site scripting (XSS) attacks.

## The event loop and asynchronous code
JavaScript runs your code on one thread. Slow operations such as network requests and timers are handed to the browser, and their callbacks are queued to run later when the call stack is empty. Promise callbacks go into the microtask queue, which runs before the next timer callback. This explains the order of this example.
```javascript
console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
console.log("D");
```
It prints A, D, C, B: first the synchronous lines A and D, then the promise microtask C, and finally the timer B, even though its delay was zero. A long synchronous loop blocks the page, because nothing else can run until it finishes.
A Promise represents a value that will be available later and has three states: pending, fulfilled and rejected. async and await are syntax that lets you write promise code in a straight line. An async function always returns a promise, and await pauses that function until the promise settles, without blocking the page. Handle errors with try and catch. Forgetting await is the most common bug: you then get a Promise object instead of the value.
```javascript
const wait = (ms, value) => new Promise(resolve => setTimeout(() => resolve(value), ms));
async function main() {
  const first = await wait(20, "one");
  const [a, b] = await Promise.all([wait(30, "two"), wait(10, "three")]);
  console.log(first, a, b);
}
main();
```
This prints one two three. Promise.all runs the two waits at the same time and returns when both are done, so it takes about 30 milliseconds, not 40. Use it for independent requests.

## Calling a server with fetch
fetch sends an HTTP request and returns a promise for the response. A very common beginner mistake is thinking fetch rejects on HTTP errors. It does not: a 404 or 500 response still resolves normally, and it rejects only on network failures. Always check response.ok.
```javascript
async function loadStudents() {
  try {
    const response = await fetch("/api/students");
    if (!response.ok) throw new Error("HTTP " + response.status);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Could not load students:", error);
    return [];
  }
}
```
To send JSON use method: "POST", headers: {"Content-Type": "application/json"} and body: JSON.stringify(object). If the browser blocks a request to another site with a message about CORS, the server of that other site must send the right Access-Control-Allow-Origin header. You cannot fix it from the browser code, and a CORS rule is a browser protection, not a server security feature.

## Storage in the browser
localStorage keeps small strings per site and persists after the browser closes, and sessionStorage lasts for the tab session. Both store only strings, so use JSON.stringify and JSON.parse. Never store passwords or secret tokens there, because any script on the page can read them. Cookies are sent to the server with every request, so keep them small and mark session cookies HttpOnly, Secure and SameSite.

## Modules, Node.js and npm
Modern JavaScript splits code into modules with export and import. Node.js runs JavaScript outside the browser, for servers and tools, and has no document or window objects. npm installs packages and records them in package.json, and the node_modules folder, which can be huge, should be listed in .gitignore, since anyone can recreate it with npm install. Always check how maintained a package is before depending on it, because every dependency is also a security risk.

## Debugging in the browser
Open the developer tools with F12. The Console shows errors with the file and line number and lets you run code. The Network tab shows every request with its status, timing and response, which is the fastest way to find out whether a bug is in the front end or the server. The Elements tab shows the live DOM and the CSS rules applied to an element. Use breakpoints in the Sources tab to pause execution and inspect variables. console.log is fine for quick checks, and console.table prints arrays of objects neatly.

## A mini project to practise
Build a to-do list: an input and a button in HTML, a list that grows when you add an item, a click on an item toggles a done class, and the list is saved in localStorage as JSON and restored when the page loads. This one exercise uses variables, functions, arrays, events, the DOM, JSON and browser storage. After it works, add a delete button using event delegation, then load the initial list from a small server using fetch.

<!-- id: sql_worked_examples; topics: databases -->
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

<!-- id: databases_security_devtools; topics: databases,web_security,dev_tools -->
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

<!-- id: networking_fundamentals; topics: networking -->
# Networking Fundamentals: Practical Notes

## IPv4 addressing and subnet math
An IPv4 address has 32 bits, written as four decimal octets such as 192.168.10.77. The prefix length (CIDR notation, for example /26) says how many leading bits identify the network. The remaining bits identify the host inside that network.
The number of addresses in a subnet is 2 to the power of (32 minus prefix). Usable host addresses are that number minus 2, because the first address is the network address and the last is the broadcast address. A /24 has 256 addresses and 254 usable hosts. A /26 has 64 addresses and 62 usable hosts. A /30 has 4 addresses and 2 usable hosts, which is why /30 was traditionally used for point-to-point links. A /31 is a special case allowed on point-to-point links (RFC 3021) with no network or broadcast address.
The subnet mask is the same information in dotted form. /24 is 255.255.255.0, /25 is 255.255.255.128, /26 is 255.255.255.192, /27 is 255.255.255.224, /28 is 255.255.255.240, /29 is 255.255.255.248, /30 is 255.255.255.252.

## How to find the network and broadcast address quickly
Find the interesting octet, the one where the mask is not 255 or 0. Compute the block size as 256 minus the mask value in that octet. Network addresses are multiples of the block size.
Example: 192.168.10.77/26. The mask in the last octet is 192, so the block size is 256 minus 192 which is 64. The blocks start at 0, 64, 128, 192. The address .77 falls in the block starting at 64. So the network address is 192.168.10.64, the broadcast address is 192.168.10.127, and the usable hosts are .65 to .126.
Example: how many /27 subnets fit in a /24? A /27 adds 3 bits to the /24, so there are 2 to the power of 3, which is 8 subnets, each with 32 addresses (30 usable).

## Special and private IPv4 ranges
Private addresses that are not routed on the public internet: 10.0.0.0/8, 172.16.0.0/12 (that is 172.16.0.0 to 172.31.255.255), and 192.168.0.0/16.
Loopback is 127.0.0.0/8, and 127.0.0.1 is localhost. Link-local addresses 169.254.0.0/16 appear when a device fails to get an address from DHCP (called APIPA on Windows). The range 100.64.0.0/10 is used by carriers for carrier-grade NAT.
A common beginner mistake is to think 172.32.x.x is private. It is not. Only 172.16 through 172.31 is private.

## NAT
Network Address Translation lets many private hosts share one public IPv4 address. Home routers do PAT (port address translation, also called NAT overload): the router rewrites the source address and source port of outgoing packets and remembers the mapping in a translation table so replies can be sent back to the right internal host.
NAT is one reason inbound connections to a home network fail by default. To expose a service you need port forwarding, a VPN, or a tunnel. NAT is not a security feature by itself, although the default behaviour of dropping unsolicited inbound traffic helps in practice.

## IPv6 basics
IPv6 addresses are 128 bits, written as eight groups of four hex digits, for example 2001:0db8:0000:0000:0000:0000:0000:0001. Leading zeros in a group can be dropped and one run of all-zero groups can be replaced by two colons, so the example becomes 2001:db8::1.
A typical LAN subnet is a /64. There is no broadcast in IPv6; multicast is used instead. The ARP protocol is replaced by the Neighbor Discovery Protocol (NDP). Addresses beginning with fe80::/10 are link-local and exist on every IPv6 interface. Addresses in 2000::/3 are global unicast. fc00::/7 is unique local, similar in purpose to private IPv4.

## Layers: OSI and TCP/IP in practice
The OSI model has 7 layers: physical, data link, network, transport, session, presentation, application. The TCP/IP model groups these into 4: link, internet, transport, application.
Useful mapping: Ethernet frames and MAC addresses are layer 2. IP packets and routers are layer 3. TCP segments and UDP datagrams are layer 4. HTTP, DNS, SMTP and TLS belong to the application side.
A switch forwards frames using MAC addresses and builds a MAC address table by learning the source address of frames it sees. A router forwards packets between networks using a routing table and the longest prefix match rule: when several routes match a destination, the most specific one (longest prefix) wins.
Hubs are obsolete. A hub repeats every signal to all ports, while a switch sends a frame only to the port where the destination MAC was learned.

## ARP
On an IPv4 Ethernet LAN, a host that knows the destination IP address but not its MAC address sends an ARP request as a broadcast: who has this IP. The owner replies with its MAC address. Hosts cache the answer for a short time. If the destination is on another network, the host ARPs for the default gateway instead, not for the remote host.
ARP has no authentication, which is why ARP spoofing (also called ARP poisoning) is possible on a LAN. Dynamic ARP inspection on managed switches is one defence.

## DHCP
DHCP gives hosts an IP address, mask, default gateway, DNS servers and a lease time. The four messages are DORA: Discover (broadcast from client), Offer (from server), Request (client asks for the offered address), Acknowledge (server confirms).
Clients use UDP port 68 and servers use UDP port 67. A lease is renewed when about half of the lease time has passed. Two DHCP servers on the same LAN without coordination is a common cause of random address conflicts.

## DNS in detail
DNS maps names to records. Common record types: A (name to IPv4), AAAA (name to IPv6), CNAME (alias to another name), MX (mail servers with priority), NS (authoritative name servers), TXT (free text, used for SPF, DKIM and domain verification), PTR (reverse lookup from IP to name), SOA (zone authority information).
Resolution path when you type a name: the application asks the stub resolver of the operating system, which asks a recursive resolver (your ISP, or a public one). If the answer is not cached, the recursive resolver asks a root server, which points to the TLD servers (for example .com), which point to the authoritative servers of the domain, which return the answer. Every answer carries a TTL that says how long it may be cached.
DNS uses UDP port 53 for most queries and TCP port 53 for large responses and zone transfers. DNS over HTTPS and DNS over TLS encrypt queries between the client and the resolver.
When a DNS change seems not to work, the usual reason is caching of the old record until its TTL expires. Lowering the TTL before a planned migration is standard practice.

## TCP in detail
TCP provides a reliable, ordered byte stream. Connection setup is the three-way handshake: SYN from the client, SYN-ACK from the server, ACK from the client. Sequence numbers number the bytes, acknowledgements confirm them, and lost segments are retransmitted after a timeout or after duplicate acknowledgements.
Flow control uses the receiver window: the receiver tells the sender how much data it can buffer. Congestion control (slow start, congestion avoidance, fast retransmit) prevents the sender from overloading the network. The effective sending rate is limited by the smaller of the congestion window and the receiver window.
Closing a connection uses FIN and ACK in each direction. The side that closes first enters TIME_WAIT for a while so that late packets from the old connection are not mixed into a new one. Many sockets in TIME_WAIT on a busy server are normal. Many sockets stuck in CLOSE_WAIT usually mean the application forgot to close its side.
Common TCP flags: SYN start a connection, ACK acknowledge, FIN finish, RST abort immediately, PSH push data to the application.

## UDP and when to use it
UDP has no connection, no ordering, no retransmission and no congestion control. It is a thin layer on top of IP that adds ports and a checksum. It is used when low latency matters more than perfect delivery or when the application handles reliability itself: DNS queries, DHCP, VoIP, online games, video calls, and QUIC (the transport under HTTP/3).

## Well-known ports
20 and 21 FTP, 22 SSH, 23 Telnet (insecure), 25 SMTP, 53 DNS, 67 and 68 DHCP, 80 HTTP, 110 POP3, 123 NTP, 143 IMAP, 161 SNMP, 389 LDAP, 443 HTTPS, 445 SMB, 587 SMTP submission, 993 IMAPS, 3306 MySQL, 3389 RDP, 5432 PostgreSQL, 6379 Redis, 8080 alternative HTTP, 27017 MongoDB.
Ports 0 to 1023 are well-known ports, 1024 to 49151 are registered, and 49152 to 65535 are dynamic ports used as temporary source ports by clients.

## HTTP versions
HTTP/1.1 reuses TCP connections (keep-alive) but handles requests on a connection one after another, which causes head-of-line blocking. HTTP/2 multiplexes many streams over one TCP connection and compresses headers. HTTP/3 runs over QUIC on UDP, which removes TCP-level head-of-line blocking and speeds up connection setup.
HTTPS means HTTP carried inside TLS. TLS 1.3 completes its handshake in one round trip and removes old insecure options. The server proves its identity with a certificate signed by a certificate authority that the client trusts.

## ICMP, ping and traceroute
ICMP carries control and error messages. Ping sends ICMP echo request and waits for echo reply, and it measures round-trip time and packet loss. Traceroute sends packets with TTL values 1, 2, 3 and so on. Each router decrements the TTL, and the router where it reaches zero returns an ICMP time exceeded message, which reveals the path hop by hop. Some routers do not answer, so stars in the output do not always mean a problem.
Ping failing does not prove a host is down, because firewalls often block ICMP.

## MTU and fragmentation
Ethernet usually has an MTU (maximum transmission unit) of 1500 bytes. If a packet is bigger than the MTU of a link, it must be fragmented (IPv4) or the sender must reduce its size using path MTU discovery. Tunnels such as VPNs add headers, so a wrong MTU is a classic cause of "small requests work but large ones hang".

## VLANs
A VLAN splits one physical switch into several logical layer-2 networks. Frames are tagged with IEEE 802.1Q. A trunk port carries several VLANs, an access port carries one. Hosts in different VLANs need a router (or a layer-3 switch) to talk to each other, which is also where access control between them can be applied.

## Routing
Static routes are entered by hand. Dynamic routing protocols exchange routes automatically. RIP is a simple distance-vector protocol with a maximum of 15 hops. OSPF is a link-state protocol used inside an organisation and computes shortest paths with Dijkstra's algorithm. BGP is the path-vector protocol that connects autonomous systems and holds the internet together.
The default route 0.0.0.0/0 matches anything not matched by a more specific route and usually points to the ISP.

## Wi-Fi basics
Wi-Fi is IEEE 802.11. The 2.4 GHz band reaches further but has few non-overlapping channels (1, 6 and 11 in most regions) and more interference. The 5 GHz band is faster with more channels and shorter range. Wi-Fi 6 is 802.11ax. For security use WPA2 or WPA3 and avoid WEP and open networks. WPS push-button or PIN setup has known weaknesses.

## Load balancers, proxies, CDN
A forward proxy acts for clients. A reverse proxy sits in front of servers, and can terminate TLS, cache, compress and route requests. A load balancer spreads requests over several servers using strategies such as round robin, least connections or hashing, and removes unhealthy servers using health checks. A CDN stores copies of content in many locations so users fetch it from a nearby server.

## Troubleshooting method
Work from the bottom up or divide and conquer. First check the cable or Wi-Fi link, then the IP address and gateway, then reachability of the gateway, then reachability of an outside IP such as 8.8.8.8, then DNS by resolving a name. If an IP works but a name does not, the problem is DNS. If the name resolves but the web page does not load, test the port with curl or telnet-style tools and look at firewalls and the service itself.
Useful commands: on Windows ipconfig /all, ping, tracert, nslookup, netstat -ano. On Linux ip addr, ip route, ping, traceroute or mtr, dig, ss -tuln, curl -v. Wireshark and tcpdump show actual packets for deeper analysis.

## Firewalls and VPNs
A stateless packet filter judges each packet alone. A stateful firewall tracks connections, so replies to allowed outbound connections are allowed automatically. The default policy should be deny, with explicit allows for needed traffic. A VPN builds an encrypted tunnel between a device and a network, using protocols like WireGuard, OpenVPN or IPsec. A VPN protects traffic between you and the VPN endpoint, it does not make you anonymous.

<!-- id: network_security; topics: networking,web_security -->
# Network Security Explained: Threats and Defences

## The goals of security: the CIA triad
Security work protects three properties. Confidentiality means only authorised people can read the data. Integrity means data is not changed without authorisation and any change can be detected. Availability means systems and data can be used when needed. Every attack harms one or more of these. Eavesdropping attacks confidentiality, tampering attacks integrity, and a denial of service attack hits availability. When you evaluate a defence, ask which of the three it protects, and what it costs in convenience, because a control that users bypass because it is too painful does not protect anybody.
Related ideas: authentication proves identity, authorisation decides permissions, accounting records what was done (together called AAA), and non-repudiation means a person cannot credibly deny an action, which signatures and audit logs support. The attack surface is the sum of all places an attacker could try to get in, such as open ports, web forms and user accounts, and good security reduces it by switching off what is not needed.

## Threats you will meet most often
Phishing tricks a person into revealing credentials or running something, using fake messages that look real. It is the most common start of real breaches because it attacks people rather than software. Defences are training, careful checking of sender and link, multi-factor authentication, and email filtering.
Malware is hostile software: viruses, worms, trojans, ransomware that encrypts files and demands payment, and spyware. Defences are updates, least privilege, reputable endpoint protection, avoiding unknown attachments, and offline backups that ransomware cannot reach, tested by actually restoring them.
A man-in-the-middle attack places the attacker between two parties so they can read or change traffic. On a LAN it can be done by ARP spoofing, and on public Wi-Fi with a fake access point. The main defence is encryption with authentication, which is what HTTPS and TLS provide, plus not ignoring certificate warnings.
Denial of service attacks overwhelm a service with traffic or requests. A distributed version (DDoS) uses many machines. Defences are rate limiting, scaling, content delivery networks and specialised mitigation services, since a single server cannot absorb a large flood.
DNS spoofing or cache poisoning returns false DNS answers to send users to the wrong server, and DNSSEC and encrypted DNS reduce this risk. Credential stuffing tries passwords leaked from other sites, which is why password reuse is dangerous and why rate limiting, breach checks and multi-factor authentication matter. Insider threats come from people with legitimate access, and least privilege and logging help. Social engineering is the general name for manipulating people, and includes phone calls pretending to be support staff.

## Encryption in transit: how TLS protects you
TLS combines two kinds of cryptography. Asymmetric cryptography uses a key pair: the public key can be shared, and only the matching private key can decrypt or sign. It is slow, so it is used at the start to authenticate the server and agree on a shared secret. Symmetric cryptography uses one shared key to encrypt the actual data quickly. The server's certificate, signed by a certificate authority, links its domain name to its public key, so the browser can be confident it is talking to the real site and not to an impostor.
HTTPS gives confidentiality, integrity and server authentication for web traffic. It does not tell you the site is honest, only that you are connected to the owner of that domain securely. Other examples of the same protection: SSH for remote administration, SFTP instead of FTP, IMAPS and SMTPS for mail, and WPA2 or WPA3 for Wi-Fi. Plain HTTP, FTP and Telnet send everything, including passwords, in readable form and should not be used on untrusted networks.

## Firewalls, IDS and IPS
A firewall enforces rules about which traffic may pass. A packet filter checks addresses, ports and protocols. A stateful firewall also tracks connections, so replies to allowed outgoing connections are allowed automatically. A web application firewall understands HTTP and can block patterns such as SQL injection attempts. The best default is deny everything and then allow only what is required, instead of allowing everything and trying to block the bad.
An intrusion detection system (IDS) watches traffic or logs and raises alerts. An intrusion prevention system (IPS) sits in the traffic path and can block. Detection can be signature-based, which finds known patterns, or anomaly-based, which finds unusual behaviour and gives more false alarms. Alerts have value only if someone reads them, so tune them and keep logs centrally.

## Network design: segmentation and zero trust
Do not put everything in one flat network. Segmentation splits the network into zones with firewall rules between them, so a compromised laptop cannot reach the database server. A common layout is a DMZ for public-facing servers, an internal zone for staff and a restricted zone for sensitive data. VLANs implement the separation on switches. Guest Wi-Fi should be isolated from the office network, and IoT devices such as cameras and smart TVs should sit in their own segment because they are rarely updated.
Zero trust is the idea of not trusting a device or user just because it is inside the network. Every request is verified using identity, device health and context, and access is limited to the minimum required. It fits modern work where staff and applications are outside the old office perimeter.

## Wi-Fi and home network security
Use WPA3 if all devices support it, otherwise WPA2 with AES and a long passphrase. Avoid WEP and open networks without protection. Change the default administrator password on the router, update its firmware, and disable remote administration from the internet unless you truly need it. WPS has known weaknesses and is best switched off. Give guests a separate guest network. On public Wi-Fi assume others can see your connection, rely on HTTPS, and use a VPN for extra protection if you do not trust the network. A VPN moves trust to the VPN provider, it does not make you anonymous.

## Passwords, MFA and account hygiene
Long unique passphrases are better than short complex ones. Use a password manager so every site gets a different password. Turn on multi-factor authentication, preferring app-based codes or hardware keys and passkeys to SMS codes, because SMS can be intercepted through SIM swapping. Check whether your accounts appear in known data breaches on a breach-notification service. For administrators, separate everyday accounts from administrative ones and never share accounts.

## Securing remote access with SSH
SSH gives encrypted remote shell access, on port 22 by default. Use key-based authentication instead of passwords: generate a key pair with ssh-keygen, put the public key into the server's authorized_keys file, and keep the private key secret and protected with a passphrase. Then disable password login and direct root login in the server configuration file (PasswordAuthentication no and PermitRootLogin no), restrict who may connect with firewall rules, and keep the software updated. Tools such as fail2ban block addresses after repeated failures. Changing the port reduces log noise but is not real security.

## Scanning and testing, ethically
Port scanners such as nmap show which ports and services a host exposes, and they are standard tools for defenders to audit their own systems and understand their attack surface. Only scan systems you own or have written permission to test, because unauthorised scanning and testing is illegal in many countries and can be treated as an attack. Practise on your own lab or on deliberately vulnerable training environments built for learning. A penetration test is an authorised simulated attack with an agreed scope, and a vulnerability scan is an automated search for known weaknesses, which is cheaper but shallower.
For defenders, the useful outputs are: which ports are open that should not be, which services are outdated, and which systems nobody knew existed. Closing unused ports and patching exposed services removes most easy risk.

## Patching and vulnerability management
Many breaches exploit flaws for which a fix already existed. Keep an inventory of what you run, subscribe to security advisories for it, apply updates quickly for internet-facing systems, and test updates before large rollouts. Vulnerabilities are catalogued with CVE identifiers and a severity score called CVSS, but severity must be read together with exposure: a critical flaw in a service that is not reachable is less urgent than a medium flaw on a public server. Dependency scanners can check the libraries of your own code for known problems.

## Logging, monitoring and incident response
You cannot investigate what you did not record. Log authentication attempts, administrative actions, firewall decisions and application errors, keep logs on a separate system so an intruder cannot erase them, and keep clocks synchronised with NTP so events from different machines line up. An incident response plan has phases: preparation, detection, containment (isolate affected systems), eradication (remove the cause), recovery (restore from clean backups) and lessons learned. Decide in advance who is called, who may disconnect a system and how to communicate. The 3-2-1 backup rule means three copies of data on two kinds of media with one copy offsite or offline.

## How the OWASP Top 10 relates to the network view
Network defences such as firewalls and TLS do not stop application flaws. A perfectly encrypted connection can still carry a SQL injection payload or a request that exploits broken access control. Security needs both layers: the network protects the path and the perimeter, and the application validates input, checks permissions on the server, handles sessions safely and keeps dependencies updated. Treat the application and the network as one system.

## A checklist for a small project
Use HTTPS everywhere. Keep secrets out of the repository and rotate any that leaked. Give each service its own least-privileged account. Close all ports you do not use and allow SSH only with keys. Enable automatic security updates where possible. Take automated backups and test a restore. Add rate limiting to login and public API endpoints. Log important events and look at the logs. Turn on multi-factor authentication for every administrative account, including your cloud and GitHub accounts.

<!-- id: cloud_and_deployment; topics: dev_tools,networking,web_security -->
# Cloud Computing and Deploying a Project

## What the cloud is, in plain terms
Cloud computing means renting computing resources over the internet and paying for what you use, instead of buying and maintaining your own servers. The provider owns data centres in many regions, and you create virtual machines, storage, databases and networks with a few clicks or lines of configuration. The main benefits are speed (a server in minutes), elasticity (add or remove capacity as demand changes) and no hardware maintenance. The main risks are cost surprises, leaving things misconfigured, and depending on one provider.
The three service models describe how much the provider manages. Infrastructure as a Service (IaaS) gives you virtual machines, disks and networks, and you manage the operating system and everything above it. Platform as a Service (PaaS) gives you a place to run your code and you manage only the application and its data. Software as a Service (SaaS) is a finished application you just use, such as email or a document editor. The shared responsibility model says the provider secures the cloud itself, and you secure what you put in it: your data, accounts, configuration and access rules.

## Core building blocks
A virtual machine is a software-defined computer. A container packages an application with its dependencies and starts in seconds, and an orchestrator such as Kubernetes runs and restarts containers across many machines. Serverless functions run your code only when triggered and charge per execution, so you do not manage servers at all. Object storage holds files as objects in buckets, and it is cheap, durable and accessed over HTTP. Managed databases handle backups, patching and failover for you. A virtual private network inside the cloud (a VPC) is your private address space with subnets, route tables and security groups acting as virtual firewalls. A load balancer spreads traffic across several instances and checks their health, and DNS maps your domain name to the load balancer or server.
Regions and availability zones matter. A region is a geographic area, and an availability zone is an isolated data centre within it. Spreading instances across zones keeps the service alive when one zone fails, and choosing a region near your users reduces latency.

## Scaling and reliability
Vertical scaling makes one machine bigger. Horizontal scaling adds more machines, which usually scales further and survives failures, but it needs the application to be stateless, meaning requests do not depend on data kept in the memory or on the disk of one instance. Keep state in a database, a cache or object storage. Caches such as Redis reduce database load. Health checks remove broken instances from rotation. Design for failure: assume that any machine can disappear and that a request can be retried, which is why write operations should be idempotent where possible.

## Configuration and secrets: the twelve-factor ideas
Keep configuration out of the code, in environment variables. Treat backing services such as databases as attached resources defined by a URL. Make the build, release and run stages separate. Run the app as stateless processes, write logs to standard output, and let the platform collect them. Keep development and production as similar as possible. Never commit secrets such as API keys, tokens and passwords to Git: use environment variables, a .env file listed in .gitignore, or the secret store of the platform. If a secret was ever pushed to a repository, treat it as compromised and rotate it, because deleting the commit does not remove it from history or from copies.

## Containerising a Python web app
A typical Dockerfile for a FastAPI application looks like this.
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Copying requirements.txt and installing before copying the rest of the code lets Docker reuse the cached layer of installed packages when only your code changes, which makes rebuilds much faster. Binding to 0.0.0.0 is required so that the app is reachable from outside the container, since 127.0.0.1 inside a container is only the container itself. Add a .dockerignore file listing .git, .venv, __pycache__ and .env so they are not copied into the image.
Docker Compose runs several containers together. Services reach each other by service name on the internal network, so the app connects to the database at the host name db, not localhost.
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/appdb
    depends_on:
      - db
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: appdb
    volumes:
      - dbdata:/var/lib/postgresql/data
volumes:
  dbdata:
```
The named volume dbdata keeps the database files when the container is recreated. The passwords above are only for local practice, and real deployments should take them from a secret store. Start everything with docker compose up --build, and stop it with docker compose down.

## Continuous integration with GitHub Actions
A workflow is a YAML file in .github/workflows. It defines when it runs, on which kind of machine, and which steps to execute. This one runs the tests on every push and pull request.
```yaml
name: tests
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest
```
Make the main branch protected so that a pull request cannot be merged unless these checks pass. Store deployment credentials in the repository secrets and never in the workflow file. Extend the workflow with a linter, a dependency vulnerability scan and a build of the Docker image. Continuous delivery adds an automatic deployment step after the checks pass.

## Deploying: a practical path for a student project
For a first deployment, a PaaS or a container hosting service is the easiest because it handles servers, TLS certificates and restarts. A path that works: push the project to GitHub, connect the repository to the platform, set the environment variables in its dashboard, and let it build from the Dockerfile. If you rent a plain virtual machine instead, you must also manage updates, the firewall, a reverse proxy such as Nginx or Caddy for HTTPS, a process manager so the app restarts after a crash or reboot, and backups.
After deployment check these things: the app starts from a clean checkout using only the README instructions, the health endpoint answers, HTTPS works and HTTP redirects to it, secrets are not in the image or the repository, debug mode is off, and logs show errors. Add a simple health route such as /health that returns status ok, which monitoring tools and load balancers can poll.

## Domains, DNS and HTTPS
To use your own domain, register it, then create DNS records: an A record maps the name to an IPv4 address, an AAAA record to an IPv6 address, and a CNAME record points a name to another name, which is the usual way to connect a subdomain to a platform. DNS changes take time to spread because of caching, up to the TTL of the old record. Free automatic certificates from Let's Encrypt are issued after you prove control of the domain, and many platforms and servers such as Caddy renew them automatically. Certificates expire, and an expired certificate is a common cause of outages, so monitor expiry dates.

## Monitoring, logging and cost control
Monitoring answers whether the system is healthy, using metrics such as request rate, error rate, latency and resource use, and alerts that notify someone when thresholds are crossed. The useful starting set is the four golden signals: latency, traffic, errors and saturation. Logs explain why, and structured logs in JSON make searching easier. Tracing follows one request across services.
Costs can grow silently. Set a budget and billing alerts on day one, switch off resources you are not using, delete old snapshots and unattached disks, choose small instance sizes while testing, and remember that data leaving the provider (egress) is charged. Tag resources with the project name so you can see what each one costs. Free tiers have limits and expire, so read them before relying on them.

## Running an AI chatbot like this project in production
The model server and the web interface are separate concerns. Local models served by Ollama need a machine with enough memory, and a GPU makes them much faster, so a small cloud virtual machine without a GPU will answer slowly with a 7B model. Options are: run everything locally for the demo, rent a GPU machine only while needed, or call a hosted model API and keep only retrieval and the interface on your server. Keep the vector index and the SQLite knowledge base as files that are rebuilt by a script, so any machine can recreate them. Protect the interface with rate limiting, because every request costs compute, and never expose the Ollama port 11434 directly to the internet, since it has no authentication. Put it behind your application or a private network.

<!-- id: ai_llm_practical; topics: ai -->
# AI, Machine Learning and LLMs: Practical Notes

## AI, ML and deep learning: how the terms relate
Artificial intelligence is the broad goal of making machines do tasks that need intelligence. Machine learning is the part of AI where a system learns patterns from data instead of following hand-written rules. Deep learning is machine learning with neural networks that have many layers. Large language models are deep learning models trained on huge amounts of text to predict the next token.

## The standard ML workflow
Define the problem and the success metric. Collect and clean data. Split the data into training, validation and test sets. Pick a simple baseline first. Train, tune hyperparameters on the validation set, and evaluate once on the test set at the end. Deploy, then monitor, because data changes over time.
A typical split is 70 percent train, 15 percent validation, 15 percent test, but the right split depends on how much data you have.

## Data leakage
Data leakage means information from outside the training data, often from the test set or from the future, influences training, so the measured score is too optimistic. Common causes: scaling or imputing using statistics of the whole dataset before splitting, duplicates present in both train and test, and using a feature that would not be known at prediction time (for example, using the final outcome as a feature). The fix is to split first and fit every preprocessing step only on the training data, which scikit-learn pipelines make easy.

## Overfitting, underfitting and bias-variance
Underfitting: the model is too simple and performs badly on both training and validation data (high bias). Overfitting: the model memorises noise, so it scores very well on training data but poorly on new data (high variance).
Ways to reduce overfitting: more data, simpler model, regularisation (L1, L2, dropout), early stopping, data augmentation, cross-validation to detect it. Ways to reduce underfitting: more expressive model, better features, longer training, less regularisation.

## Classification metrics
Accuracy is the share of correct predictions and is misleading with imbalanced classes: a model that always predicts "no fraud" is 99 percent accurate when fraud is 1 percent of cases.
From the confusion matrix: precision is true positives divided by all predicted positives. Recall (also called sensitivity) is true positives divided by all actual positives. F1 is the harmonic mean of precision and recall. Choose by cost: for cancer screening favour recall (do not miss cases), for spam filters favour precision (do not block real mail).
ROC-AUC measures how well the model ranks positives above negatives across thresholds. For very imbalanced data, precision-recall curves are often more informative.
Regression metrics: MAE (mean absolute error), MSE and RMSE (penalise big errors more), and R squared.

## Cross-validation
In k-fold cross-validation the training data is split into k parts. The model is trained k times, each time using one part as validation and the rest for training, and the scores are averaged. It gives a more stable estimate than one split. Use stratified folds for classification so that class proportions stay the same.

## Gradient descent in plain words
Training means finding parameters that minimise a loss function. Gradient descent computes the slope (gradient) of the loss with respect to the parameters and moves the parameters a small step in the opposite direction. The step size is the learning rate. Too high and the loss jumps around or diverges. Too low and training is slow. Stochastic and mini-batch gradient descent use a small batch of examples per step, which is faster and adds helpful noise. Adam is a popular optimiser that adapts the step size per parameter.

## Neural network vocabulary
A neuron computes a weighted sum of inputs plus a bias and passes it through an activation function such as ReLU, sigmoid or tanh. Without non-linear activations a stack of layers collapses into one linear function. Backpropagation applies the chain rule to compute gradients for all layers efficiently. An epoch is one full pass over the training data. A batch is the group of examples used for one update.
Convolutional neural networks are strong on images because filters share weights across positions. Recurrent networks handled sequences before transformers. Transformers use attention, which lets every token look at every other token, and they train well in parallel.

## Tokens, embeddings and context windows
LLMs do not read characters or words directly. Text is split into tokens, which are pieces of words. English averages roughly 0.75 words per token, and Arabic often needs more tokens per word, so Arabic text uses up context faster.
An embedding is a vector of numbers that represents the meaning of a text. Texts with similar meaning have vectors that are close together, measured with cosine similarity. Multilingual embedding models place sentences with the same meaning in different languages near each other, which is why an Arabic question can retrieve an English passage.
The context window is the maximum number of tokens the model can consider at once, including the prompt, the retrieved passages and the answer.

## How an LLM generates text
The model outputs a probability for each possible next token, one token at a time. Temperature controls randomness: a low value gives more predictable output and a high value gives more varied output. Top-p sampling keeps only the smallest set of tokens whose probabilities add up to p. For factual question answering use a low temperature.

## Hallucination
A hallucination is a fluent answer that is not true or not supported by the source. It happens because the model predicts plausible text and has no built-in fact check. Ways to reduce it: ground the answer in retrieved documents, instruct the model to say when it does not know, ask for citations, lower the temperature, and verify important claims.

## RAG: retrieval-augmented generation
RAG gives an LLM relevant documents at question time. Steps: split documents into chunks, embed each chunk, store the vectors in a vector database, embed the user question, retrieve the nearest chunks, put them into the prompt, and ask the model to answer only from them.
Design choices that matter: chunk size (too small loses context, too large dilutes the match; 200 to 500 words is a common starting range), chunk overlap, keeping the heading with each chunk, how many chunks to retrieve (top-k), a similarity threshold below which the bot answers "I don't know", and metadata filters such as topic or language.
Hybrid search combines keyword search (BM25) with vector search and often beats either alone, especially for exact names, error codes and acronyms. A reranker is a second model that reorders the retrieved chunks by relevance and usually improves quality.
Typical failure modes: the right chunk was not retrieved (a retrieval problem, fix chunking or embeddings), the right chunk was retrieved but the model ignored it (a prompt or model problem), or the knowledge base simply lacks the answer (a coverage problem).

## RAG versus fine-tuning
RAG is best for adding facts that change or are private, and it can show sources. Fine-tuning is best for changing style, format or behaviour, or for teaching a narrow skill. It is a poor way to add knowledge that must stay up to date. Many systems use both.

## Prompt engineering basics
Be specific about the task, audience and output format. Give the role and rules in the system prompt. Provide one or two examples of the desired output (few-shot prompting). For reasoning tasks, ask the model to work step by step. Put the retrieved context clearly separated from the question. Tell the model what to do when the context is insufficient. Test prompts on a fixed set of questions instead of judging by one lucky answer.
Prompt injection is an attack where text inside a document or web page tries to give the model new instructions. Treat retrieved text as data, not as instructions, and do not give the model dangerous tools without checks.

## Evaluating a RAG chatbot
Build a test set of 30 to 100 questions with the expected answers and the expected source. Measure retrieval quality (was the right chunk in the top k, often called hit rate or recall at k) and answer quality (is it correct, complete and supported by the sources). Include questions that the knowledge base cannot answer, and check that the bot says so. Re-run the test set after every change to chunking, embeddings or prompts.

## Responsible AI
Models can reflect bias in their training data. Check performance across groups, not only overall. Do not feed private data to services you do not control. Be transparent that answers come from an AI, show sources, and let users report mistakes. For education, encourage students to verify and understand rather than copy.

## Python ML ecosystem map
NumPy for arrays. pandas for tables. matplotlib and seaborn for plots. scikit-learn for classic ML, pipelines and metrics. PyTorch and TensorFlow for deep learning. Hugging Face transformers for pretrained models. Jupyter notebooks for exploration. Ollama and llama.cpp run open models locally. ChromaDB, FAISS and pgvector store vectors.

<!-- id: transformers_and_training; topics: ai -->
# Neural Networks, Transformers and Training Explained in Depth

## From one neuron to a deep network
A single artificial neuron multiplies each input by a weight, adds the results together with a bias, and passes the sum through an activation function. A layer is many neurons that look at the same inputs. A deep network stacks layers so that each layer works with the features produced by the previous one: early layers detect simple patterns and later layers combine them into complex ones. In an image model the first layers react to edges, the middle layers to shapes and textures, and the last layers to whole objects.
The activation function is essential. If every layer were purely linear, a hundred layers would still be equivalent to one linear function, so the network could not learn curved decision boundaries. ReLU, which returns max(0, x), is the default choice in hidden layers because it is cheap and avoids saturating for positive values. Sigmoid squeezes values into 0 to 1 and is used for binary probabilities. Softmax turns a vector of scores into probabilities that add up to 1 and is used for multi-class outputs.
The number of learnable parameters grows quickly. A layer from 20 inputs to 64 outputs has 20 times 64 weights plus 64 biases, which is 1,344 parameters. Large language models have billions.

## What training really does
Training repeats four steps. The forward pass computes predictions from a batch of inputs. The loss function compares predictions with the true answers and produces one number that says how wrong the model is. The backward pass (backpropagation) uses the chain rule to compute the gradient, which says how the loss changes if each weight changes a little. The optimiser then moves every weight a small step in the direction that reduces the loss. One pass through the whole training set is an epoch.
For classification the standard loss is cross-entropy. A useful sanity check: before training, a model that guesses uniformly among C classes should have a loss near the natural log of C, so about 2.30 for 10 classes and about 1.10 for 3 classes. If your first loss is far from that value, there is probably a bug in the data pipeline or the loss setup.
Learning rate is the most important hyperparameter. If it is too high the loss oscillates or becomes NaN. If it is too low, learning is painfully slow. Common starting values are 1e-3 for Adam and 1e-2 to 1e-1 for plain SGD with momentum. Schedules that reduce the learning rate during training, and a short warm-up at the start, usually help.

## A minimal PyTorch training loop
```python
import torch
from torch import nn

model = nn.Sequential(nn.Linear(20, 64), nn.ReLU(), nn.Linear(64, 3))
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(10):
    model.train()
    for x, y in train_loader:
        optimizer.zero_grad()
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in val_loader:
            correct += (model(x).argmax(dim=1) == y).sum().item()
            total += y.numel()
    print(epoch, "val accuracy", correct / total)
```
Why each line exists: zero_grad clears old gradients, because PyTorch accumulates gradients by default. loss.backward computes the gradients, and optimizer.step updates the weights. model.train and model.eval switch layers such as dropout and batch normalisation between training and evaluation behaviour. torch.no_grad turns off gradient tracking during validation to save memory and time. CrossEntropyLoss expects raw scores (logits) and integer class labels, so do not add a softmax before it, which is a very common mistake.

## Debugging a network that does not learn
First try to overfit a single small batch of 10 to 20 examples. A healthy model and pipeline should reach almost zero loss on it within a few hundred steps. If it cannot, the problem is a bug, not a lack of data. Check that inputs and labels are aligned after shuffling, that data is normalised, that the loss matches the output layer, that the learning rate is sensible, and that you call zero_grad. Print the shapes of tensors at each step. Watch both training and validation loss: if training loss falls but validation loss rises, the model is overfitting, and you need regularisation, more data or a smaller model. If both stay high, the model is underfitting or the learning is broken.
Vanishing gradients happen when gradients shrink to almost zero as they pass back through many layers, so early layers stop learning. Remedies include ReLU-style activations, residual connections (used in ResNets and transformers), normalisation layers and careful weight initialisation. Exploding gradients are controlled by gradient clipping.

## Regularisation tools
Dropout randomly switches off a fraction of neurons during training so the network cannot rely on any single path. Weight decay (L2 regularisation) penalises large weights. Early stopping halts training when validation loss stops improving. Data augmentation creates modified copies of training examples, such as flipped or cropped images. Batch normalisation stabilises the distribution of layer inputs and usually allows higher learning rates. Layer normalisation does the same per example and is the standard in transformers.

## Convolutional and recurrent networks
A convolutional layer slides a small filter, for example 3 by 3, across an image. The same filter weights are reused at every position, so the layer needs far fewer parameters than a fully connected one and it detects a pattern wherever it appears. Pooling layers shrink the feature maps by summarising small regions. This is why convolutional networks were the standard for vision for a decade.
A recurrent network processes a sequence one step at a time and carries a hidden state forward as memory. Basic recurrent networks forget quickly because of vanishing gradients, and LSTM and GRU cells add gates that decide what to keep and what to forget. Recurrent models are slow to train because each step depends on the previous one, and that limitation is one of the reasons transformers replaced them for language.

## Attention: the core idea of transformers
When you read the sentence "The animal did not cross the street because it was too tired", you know that "it" refers to the animal. Attention lets a model do this kind of lookup. For every token the model computes three vectors by multiplying its embedding with learned matrices: a query (what am I looking for), a key (what do I contain) and a value (what information do I give). The score between two tokens is the dot product of the query of one with the key of the other. Scores are divided by the square root of the key dimension to keep them in a stable range, passed through softmax to become weights that sum to 1, and then used to take a weighted average of the value vectors.
The formula is softmax of (Q times K transposed divided by the square root of d_k), multiplied by V. The following code is a complete working version using NumPy.
```python
import numpy as np

def attention(Q, K, V):
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)
    scores = scores - scores.max(axis=-1, keepdims=True)
    weights = np.exp(scores)
    weights = weights / weights.sum(axis=-1, keepdims=True)
    return weights @ V, weights
```
Subtracting the maximum before the exponential does not change the result but prevents numerical overflow. Every row of the weights matrix sums to 1. Multi-head attention runs several attention computations in parallel with different learned projections, so different heads can specialise, for example one in grammar relations and another in nearby words, and then concatenates the results.

## The transformer block and why it works
A transformer block has multi-head self-attention followed by a small feed-forward network applied to each token, with residual connections and layer normalisation around each part. Residual connections add the input of a sublayer to its output, which helps gradients flow through deep stacks. Blocks are repeated dozens of times. Because attention does not know word order by itself, position information is added: the original transformer used sinusoidal position encodings, and many current models use rotary position embeddings (RoPE).
Transformers are efficient to train because all tokens of a sequence are processed in parallel, unlike recurrent networks. The price is that attention compares every token with every other token, so the cost grows with the square of the sequence length. That is why very long contexts are expensive in time and memory. During generation, models store the keys and values of previous tokens in a KV cache so they do not recompute them, and this cache is a major part of memory use at long context lengths.

## Encoder, decoder and the model families
Encoder-only models such as BERT read the whole text at once with attention in both directions and are trained by predicting masked words. They produce good representations and are used for classification, search and embeddings. Decoder-only models such as the GPT family and most chat models use a causal mask, so each token can attend only to earlier tokens, and they are trained to predict the next token. They generate text one token at a time. Encoder-decoder models such as T5 read the input with an encoder and generate the output with a decoder, and they suit translation and summarisation.

## How a chat model is built
Pretraining on a huge text collection teaches the model language and a lot of world knowledge by next-token prediction. Supervised fine-tuning on examples of instructions and good answers teaches it to follow instructions and to hold a conversation. Preference tuning, such as reinforcement learning from human feedback or direct preference optimisation, pushes the model toward answers people rate as helpful and safe. The model itself has no live access to the internet or your files. Anything it knows after training must be supplied in the prompt, which is exactly what retrieval-augmented generation does.

## Tokenization
Models read tokens, not letters. Byte-pair encoding starts from small units and repeatedly merges the most frequent pairs, so common words become single tokens and rare words are split into several pieces. Text in languages that were less represented in the training data, Arabic included in many tokenizers, is often split into more tokens per word. That means the same content consumes more of the context window and costs more time. Numbers, code and unusual spellings also split into many tokens, which is one reason models can make arithmetic and spelling mistakes.

## Embedding models and similarity search
An embedding model is trained so that texts with similar meaning get vectors that are close together, usually with a contrastive objective that pulls related pairs together and pushes unrelated ones apart. Similarity is measured with cosine similarity, which is the dot product of two vectors divided by the product of their lengths. Cosine distance is one minus the cosine similarity, so smaller distances mean more similar texts. When vectors are normalised to length 1, cosine similarity equals the dot product.
```python
import numpy as np

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```
For example, the vectors [1, 0] and [1, 1] have cosine similarity of about 0.707. Multilingual models such as BGE-M3 map more than 100 languages into one shared space and accept long inputs, so an Arabic question and an English paragraph that answers it can be close to each other. Always use the same embedding model for documents and for queries, and re-embed everything if you change the model. Some models expect a prefix such as "query:" or "passage:", so read the model card.

## Fine-tuning, LoRA and quantization
Fine-tuning all parameters of a large model needs a lot of GPU memory. LoRA (low-rank adaptation) freezes the original weights and trains small added matrices, which can be only a fraction of one percent of the parameters, and the result is a small adapter file that can be attached to the base model. Fine-tuning is good for style, format and specialised behaviour, and a poor way of adding facts that change, for which retrieval is better.
Quantization stores weights with fewer bits. A rough memory estimate for the weights is the number of parameters times the bytes per parameter. A 7 billion parameter model needs about 14 GB in 16-bit precision, about 7 GB in 8-bit and about 3.5 to 4 GB in 4-bit, plus extra memory for the KV cache and runtime overhead. That is why 4-bit versions of 7B and 8B models run on ordinary laptops. Quantization lowers quality slightly, usually little at 8-bit and more noticeably below 4-bit.

## Running models locally with Ollama
Ollama runs open models on your own machine and exposes a local HTTP API on port 11434. Typical commands are ollama pull model to download, ollama run model to chat in the terminal, ollama list to see installed models and ollama serve to start the server if it is not already running. The API endpoint /api/chat takes a list of messages and /api/embed returns embeddings for one or more input texts. The default context length is modest, so for retrieval-augmented generation raise num_ctx in the request options when you send several long passages, otherwise the beginning of the prompt can be silently cut off. Smaller models answer faster but follow instructions and handle Arabic less reliably, so test with your own questions. If answers are slow, check whether the model fits in GPU memory, because spilling to the CPU makes generation much slower.

## Sampling settings in practice
Temperature rescales the probabilities before sampling. Near 0 the model almost always picks the most likely token, which is best for factual answers and code. Around 0.7 gives more varied, creative text. Top-p keeps only the most probable tokens whose combined probability reaches p, and top-k keeps only the k most probable. Repetition penalties reduce loops. For a question-answering assistant grounded in documents, use a low temperature such as 0.1 to 0.3.

## Reading papers and learning path
A practical order for learning: Python and NumPy, then pandas and basic statistics, then scikit-learn for classic models and evaluation, then a neural network from scratch on a tiny dataset, then PyTorch, then transformers with the Hugging Face library, then retrieval and building an application around a model. For each concept, implement the smallest possible version yourself, since writing attention or a training loop once by hand makes the library versions understandable.

<!-- id: glossary_ar; topics: programming,ai,networking,databases,web_security,dev_tools -->
# قاموس المصطلحات التقنية عربي - إنجليزي مع شرح مبسط

## البرمجة
المتغير (variable): اسم يشير إلى قيمة مخزنة بالذاكرة، ويمكن تغيير قيمته أثناء تشغيل البرنامج.
نوع البيانات (data type): تصنيف القيمة مثل عدد صحيح (integer) أو عدد عشري (float) أو نص (string) أو قيمة منطقية (boolean).
الدالة (function): كتلة من الكود لها اسم، تأخذ مدخلات (parameters) وقد تُرجع نتيجة (return value)، وتُستخدم لتجنب تكرار الكود.
الحلقة التكرارية (loop): تكرار تنفيذ مجموعة أوامر، مثل for و while.
الجملة الشرطية (conditional): تنفيذ كود حسب شرط، مثل if و else.
القائمة (list): مجموعة مرتبة وقابلة للتعديل من العناصر. الصف (tuple): مجموعة مرتبة غير قابلة للتعديل. القاموس (dictionary): أزواج مفتاح وقيمة. المجموعة (set): عناصر فريدة بدون ترتيب.
الاستدعاء الذاتي (recursion): أن تستدعي الدالة نفسها، ويجب أن تحتوي على حالة أساسية (base case) توقف التكرار وإلا حدث تجاوز للمكدس (stack overflow).
الكائن (object) والصنف (class): الصنف هو القالب، والكائن هو نسخة منه تحمل بيانات وسلوك.
الوراثة (inheritance): أن يأخذ صنف خصائص صنف آخر. تعدد الأشكال (polymorphism): نفس اسم الدالة بسلوك مختلف حسب الكائن. التغليف (encapsulation): إخفاء التفاصيل الداخلية.
الخوارزمية (algorithm): خطوات محددة لحل مشكلة. التعقيد الزمني (time complexity): كيف يزداد وقت التنفيذ مع زيادة حجم المدخلات.
هيكل البيانات (data structure): طريقة لتنظيم البيانات مثل المصفوفة (array) والقائمة المترابطة (linked list) والمكدس (stack) والطابور (queue) والشجرة (tree) والرسم البياني (graph) وجدول التجزئة (hash table).
المُصحِّح (debugger): أداة تتيح إيقاف البرنامج وفحص قيم المتغيرات. تصحيح الأخطاء (debugging): البحث عن الأخطاء وإصلاحها.
المفسِّر (interpreter): ينفذ الكود سطراً سطراً مثل بايثون. المُترجِم (compiler): يحوّل الكود كله إلى لغة الآلة قبل التشغيل مثل لغة C.
الواجهة البرمجية (API): طريقة تسمح لبرنامج بالتحدث مع برنامج آخر. المكتبة (library): كود جاهز تستخدمه. الإطار (framework): هيكل جاهز يفرض طريقة معينة لبناء التطبيق.
البيئة الافتراضية (virtual environment): مساحة معزولة لحزم مشروع واحد. الاعتماديات (dependencies): الحزم التي يحتاجها مشروعك.

## الذكاء الاصطناعي
التعلم الآلي (machine learning): أن يتعلم النظام الأنماط من البيانات بدل كتابة القواعد يدوياً. التعلم العميق (deep learning): تعلم آلي بشبكات عصبية متعددة الطبقات.
التعلم الموجَّه (supervised learning): التدريب على بيانات لها إجابات صحيحة (labels). التعلم غير الموجَّه (unsupervised learning): إيجاد أنماط بدون إجابات، مثل التجميع (clustering). التعلم المعزَّز (reinforcement learning): التعلم بالمكافأة والعقوبة.
الشبكة العصبية (neural network): نموذج من طبقات من العُقَد (neurons) المرتبطة بأوزان (weights).
مجموعة التدريب (training set) والتحقق (validation set) والاختبار (test set): ثلاث أجزاء من البيانات؛ التدريب لتعليم النموذج، التحقق لضبط الإعدادات، الاختبار لتقييم نهائي واحد.
فرط التخصيص (overfitting): النموذج يحفظ بيانات التدريب ويفشل مع بيانات جديدة. نقص التخصيص (underfitting): النموذج بسيط جداً فيفشل مع الجميع.
دالة الخسارة (loss function): تقيس مقدار خطأ النموذج. النزول التدريجي (gradient descent): طريقة لتقليل الخسارة بتحريك الأوزان بعكس الميل. معدل التعلم (learning rate): حجم الخطوة.
الدقة (accuracy)، الاستدعاء (recall)، الضبط أو الدقة الموجبة (precision)، مقياس F1: مقاييس لتقييم التصنيف.
النموذج اللغوي الكبير (LLM): نموذج يتنبأ بالكلمة التالية بعد تدريبه على نصوص ضخمة. الرمز (token): قطعة نص يقرأها النموذج. نافذة السياق (context window): أقصى عدد رموز يستوعبها النموذج مرة واحدة.
التضمين (embedding): تحويل نص إلى متجه أرقام يمثل معناه، والنصوص المتشابهة المعنى تكون متجهاتها قريبة. قاعدة بيانات المتجهات (vector database): تخزن المتجهات وتبحث عن الأقرب.
التوليد المعزَّز بالاسترجاع (RAG): جلب مقاطع من قاعدة معرفة وإعطاؤها للنموذج ليجيب منها. التقطيع (chunking): تقسيم المستندات إلى قطع صغيرة. الهلوسة (hallucination): إجابة تبدو مقنعة لكنها غير صحيحة. الضبط الدقيق (fine-tuning): إكمال تدريب النموذج على بيانات خاصة. هندسة الأوامر (prompt engineering): صياغة التعليمات للنموذج بشكل فعّال.

## الشبكات
عنوان IP: رقم يعرّف الجهاز على الشبكة. قناع الشبكة الفرعية (subnet mask): يحدد جزء الشبكة وجزء الجهاز من العنوان. البوابة الافتراضية (default gateway): الجهاز الذي يوصلك لشبكات أخرى.
المُوجِّه (router): يوجه الحزم بين الشبكات حسب جدول التوجيه. المحوِّل (switch): يوصل الأجهزة داخل شبكة محلية باستخدام عناوين MAC. جدار الحماية (firewall): يسمح أو يمنع حركة المرور حسب قواعد.
عنوان MAC: عنوان فيزيائي فريد لبطاقة الشبكة. المنفذ (port): رقم يحدد الخدمة على الجهاز مثل 80 للـ HTTP و443 للـ HTTPS.
بروتوكول (protocol): مجموعة قواعد للتواصل. TCP: بروتوكول موثوق يضمن وصول البيانات بالترتيب بعد مصافحة ثلاثية (three-way handshake). UDP: بروتوكول سريع بدون ضمان وصول.
نظام أسماء النطاقات (DNS): يحوّل اسم الموقع إلى عنوان IP. بروتوكول DHCP: يعطي الأجهزة عناوينها تلقائياً. ترجمة عناوين الشبكة (NAT): تسمح لعدة أجهزة بمشاركة عنوان عام واحد.
زمن الاستجابة (latency): الوقت الذي تستغرقه الحزمة للذهاب والعودة. عرض النطاق (bandwidth): أقصى سعة نقل. فقدان الحزم (packet loss): حزم لا تصل.
الشبكة الافتراضية الخاصة (VPN): نفق مشفّر بين جهازك وشبكة أخرى. الشبكة المحلية (LAN) والواسعة (WAN).

## قواعد البيانات والأمان وأدوات التطوير
قاعدة البيانات (database): تخزين منظم للبيانات. الجدول (table)، الصف (row)، العمود (column). المفتاح الأساسي (primary key): يحدد كل صف بشكل فريد. المفتاح الأجنبي (foreign key): يشير إلى مفتاح أساسي في جدول آخر.
الاستعلام (query): طلب بيانات، ولغة SQL هي لغة الاستعلام. الربط (join): دمج جداول. الفهرس (index): بنية تسرّع البحث. المعاملة (transaction): مجموعة عمليات تنجح كلها أو تفشل كلها. التسوية أو التطبيع (normalization): تقليل التكرار في تصميم الجداول.
المصادقة (authentication): إثبات هوية المستخدم. التفويض (authorization): تحديد ما يُسمح له بفعله. التشفير (encryption): إخفاء البيانات بمفتاح ويمكن عكسه. التجزئة (hashing): تحويل باتجاه واحد لا يمكن عكسه، وتُستخدم لتخزين كلمات المرور مع ملح (salt).
حقن SQL (SQL injection): إدخال أوامر خبيثة عبر مدخلات المستخدم، وعلاجه الاستعلامات المُعاملة (parameterized queries). البرمجة عبر المواقع (XSS): تشغيل سكربت خبيث في متصفح مستخدم آخر. الثغرة (vulnerability): نقطة ضعف يمكن استغلالها.
التحكم بالإصدارات (version control) وGit: تتبع تغييرات الكود. المستودع (repository): مجلد المشروع مع تاريخه. الإيداع (commit): لقطة محفوظة من التغييرات. الفرع (branch): خط تطوير مستقل. الدمج (merge): جمع فرعين. طلب السحب (pull request): طلب مراجعة ودمج تغييراتك. التعارض (conflict): تعديل نفس السطر بطريقتين مختلفتين ويحتاج حلاً يدوياً.
الحاوية (container) والصورة (image) في Docker: الصورة قالب للقراءة فقط، والحاوية نسخة تعمل منه. التكامل المستمر (CI): تشغيل الاختبارات تلقائياً مع كل تغيير.

## نصائح لشرح المصطلحات بالعربي
عند الكتابة بالعربي يُفضَّل ذكر المصطلح الإنجليزي بين قوسين عند أول ظهور، لأن المصطلحات الإنجليزية هي التي ستجدها في التوثيق ورسائل الأخطاء والبحث على الإنترنت. كود البرمجة والأوامر وأسماء الملفات تبقى بالإنجليزية دائماً.

<!-- id: arabic_explainers; topics: programming,ai,networking,databases,web_security,dev_tools -->
# شروحات مفصلة بالعربي لأهم المفاهيم التقنية

## ما الفرق بين TCP و UDP؟
بروتوكول TCP يشبه مكالمة هاتفية: تبدأ باتصال يتأكد فيه الطرفان أنهما جاهزان، ثم يتبادلان الكلام بالترتيب، وإذا ضاعت جملة يطلب المستمع إعادتها. تقنياً يبدأ الاتصال بمصافحة ثلاثية (three-way handshake): يرسل العميل SYN، فيرد الخادم بـ SYN-ACK، ثم يرسل العميل ACK. بعد ذلك تُرقَّم البيانات، ويؤكد المستلم وصول كل جزء، وتُعاد الأجزاء المفقودة، ويتحكم البروتوكول بسرعة الإرسال حتى لا يغرق الشبكة. النتيجة تدفق بيانات موثوق ومرتب، لكن بثمن هو التأخير الإضافي.
بروتوكول UDP يشبه إرسال بطاقات بريدية: ترسل كل رسالة (datagram) باستقلال، ولا يوجد اتصال مسبق ولا تأكيد استلام ولا إعادة إرسال ولا ضمان للترتيب. ميزته السرعة وقلة التأخير، فهو مناسب عندما يكون التأخير أسوأ من فقدان جزء بسيط من البيانات، مثل المكالمات الصوتية والمرئية والألعاب الإلكترونية، وكذلك استعلامات DNS الصغيرة. أما تصفح المواقع ونقل الملفات والبريد الإلكتروني فتستخدم TCP لأن ضياع جزء من الملف يفسده.
القاعدة العملية: إذا كان وصول كل بايت بالترتيب ضرورياً فاستخدم TCP، وإذا كانت الحداثة أهم من الكمال أو كان التطبيق يتعامل مع الموثوقية بنفسه فاستخدم UDP.

## ماذا يحدث عندما أكتب عنوان موقع في المتصفح وأضغط Enter؟
الخطوات بالترتيب. أولاً يبحث المتصفح عن عنوان IP للاسم، فيسأل أولاً الذاكرة المؤقتة (cache) ثم نظام التشغيل ثم خادم DNS المعتمد عندك (الـ recursive resolver)، وهذا الأخير يسأل عند الحاجة الخوادم الجذرية ثم خوادم النطاق العلوي مثل com ثم الخادم المسؤول عن نطاق الموقع. ثانياً ينشئ المتصفح اتصال TCP مع عنوان IP على المنفذ 443 بمصافحة ثلاثية. ثالثاً تتم مصافحة TLS: يرسل الخادم شهادته، ويتحقق المتصفح أنها موقعة من جهة موثوقة وأنها تخص النطاق، ثم يتفق الطرفان على مفاتيح تشفير الجلسة. رابعاً يرسل المتصفح طلب HTTP مثل GET على المسار المطلوب. خامساً يعالج الخادم الطلب ويرد برمز حالة مثل 200 ومحتوى الصفحة. سادساً يحلل المتصفح HTML ويطلب بقية الموارد كملفات CSS وJavaScript والصور، ثم يرسم الصفحة.
إذا فشل المتصفح عند خطوة معينة تعرف أين المشكلة: خطأ في الاسم يعني DNS، وانتهاء المهلة يعني مشكلة وصول أو جدار حماية، وتحذير الشهادة يعني مشكلة TLS، ورمز 404 أو 500 يعني أن الشبكة سليمة لكن التطبيق عنده مشكلة.

## كيف أحسب الشبكات الفرعية (subnetting) خطوة بخطوة؟
لنفترض العنوان 192.168.10.77/26. الرقم 26 يعني أن أول 26 بتاً تمثل الشبكة، وما تبقى هو 6 بتات للأجهزة، أي 2 أس 6 يساوي 64 عنواناً في كل شبكة فرعية. القناع بصيغة النقاط هو 255.255.255.192 لأن آخر ثماني بتات تحتوي بتين للشبكة، وقيمتهما 128 + 64 = 192.
حجم الكتلة (block size) هو 256 ناقص 192 يساوي 64، فالشبكات الفرعية تبدأ عند 0 و64 و128 و192. العنوان ينتهي بـ 77 فهو يقع في الكتلة التي تبدأ عند 64. إذن عنوان الشبكة 192.168.10.64، وعنوان البث (broadcast) هو آخر عنوان في الكتلة 192.168.10.127، والأجهزة المتاحة من 192.168.10.65 إلى 192.168.10.126، أي 62 جهازاً. عدد الأجهزة المتاحة دائماً هو عدد العناوين ناقص 2.
للتدرب: كم شبكة فرعية من نوع /27 تتسع داخل شبكة /24؟ كل /27 يضيف 3 بتات، فالعدد 2 أس 3 يساوي 8 شبكات، وفي كل واحدة 32 عنواناً منها 30 صالحة للأجهزة.

## ما هي الدالة الذاتية الاستدعاء (recursion) وكيف أفهمها؟
الاستدعاء الذاتي أن تحل مسألة كبيرة باستدعاء نفس الدالة على نسخة أصغر من المسألة. تخيل أنك تقف في طابور طويل وتريد معرفة ترتيبك. تسأل الشخص الذي أمامك: ما ترتيبك؟ فهو يسأل من أمامه، وهكذا حتى يصل السؤال إلى أول شخص في الطابور فيجيب 1. كل شخص بعده يضيف 1 إلى الجواب الذي سمعه ويمرره للخلف. السؤال يمشي للأمام ثم الأجوبة ترجع للخلف.
في الكود لا بد من شيئين. الأول الحالة الأساسية (base case) وهي الشخص الأول الذي يجيب مباشرة بلا سؤال، وبدونها تستمر الاستدعاءات بلا نهاية فيحدث RecursionError. الثاني الخطوة التراجعية التي تقرّب المسألة من الحالة الأساسية، مثل n ناقص 1. المثال المعروف هو العاملي: factorial(5) تساوي 5 ضرب factorial(4)، وهكذا حتى factorial(1) تعطي 1، ثم تتضاعف النتائج عند العودة فتصبح 120.
متى نستخدمها؟ عندما تكون المسألة نفسها متداخلة مثل المجلدات داخل مجلدات والأشجار والبحث بالتجربة والتراجع. وإذا لاحظت أن الدالة تعيد حساب نفس القيم كثيراً، كما في فيبوناتشي، فاحفظ النتائج (memoization) باستخدام lru_cache فيتحول الزمن من أُسّي إلى خطي.

## ما هو Big-O ولماذا يهمني؟
Big-O طريقة لوصف كيف يزداد زمن تشغيل الخوارزمية (أو الذاكرة التي تستهلكها) عندما يكبر حجم المدخلات، دون الاهتمام بسرعة جهاز بعينه. إذا كان الزمن O(n) فمضاعفة البيانات تضاعف الزمن. وإذا كان O(n²) فمضاعفة البيانات تجعل الزمن أربعة أضعاف. وإذا كان O(log n) فمضاعفة البيانات تضيف خطوة واحدة فقط، ولذلك البحث الثنائي في مليون عنصر يحتاج نحو 20 خطوة.
أمثلة: الوصول لعنصر بالفهرس O(1)، والبحث في قائمة غير مرتبة O(n)، والبحث الثنائي O(log n)، والترتيب الجيد O(n log n)، وحلقتان متداخلتان على نفس البيانات O(n²). في بايثون البحث عن عنصر داخل list بطيء O(n) أما داخل set أو dict فمتوسطه O(1)، وهذا من أسهل أساليب تسريع الكود.
لا تحسّن قبل أن تقيس. للبيانات الصغيرة قد لا تهم هذه الفروق، لكنها تصبح حاسمة عندما تكبر البيانات إلى ملايين العناصر.

## ما هو فرط التخصيص (overfitting) وكيف أكتشفه وأعالجه؟
تخيل طالباً حفظ أسئلة امتحانات السنوات الماضية بأجوبتها حرفياً دون فهم. سيحصل على علامة ممتازة إن تكررت الأسئلة نفسها، لكنه سيفشل عند أي سؤال جديد. هذا هو فرط التخصيص: النموذج يحفظ بيانات التدريب بما فيها الضجيج بدل أن يتعلم النمط العام.
العلامة الأوضح أن الخطأ على بيانات التدريب ينخفض باستمرار بينما الخطأ على بيانات التحقق (validation) يتوقف عن الانخفاض ثم يبدأ بالارتفاع. لذلك نقسم البيانات دائماً إلى تدريب وتحقق واختبار، ولا نحكم على النموذج بأدائه على بيانات رآها أثناء التدريب.
العلاج يكون بإحدى الطرق التالية أو بجمعها: جمع بيانات أكثر، أو استخدام نموذج أبسط، أو التنظيم (regularization) مثل L2 والـ dropout، أو الإيقاف المبكر (early stopping)، أو زيادة البيانات (data augmentation)، أو استخدام التحقق المتقاطع (cross-validation) لتقدير الأداء بثبات أكبر. والعكس هو نقص التخصيص (underfitting) حيث يكون الأداء ضعيفاً على التدريب والتحقق معاً، وعلاجه نموذج أقوى أو ميزات أفضل أو تدريب أطول.

## كيف يعمل RAG خطوة بخطوة؟
النموذج اللغوي لا يعرف مستنداتك الخاصة ولا أحدث المعلومات، وقد يخترع إجابة تبدو مقنعة (هلوسة). فكرة RAG أن نعطيه الصفحات المناسبة وقت السؤال، مثل طالب يُسمح له بفتح الكتاب في الامتحان.
مرحلة التحضير تتم مرة واحدة: نقسم المستندات إلى قطع صغيرة (chunks) من 200 إلى 500 كلمة تقريباً، ونحوّل كل قطعة إلى متجه أرقام (embedding) يمثل معناها، ونخزن المتجهات في قاعدة بيانات متجهات. مرحلة السؤال تتم في كل مرة: نحوّل سؤال المستخدم إلى متجه بنفس النموذج، ونبحث عن أقرب القطع إليه، ونضع هذه القطع في الأمر (prompt) مع تعليمة واضحة بأن يجيب النموذج من النص المرفق فقط وأن يقول لا أعرف إذا لم يجد الجواب، ثم نعرض الجواب مع المصادر.
عند وجود مشكلة اسأل أين حدث الخلل. إذا لم تظهر القطعة الصحيحة بين النتائج فالمشكلة في التقطيع أو في نموذج التضمين أو أن المعلومة غير موجودة. وإذا ظهرت القطعة لكن الجواب خاطئ فالمشكلة في الأمر أو في النموذج. استخدم مجموعة أسئلة اختبار ثابتة وأعد تشغيلها بعد كل تعديل.

## ما هي التضمينات (embeddings)؟
التضمين قائمة طويلة من الأرقام، مثل 1024 رقماً، تمثل معنى نص ما. يُدرَّب النموذج بحيث تكون الجمل المتقاربة في المعنى قريبة من بعضها في هذا الفضاء الرياضي، حتى لو اختلفت كلماتها. فجملة "كيف أعيد ضبط كلمة المرور" تكون قريبة من "نسيت كلمة السر" رغم أن الكلمات مختلفة، وهذا ما يجعل البحث بالمعنى أقوى من البحث بالكلمات المفتاحية فقط.
نقيس القرب عادة بالتشابه الجيبي التمامي (cosine similarity)، وهو يقيس الزاوية بين متجهين. القيمة 1 تعني نفس الاتجاه (معنى متطابق)، والقيمة قرب 0 تعني عدم وجود علاقة. وتسمى المسافة الجيبية التمامية (cosine distance) وهي 1 ناقص التشابه، فكلما صغرت المسافة زاد التشابه. والنماذج متعددة اللغات مثل BGE-M3 تضع الجمل المتشابهة في المعنى قريبة من بعضها حتى لو كانت بلغات مختلفة، ولذلك يمكن لسؤال بالعربي أن يجد فقرة إنجليزية تجيب عنه. يجب استخدام نفس النموذج للمستندات والأسئلة.

## ما الفرق بين التشفير (encryption) والتجزئة (hashing)؟
التشفير يخفي البيانات بمفتاح ويمكن استرجاعها بمفتاح مناسب، مثل صندوق مقفل: من يملك المفتاح يفتحه. نستخدمه عندما نحتاج إلى قراءة البيانات لاحقاً، كرسائل المحادثة واتصالات HTTPS. أما التجزئة فهي تحويل باتجاه واحد: تعطي أي بيانات فتخرج بصمة ثابتة الطول، ولا يمكن استرجاع الأصل منها. وأي تغيير صغير في المدخلات يغير البصمة كلياً. نستخدمها للتحقق من سلامة الملفات ولتخزين كلمات المرور، فلا نخزن كلمة المرور نفسها بل بصمتها، وعند تسجيل الدخول نحسب بصمة ما أُدخل ونقارنها.
لتخزين كلمات المرور لا تستخدم دوال سريعة مثل MD5 أو SHA-256 المجردة لأن المهاجم يجرب مليارات الاحتمالات بالثانية. استخدم دوال بطيئة مصممة لذلك مثل Argon2 أو bcrypt أو scrypt، مع ملح (salt) عشوائي فريد لكل مستخدم حتى لا تتشابه بصمات كلمات المرور المتشابهة.

## ما هو حقن SQL وكيف أحمي تطبيقي منه؟
يحدث الحقن عندما تبني استعلام SQL بدمج نص المستخدم مباشرة بنص الاستعلام. لو كتب المستخدم في حقل الاسم قيمة مثل ' OR '1'='1 فسيتحول الشرط إلى شرط صحيح دائماً ويعيد كل الصفوف، وقد ينفذ المهاجم أوامر أخطر بحسب صلاحيات حساب قاعدة البيانات.
الحل الأساسي هو الاستعلامات المُعاملة (parameterized queries): تكتب الاستعلام بعلامات مكان مثل علامة الاستفهام وترسل القيم منفصلة، فيعاملها المحرك كبيانات فقط وليس كأوامر. في بايثون: con.execute("SELECT * FROM users WHERE name = ?", (name,)). وتستخدم مكتبات ORM هذا الأسلوب تلقائياً في أغلب الحالات. كذلك أعطِ حساب التطبيق أقل صلاحيات ممكنة، وتحقق من المدخلات في الخادم، ولا تعرض رسائل أخطاء قاعدة البيانات للمستخدم.

## كيف أفهم JOIN في SQL؟
تخيل جدولين: جدول الطلاب وجدول التسجيلات. الربط (JOIN) يطابق الصفوف بحسب عمود مشترك، عادة المفتاح الأساسي في جدول والمفتاح الأجنبي في الآخر. الـ INNER JOIN يعيد فقط الصفوف التي لها مقابل في الجدولين، فالطالب غير المسجل في أي مادة لا يظهر. الـ LEFT JOIN يعيد كل صفوف الجدول الأيسر حتى لو لم يوجد لها مقابل، ويملأ أعمدة الجدول الأيمن بـ NULL، ولذلك نستخدمه للبحث عن الغائب مثل الطلاب الذين لم يسجلوا شيئاً: نضيف الشرط WHERE e.student_id IS NULL.
أخطاء شائعة: نسيان شرط الربط ON فينتج ضرب ديكارتي بحجم ضخم، واستخدام COUNT(*) بعد LEFT JOIN فيحسب الصف الفارغ كصف، والصحيح COUNT(عمود من الجدول الأيمن)، ومقارنة NULL بعلامة المساواة بدل IS NULL.

## كيف يعمل Git وما الفرق بين merge و rebase؟
Git يحفظ تاريخ مشروعك كسلسلة لقطات (commits)، كل واحدة تحتوي رسالة ومؤلفاً ومؤشراً لما قبلها. الفرع (branch) مجرد مؤشر متحرك إلى آخر لقطة في خط تطوير. الخطوات اليومية: تعدّل الملفات، ثم git add لوضعها في منطقة التجهيز (staging)، ثم git commit لحفظ اللقطة، ثم git push لإرسالها إلى المستودع البعيد، وgit pull لجلب تغييرات الآخرين.
عند الحاجة لدمج عمل فرعين: الدمج (merge) يجمع الفرعين بلقطة دمج جديدة ويحفظ التاريخ الحقيقي كما حدث. أما rebase فيعيد تشغيل لقطاتك فوق آخر نقطة من الفرع الآخر لينتج تاريخ خطي أنظف، لكنه يعيد كتابة اللقطات ويغير معرّفاتها. لذلك القاعدة الذهبية: لا تعمل rebase للقطات نشرها غيرك. وعند حدوث تعارض (conflict) يضع Git علامات <<<<<<< و======= و>>>>>>> حول الجزأين المتعارضين، فتحرر الملف وتختار الصيغة النهائية وتحذف العلامات ثم git add ثم تكمل. وإذا ارتكبت خطأ كبيراً فجرّب git reflog، فهو يعرض أين كان HEAD سابقاً وغالباً يمكنك العودة منه.

## ما الفرق بين الصورة (image) والحاوية (container) في Docker؟
الصورة قالب للقراءة فقط يحتوي على نظام ملفات صغير وبرنامجك ومكتباته وإعداداته، وتُبنى من ملف Dockerfile. الحاوية نسخة تعمل من هذه الصورة. العلاقة تشبه الفرق بين الصنف (class) والكائن (object) في البرمجة: من صورة واحدة يمكن تشغيل عدة حاويات. الحاوية تعزل برنامجها عن بقية الجهاز، وتضمن أن البرنامج يعمل بنفس الطريقة على جهازك وجهاز زميلك والخادم.
نقطتان يخطئ فيهما المبتدئون. الأولى أن بيانات الحاوية تضيع عند حذفها ما لم تربط مجلداً خارجياً (volume) بالخيار -v. الثانية ترتيب المنافذ في -p 8000:80 فهو دائماً المنفذ على جهازك أولاً ثم المنفذ داخل الحاوية.

## ما هي واجهة API ومعنى REST؟
الواجهة البرمجية (API) عقد يوضح كيف يطلب برنامج خدمة من برنامج آخر دون معرفة تفاصيله الداخلية. مثل قائمة الطعام في مطعم: تطلب من القائمة دون أن تدخل المطبخ. في واجهات REST تُمثَّل الأشياء كموارد لها عناوين، مثل /students/7، وتُحدد العملية بطريقة HTTP: GET للقراءة، وPOST للإنشاء، وPUT للاستبدال، وPATCH للتعديل الجزئي، وDELETE للحذف. وترجع الاستجابة عادة بصيغة JSON مع رمز حالة: 200 نجاح، 201 تم الإنشاء، 400 طلب خاطئ، 401 غير مسجل الدخول، 403 ممنوع، 404 غير موجود، 422 فشل التحقق من المدخلات، 500 خطأ في الخادم.
في FastAPI تكتب دالة بايثون لكل مسار وتحدد أنواع المدخلات، فيتحقق الإطار منها تلقائياً ويولد وثائق تفاعلية على المسار /docs.

## كيف أتعامل مع الأخطاء البرمجية بذكاء؟
اقرأ رسالة الخطأ من آخر سطر للأعلى: آخر سطر يوضح نوع الخطأ وسببه، والسطور فوقه تبين تسلسل الاستدعاءات، وأقرب سطر فيها من كودك هو أول مكان تبحث فيه. انسخ نص الخطأ كما هو إلى محرك البحث لأن الإجابة غالباً موجودة. ثم صغّر المشكلة إلى أقل مثال يعيد الخطأ، وغيّر شيئاً واحداً في كل مرة، وتحقق من افتراضاتك بطباعة القيم أو باستخدام المُصحِّح. اكتب اختباراً يفشل بسبب الخطأ قبل إصلاحه حتى لا يعود لاحقاً. وعندما تسأل غيرك أو أداة ذكاء اصطناعي، أرفق الكود المختصر ورسالة الخطأ الكاملة وما جربته، فجودة السؤال تحدد جودة الجواب.

<!-- id: learning_resources; topics: programming,ai,networking,databases,web_security,dev_tools -->
# Recommended Books, Courses and Learning Resources

## How to use this list
These are well-known resources chosen by one author from general knowledge, not an official ranking. Editions, prices and availability change, so check the latest edition and the author's website before buying. Resources marked free are legally available to read online at the time of writing. Match the book to your level: beginners should start with practical books and courses, and move to the mathematical books after they have built a few projects.

## Machine learning and deep learning books
Hands-On Machine Learning with Scikit-Learn, Keras and TensorFlow by Aurélien Géron is the most popular practical book for beginners and intermediate learners. It combines short explanations with code in Python, and it is a good first book after you know basic Python.
An Introduction to Statistical Learning (known as ISLR, with a Python edition called ISLP) by James, Witten, Hastie and Tibshirani is a gentle and clear introduction to the statistics behind machine learning. The authors make the PDF free to read online. The Elements of Statistical Learning by Hastie, Tibshirani and Friedman is its more mathematical big sibling, also free as a PDF.
Pattern Recognition and Machine Learning by Christopher Bishop is a classic textbook with a probabilistic point of view and demanding mathematics, and it suits readers who are comfortable with linear algebra and probability. Machine Learning: A Probabilistic Perspective by Kevin Murphy is another comprehensive classic. Murphy later wrote Probabilistic Machine Learning: An Introduction and an Advanced Topics volume, and drafts of these are available free from the author's site.
Deep Learning by Goodfellow, Bengio and Courville is the standard deep learning textbook and can be read free online at deeplearningbook.org. Dive into Deep Learning (d2l.ai) by Zhang, Lipton, Li and Smola is a free interactive book where every concept comes with runnable code in PyTorch and other frameworks.
Machine Learning with PyTorch and Scikit-Learn by Sebastian Raschka covers classic machine learning and deep learning with code. Build a Large Language Model From Scratch by Sebastian Raschka walks through building a small GPT-style model step by step. Deep Learning with Python by François Chollet is a clear introduction written by the creator of Keras. Natural Language Processing with Transformers by Tunstall, von Werra and Wolf explains the Hugging Face ecosystem. Speech and Language Processing by Jurafsky and Martin is the standard natural language processing textbook, and a draft of the latest edition is free online. Designing Machine Learning Systems by Chip Huyen explains how to take models into production.

## Machine learning courses
Andrew Ng's Machine Learning Specialization on Coursera (from DeepLearning.AI and Stanford) is the most popular first course. Practical Deep Learning for Coders by fast.ai is free and teaches by building real projects first and explaining theory later. Andrej Karpathy's video series Neural Networks: Zero to Hero builds a neural network and a GPT model from scratch. Stanford lectures such as CS229 (machine learning), CS231n (computer vision) and CS224n (natural language processing) are available on YouTube with notes. Kaggle offers free short courses and competitions that give hands-on practice with real datasets.

## Programming and algorithms
Automate the Boring Stuff with Python by Al Sweigart is free to read online and is a very good first Python book. Python Crash Course by Eric Matthes teaches Python through three projects. Fluent Python by Luciano Ramalho is the book to read after the basics, for writing idiomatic Python. Introduction to Algorithms by Cormen, Leiserson, Rivest and Stein (CLRS) is the standard algorithms textbook, and The Algorithm Design Manual by Steven Skiena is a more approachable alternative. Structure and Interpretation of Computer Programs (SICP) is a classic about the ideas of programming, free online. Harvard's CS50 is a free introductory computer science course with excellent lectures. Clean Code by Robert Martin and The Pragmatic Programmer by Hunt and Thomas teach professional habits. The Missing Semester of Your CS Education from MIT is a free course on the shell, Git, debugging and other tools that classes often skip.

## Networking
Computer Networking: A Top-Down Approach by Kurose and Ross is the most widely used university textbook. Computer Networks by Tanenbaum and Wetherall is another standard. TCP/IP Illustrated by W. Richard Stevens is the classic deep look at protocols. For practical certification-style learning, the Cisco Networking Academy courses and the CCNA Official Cert Guide are popular, and Wireshark is the tool to practise reading real packets. The Cloudflare Learning Center has short free explanations of DNS, TLS, DDoS and more.

## Databases
Database System Concepts by Silberschatz, Korth and Sudarshan is a standard university textbook. Designing Data-Intensive Applications by Martin Kleppmann is highly recommended for understanding how modern data systems work. Learning SQL by Alan Beaulieu is a good beginner book. Use The Index, Luke is a free website about SQL performance and indexes. SQLBolt and similar interactive sites let you practise queries in the browser.

## Security
Security Engineering by Ross Anderson is a broad classic and the author makes it available free online. The Web Application Hacker's Handbook by Stuttard and Pinto is a well-known book on web vulnerabilities, although parts of it are dated. The OWASP Cheat Sheet Series is a free collection of practical guidance on secure coding. PortSwigger Web Security Academy is a free hands-on training site with safe labs. Practise only in labs and on systems you own or have written permission to test.

## Developer tools and cloud
Pro Git by Scott Chacon and Ben Straub is free online and is the reference for Git. The Linux Command Line by William Shotts is free and is a good introduction to the shell. The official documentation of Docker, and the book Docker Deep Dive by Nigel Poulton, help with containers. GitHub Skills offers short interactive courses inside GitHub. The documentation of the major cloud providers includes free tiers and tutorials for beginners.

## A suggested path for a beginner in machine learning
Learn Python basics with Automate the Boring Stuff. Learn NumPy and pandas. Take Andrew Ng's course or read ISLP for the core ideas. Read Géron's Hands-On Machine Learning while building projects, and put the projects on GitHub. Then pick a direction: deep learning with fast.ai or Dive into Deep Learning, or language models with Karpathy's videos and Raschka's book. Read Bishop or Murphy later, when you want depth.

<!-- id: learning_resources_ar; topics: programming,ai,networking,databases,web_security,dev_tools -->
# كتب ومصادر تعلم مقترحة بالعربي

## أشهر كتب تعلم الآلة (machine learning)
هذه قائمة من اختيار كاتب واحد وبحسب المعرفة العامة، وليست ترتيباً رسمياً. تأكد من أحدث طبعة وأسعارها قبل الشراء.
الكتاب العملي الأشهر للمبتدئين هو Hands-On Machine Learning with Scikit-Learn, Keras and TensorFlow لمؤلفه Aurélien Géron، فيه شرح مختصر مع كود بايثون. للأساس الإحصائي هناك An Introduction to Statistical Learning (واختصاره ISLR، وله نسخة بايثون اسمها ISLP) لـ James وWitten وHastie وTibshirani، وهو مجاني للقراءة من موقع المؤلفين. وللتعمق الرياضي هناك The Elements of Statistical Learning.
الكتب الكلاسيكية الأكاديمية هي Pattern Recognition and Machine Learning لـ Christopher Bishop وMachine Learning: A Probabilistic Perspective لـ Kevin Murphy، وهي تحتاج أساساً جيداً بالجبر الخطي والاحتمالات. وللتعلم العميق (deep learning) هناك كتاب Deep Learning لـ Goodfellow وBengio وCourville ويمكن قراءته مجاناً على الموقع deeplearningbook.org، وكتاب Dive into Deep Learning التفاعلي المجاني على d2l.ai مع كود يعمل لكل فكرة.
لتعلم النماذج اللغوية الكبيرة هناك Build a Large Language Model From Scratch لـ Sebastian Raschka، وNatural Language Processing with Transformers لشرح مكتبة Hugging Face، وSpeech and Language Processing لـ Jurafsky وMartin (مسودة الطبعة الأحدث مجانية على الإنترنت).

## دورات مجانية ومدفوعة
دورة Machine Learning Specialization لـ Andrew Ng على Coursera هي أشهر بداية. ودورة fast.ai المسماة Practical Deep Learning for Coders مجانية وتعلّم ببناء مشاريع أولاً. وسلسلة فيديوهات Neural Networks: Zero to Hero لـ Andrej Karpathy تبني شبكة عصبية ونموذج GPT من الصفر. ومحاضرات جامعة Stanford مثل CS229 وCS231n وCS224n متاحة على يوتيوب. ومنصة Kaggle فيها دورات قصيرة ومسابقات للتطبيق العملي.

## مصادر لمواضيع أخرى
للبرمجة: Automate the Boring Stuff with Python (مجاني) وCS50 من Harvard (مجاني) وكتاب Introduction to Algorithms للخوارزميات. للشبكات: Computer Networking: A Top-Down Approach لـ Kurose وRoss. لقواعد البيانات: Database System Concepts وDesigning Data-Intensive Applications لـ Martin Kleppmann. للأمان: Security Engineering لـ Ross Anderson ومنصة PortSwigger Web Security Academy المجانية للتدريب بمختبرات آمنة. لأدوات التطوير: كتاب Pro Git المجاني.

## مسار مقترح لمبتدئ في تعلم الآلة
ابدأ بأساسيات بايثون، ثم مكتبتي NumPy وpandas، ثم دورة Andrew Ng أو كتاب ISLP لفهم الأفكار الأساسية، ثم كتاب Géron مع بناء مشاريع ونشرها على GitHub. بعدها اختر اتجاهاً: التعلم العميق مع fast.ai أو Dive into Deep Learning، أو النماذج اللغوية مع Karpathy وRaschka. اترك كتب Bishop وMurphy لمرحلة متأخرة عندما تريد التعمق.

<!-- id: ml_algorithms_explained; topics: ai -->
# Classic Machine Learning Algorithms Explained With Working Code

## How to read this note
Each algorithm is explained in plain words, then shown with a short NumPy implementation so that you see exactly what it does. The NumPy code was run and the printed numbers below are real outputs. In practice you will use scikit-learn, which provides tested and faster versions, and a short scikit-learn equivalent is listed at the end. Where several code blocks follow each other, later blocks reuse the variables X and y created in the logistic regression block.

## Linear regression
Linear regression predicts a number as a weighted sum of the features plus a bias: y is approximately X times w. Training finds the weights that minimise the mean squared error between predictions and true values. There are two ways. The closed form solution (the normal equation, or a least squares solver) computes the best weights directly. Gradient descent starts from zero weights and repeatedly moves them against the gradient of the error, which also works when the closed form is too expensive or does not exist, as in neural networks.
```python
import numpy as np
rng = np.random.default_rng(0)
X = rng.random((200, 1))
y = 2 + 3 * X[:, 0] + rng.normal(0, 0.1, 200)
Xb = np.c_[np.ones(len(X)), X]
w_closed = np.linalg.lstsq(Xb, y, rcond=None)[0]
w = np.zeros(2)
for _ in range(2000):
    grad = 2 / len(y) * Xb.T @ (Xb @ w - y)
    w -= 0.5 * grad
print(w_closed.round(3), w.round(3))
```
Both methods print [2.005 2.975], close to the true intercept 2 and slope 3 that generated the data, and the small difference is the effect of the noise. Linear regression assumes a roughly linear relationship, and it is sensitive to outliers and to strongly correlated features. Its great strength is that the weights are easy to interpret. Ridge regression adds an L2 penalty on the weights and lasso adds an L1 penalty, which reduces overfitting.

## Logistic regression
Despite its name, logistic regression is a classification method. It computes a linear score, passes it through the sigmoid function to get a probability between 0 and 1, and predicts class 1 when the probability is above 0.5. It is trained by minimising the cross-entropy loss, and the gradient has a beautifully simple form: the features multiplied by the difference between predicted probability and true label.
```python
import numpy as np
rng = np.random.default_rng(1)
X = np.r_[rng.normal(-1, 1, (100, 2)), rng.normal(1, 1, (100, 2))]
y = np.r_[np.zeros(100), np.ones(100)]
Xb = np.c_[np.ones(len(X)), X]
w = np.zeros(3)
sigmoid = lambda z: 1 / (1 + np.exp(-z))
for _ in range(2000):
    p = sigmoid(Xb @ w)
    w -= 0.1 * Xb.T @ (p - y) / len(y)
acc = ((sigmoid(Xb @ w) > 0.5) == y).mean()
print(w.round(2), acc)
```
On these two overlapping groups of points the result is weights [0.34 3.25 3.3] and a training accuracy of 0.965. The two classes overlap, so perfect accuracy is not possible. Logistic regression gives a good baseline for classification, produces probabilities, and for more than two classes it generalises to softmax regression. Feature scaling helps gradient descent to converge faster.

## k-nearest neighbours
k-NN stores the whole training set and classifies a new point by looking at its k closest training points and taking a majority vote. There is no training phase, but prediction is slow on big datasets because distances to all points are computed. Always scale features first, otherwise a feature with large numbers dominates the distance. A small k gives a jagged boundary that overfits, a large k gives a smooth boundary that underfits, and an odd k avoids ties in binary problems.
```python
def knn_predict(X_train, y_train, x, k=3):
    distances = np.linalg.norm(X_train - x, axis=1)
    nearest = np.argsort(distances)[:k]
    return np.bincount(y_train[nearest].astype(int)).argmax()

print(knn_predict(X, y, np.array([1.2, 0.8])), knn_predict(X, y, np.array([-1.5, -0.5])))
```
This prints 1 0: the first point is near the group centred at (1, 1) and the second near the group centred at (-1, -1).

## k-means clustering
k-means is an unsupervised method that splits data into k groups. It starts with k random centres, then repeats two steps: assign every point to its nearest centre, and move each centre to the mean of the points assigned to it. It stops when assignments no longer change. The result depends on the starting centres, so libraries run it several times and keep the best one. Choose k with the elbow method (plot the total within-cluster distance for several k and look for the bend) or the silhouette score, which measures how well each point fits its own cluster compared with the next closest cluster. k-means assumes round clusters of similar size, and it fails on elongated or ring-shaped groups, where DBSCAN or Gaussian mixtures work better.
```python
def kmeans(X, k, iters=20, seed=0):
    r = np.random.default_rng(seed)
    centers = X[r.choice(len(X), k, replace=False)]
    for _ in range(iters):
        labels = np.argmin(((X[:, None] - centers[None]) ** 2).sum(-1), axis=1)
        centers = np.array([X[labels == j].mean(0) if (labels == j).any() else centers[j] for j in range(k)])
    return labels, centers

labels, centers = kmeans(X, 2)
print(centers.round(2).tolist(), np.bincount(labels).tolist())
```
It prints the centres [[-1.08, -1.13], [0.77, 1.04]] and cluster sizes [98, 102], close to the true groups of 100 points each.

## Decision trees and Gini impurity
A decision tree asks a sequence of yes or no questions about the features, such as "is age greater than 30?", and each leaf gives a prediction. At every node the algorithm chooses the question that makes the resulting groups as pure as possible. Gini impurity measures purity: it is 1 minus the sum of squared class proportions. It is 0 for a pure group and 0.5 for a perfect 50-50 split of two classes. The best split is the one with the lowest weighted average impurity of the two child groups, which is the same as the largest impurity decrease. Entropy and information gain are an alternative measure with similar results.
```python
def gini(labels):
    p = np.bincount(labels) / len(labels)
    return 1 - (p ** 2).sum()

print(gini(np.array([0, 0, 1, 1])), gini(np.array([1, 1, 1, 1])), gini(np.array([0, 1, 1, 1])))
left, right = np.array([0, 0, 0, 1]), np.array([1, 1, 1, 0])
parent = np.array([0, 0, 0, 1, 1, 1, 1, 0])
weighted = (len(left) * gini(left) + len(right) * gini(right)) / len(parent)
print(gini(parent), weighted)
```
The first line prints 0.5, 0.0 and 0.375. The second prints 0.5 for the parent node and 0.375 for the weighted children, so this split reduces impurity by 0.125. Trees are easy to explain and need no feature scaling, but a deep tree overfits badly, so limit max_depth or use pruning.

## Random forests and gradient boosting
An ensemble combines many weak models into a strong one. Bagging (bootstrap aggregating) trains each model on a random sample of the data drawn with replacement and averages the results, which reduces variance. A random forest is bagging of decision trees where each split also considers only a random subset of the features, so trees are different from each other. Boosting trains models one after another, and each new model focuses on the mistakes of the previous ones: in gradient boosting every new tree is fitted to the residual errors, the difference between the true values and the current predictions, and added with a small learning rate. Boosting reduces bias and usually gives the highest accuracy on tabular data, but it can overfit and needs tuning. XGBoost, LightGBM and CatBoost are popular fast implementations. For structured table data, gradient boosting or a random forest is often a stronger first choice than a deep neural network.

## Support vector machines
An SVM finds the separating line (or hyperplane) with the largest margin, the widest empty street between the classes. Only the points closest to the boundary, the support vectors, define it. The parameter C controls the trade-off: a large C punishes misclassification strongly and risks overfitting, a small C allows a wider margin with some errors. The kernel trick lets an SVM separate data that is not linearly separable by implicitly working in a higher dimensional space, and the RBF kernel is the usual default. SVMs work well on small and medium datasets with many features, but they scale poorly to very large datasets and need feature scaling.

## Naive Bayes
Naive Bayes applies Bayes theorem: the probability of a class given the features is proportional to the prior probability of the class times the probability of the features given the class. The word naive refers to the assumption that features are independent given the class, which is rarely true but still works surprisingly well, especially for text classification such as spam detection. It trains in one pass, needs little data, and is very fast. Use Laplace smoothing so that a word never seen in a class does not give a zero probability.

## Principal component analysis
PCA reduces the number of features while keeping as much variance as possible. It centres the data, then finds new orthogonal directions, the principal components, along which the data varies most. This can be done by singular value decomposition. The share of variance explained by each component tells you how many components to keep. PCA is used for visualisation, noise reduction, speeding up other algorithms and removing correlation between features. Scale the features first, because PCA is driven by variance.
```python
rng = np.random.default_rng(0)
A = rng.normal(size=(200, 3)) @ np.diag([3, 1, 0.1])
Ac = A - A.mean(axis=0)
U, S, Vt = np.linalg.svd(Ac, full_matrices=False)
explained = S ** 2 / (len(A) - 1)
print((explained / explained.sum()).round(3))
```
The output [0.902 0.097 0.001] shows that the first component carries about 90 percent of the variance, which is expected because that axis was built with the largest spread, so two components are enough to describe this dataset.

## A worked example of why accuracy can mislead
Suppose a disease test is applied to 1000 people, and the confusion matrix has 40 true positives, 10 false positives, 20 false negatives and 930 true negatives.
```python
tp, fp, fn, tn = 40, 10, 20, 930
precision = tp / (tp + fp)
recall = tp / (tp + fn)
f1 = 2 * precision * recall / (precision + recall)
accuracy = (tp + tn) / (tp + fp + fn + tn)
print(round(precision, 3), round(recall, 3), round(f1, 3), accuracy)
```
It prints precision 0.8, recall 0.667, F1 0.727 and accuracy 0.97. The 97 percent accuracy looks excellent, yet the test misses one third of the sick people (recall 0.667), because the healthy majority dominates the accuracy. For imbalanced problems report precision, recall and F1, and choose the threshold according to the cost of each kind of error.

## Which algorithm should I try first
For a table of numbers and categories, start with logistic or linear regression as a baseline, then a random forest and gradient boosting. For images use a convolutional network or a pretrained vision model. For text, use a pretrained transformer, or TF-IDF with logistic regression as a quick baseline. For very small datasets prefer simple models and strong regularisation. If you must explain every decision, prefer linear models and shallow trees. For grouping without labels use k-means or hierarchical clustering, and for finding unusual points use isolation forest. Always compare against a trivial baseline, such as predicting the most common class, so you know whether the model learned anything.

## The same algorithms in scikit-learn
These are the standard class names, which you import from scikit-learn: LinearRegression, Ridge and Lasso in sklearn.linear_model; LogisticRegression in sklearn.linear_model; KNeighborsClassifier in sklearn.neighbors; KMeans in sklearn.cluster; DecisionTreeClassifier and RandomForestClassifier in sklearn.tree and sklearn.ensemble; GradientBoostingClassifier and HistGradientBoostingClassifier in sklearn.ensemble; SVC in sklearn.svm; GaussianNB and MultinomialNB in sklearn.naive_bayes; PCA in sklearn.decomposition. Every model follows the same pattern: create it, call fit(X_train, y_train), then predict(X_test), and evaluate with the functions in sklearn.metrics. Use Pipeline to combine scaling and a model so that preprocessing is learned only from the training data.

<!-- id: deep_learning_extras; topics: ai -->
# Deep Learning in More Depth: Numbers, Architectures and Training Practice

## Counting parameters
Knowing how to count parameters helps you estimate memory and spot mistakes. A fully connected layer with n_in inputs and n_out outputs has n_in times n_out weights plus n_out biases. A small network for 28 by 28 images with 784 inputs, a hidden layer of 128 units and 10 outputs has 784 times 128 plus 128 for the first layer and 128 times 10 plus 10 for the second.
```python
print(784 * 128 + 128 + 128 * 10 + 10)
```
The result is 101,770 parameters. Each parameter in 32-bit floating point takes 4 bytes, so this network needs about 400 kilobytes for its weights, while training needs extra memory for gradients and optimiser state, and Adam keeps two additional values per parameter.

## Softmax and cross-entropy with numbers
Softmax converts raw scores (logits) into probabilities that add up to 1. For the scores 2.0, 1.0 and 0.1 the probabilities are 0.659, 0.242 and 0.099. Cross-entropy loss for the true class is the negative logarithm of the probability the model gave to it. If the true class is the first one, the loss is minus log of 0.659, which is 0.417. If the model gave every class equal probability, the loss would be log of 3, which is 1.099, and this is the value an untrained three-class model should show at the start.
```python
import numpy as np

def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()

p = softmax(np.array([2.0, 1.0, 0.1]))
print(p.round(3), -np.log(p[0]).round(3), np.log(3).round(3))
```
The output is [0.659 0.242 0.099] 0.417 1.099. Subtracting the maximum score before exponentiating prevents overflow and does not change the result.

## Convolution output size and parameters
For an input of width n, a kernel of size k, padding p and stride s, the output width is floor((n + 2p - k) / s) + 1. This formula is used constantly when designing convolutional networks.
```python
def conv_out(n, k, padding=0, stride=1):
    return (n + 2 * padding - k) // stride + 1

print(conv_out(32, 3, 1, 1), conv_out(32, 5, 0, 1), conv_out(32, 3, 1, 2), conv_out(224, 7, 3, 2))
print(3 * 3 * 3 * 16 + 16)
```
The first line prints 32, 28, 16 and 112. A 3 by 3 kernel with padding 1 keeps the size (the same padding), a 5 by 5 kernel without padding shrinks 32 to 28, a stride of 2 halves the size, and the 7 by 7 stride-2 first layer of ResNet reduces 224 to 112. The second line prints 448, the number of parameters of a convolution layer with 3 input channels and 16 filters of size 3 by 3, which is 3 times 3 times 3 times 16 weights plus 16 biases. Compare that with a fully connected layer on the same image, which would need millions of weights. The receptive field grows with depth, so deeper layers see larger parts of the image.

## Residual connections and normalisation
Very deep networks were hard to train until residual connections were introduced in ResNet. A residual block computes F of x and adds the input back, giving x plus F of x, so gradients have a direct path back through the identity shortcut and the block only needs to learn a correction. Batch normalisation normalises each feature using the mean and variance of the current mini-batch and then rescales it with learned parameters, which stabilises and speeds up training of convolutional networks. It behaves differently in training and evaluation mode, so remember model.eval(). Layer normalisation normalises across the features of each single example, does not depend on the batch size, and is the standard in transformers and recurrent models.

## Optimisers
Plain stochastic gradient descent (SGD) updates weights by the learning rate times the gradient. Momentum adds a running average of past gradients, which smooths the path and speeds up movement along consistent directions. RMSprop divides the step by a running average of the squared gradients so each weight gets its own scale. Adam combines momentum and this adaptive scaling and works well with little tuning, and AdamW fixes the way weight decay is applied and is the usual choice for transformers. SGD with momentum and a good learning rate schedule often generalises slightly better for image models, while Adam variants are the default for language models. Common schedules are step decay, cosine decay and a linear warm-up at the start of training.

## Weight initialisation and training stability
If weights start too large or too small, signals and gradients explode or vanish as they pass through many layers. Xavier (Glorot) initialisation keeps the variance of activations similar across layers and suits tanh or sigmoid, and He (Kaiming) initialisation is designed for ReLU activations. Frameworks apply sensible defaults, but knowing the idea helps when you debug. Gradient clipping limits the gradient norm and prevents sudden explosions, especially in recurrent networks and transformers. If the loss becomes NaN, reduce the learning rate, check for division by zero or logarithm of zero in the loss, and check the data for missing values.

## Batch size, epochs and mixed precision
A larger batch gives a more accurate gradient estimate and better hardware use, but needs more memory, and very large batches may need a larger learning rate and a warm-up. A smaller batch adds noise that can help generalisation. Mixed precision training uses 16-bit numbers for most operations and 32-bit where precision matters, which roughly halves memory and speeds up training on modern GPUs. When memory is short, gradient accumulation sums gradients over several small batches before one update, which imitates a larger batch.

## Recurrent networks, LSTM and GRU in words
A recurrent network reads a sequence one element at a time and updates a hidden state that summarises everything seen so far. In a plain recurrent network gradients are multiplied through every time step, so they vanish or explode over long sequences. An LSTM adds a cell state and three gates: the forget gate decides what to erase, the input gate decides what to write, and the output gate decides what to reveal. The cell state is updated mostly by addition, which lets gradients travel across many steps. A GRU is a simpler variant with two gates. Sequence-to-sequence models used an encoder to compress an input sentence into a vector and a decoder to generate the output, and attention was invented to let the decoder look back at all encoder states instead of one compressed vector, which led to the transformer.

## Autoencoders and variational autoencoders
An autoencoder is a network trained to reproduce its input after squeezing it through a narrow middle layer called the bottleneck or latent code. The encoder compresses and the decoder reconstructs, and the loss is the reconstruction error. It is used for compression, denoising and anomaly detection, because unusual inputs reconstruct badly. A variational autoencoder makes the latent code a probability distribution and adds a term that keeps it close to a standard normal distribution, so you can sample new latent vectors and decode them into new examples.

## GANs and diffusion models
A generative adversarial network trains two networks against each other. The generator turns random noise into fake examples, and the discriminator tries to tell real examples from fake ones. As the discriminator improves, the generator is pushed to produce more realistic outputs. GANs can produce sharp images but training is unstable and can suffer from mode collapse, where the generator produces only a few kinds of output. Diffusion models work differently: during training noise is gradually added to real images and a network learns to predict and remove that noise. To generate an image, the model starts from pure noise and removes it step by step. Diffusion models are more stable to train and power most current image generators, at the cost of slower generation because many denoising steps are needed.

## Transfer learning and fine-tuning in practice
Training a large vision or language model from scratch needs huge data and compute. Transfer learning reuses a model pretrained on a large dataset. The usual recipe for a small image dataset is to load a pretrained network, freeze its early layers, replace the last layer with one that matches your number of classes, train only that layer first with a normal learning rate, and then optionally unfreeze some deeper layers and train them with a much smaller learning rate.
```python
import torch.nn as nn
from torchvision import models

model = models.resnet18(weights="DEFAULT")
for p in model.parameters():
    p.requires_grad = False
model.fc = nn.Linear(model.fc.in_features, 5)
```
After this, only the new final layer has requires_grad set to True, so the optimiser should be given model.fc.parameters(). Pretrained models expect inputs preprocessed in the same way as their training data, with the same size and normalisation. For language models the equivalent is fine-tuning a pretrained transformer, often with LoRA so that only small adapter matrices are trained.

## Evaluating language models
Perplexity measures how surprised a language model is by a text, and lower is better. It is the exponential of the average cross-entropy per token. BLEU and ROUGE compare generated text with reference text by counting overlapping word sequences, and they are mainly used in translation and summarisation, but they correlate poorly with human judgement for open-ended answers. Benchmarks such as multiple-choice question sets measure knowledge and reasoning, but models may have seen benchmark data during training. For applications, the most reliable evaluation is a test set built from your own real questions, with human or carefully checked scoring, and checking that answers are grounded in the provided sources.

## Scaling and the cost of training
Empirical scaling laws show that the loss of language models falls predictably as model size, data and compute grow, following power laws, which is why models became larger. Training a large model needs many GPUs working in parallel. Data parallelism copies the model to each GPU and splits the batch, model or tensor parallelism splits the model itself across GPUs, and techniques such as sharded optimiser states reduce memory per GPU. Inference cost depends on model size, context length and the KV cache. Smaller models trained on more data, quantised models and distilled models, where a small student is trained to imitate a large teacher, make good performance affordable.

<!-- id: ml_dl_questions_and_answers; topics: ai -->
# Machine Learning and Deep Learning: Frequently Asked Questions

## What is the difference between machine learning and deep learning?
Machine learning is the broad field of algorithms that learn patterns from data. Deep learning is a subset that uses neural networks with many layers. Classic machine learning, such as linear models, trees and support vector machines, usually needs hand-designed features and works well on small or tabular datasets. Deep learning learns its own features from raw data such as pixels, audio or text, and shines on large datasets, but needs more data, more computing power and more tuning.

## When should I use classic machine learning instead of deep learning?
Use classic machine learning when your data is a table with up to hundreds of thousands of rows, when you have little data, when you need fast training on a laptop, or when you must explain predictions. Gradient boosting and random forests are often better than neural networks on tabular data. Use deep learning for images, audio, video, text and other unstructured data, or when you have a very large dataset and enough hardware.

## What is the difference between supervised, unsupervised and reinforcement learning?
Supervised learning learns from examples that have correct answers (labels), for predicting categories or numbers. Unsupervised learning finds structure in data without labels, such as clusters or lower-dimensional representations. Reinforcement learning has an agent that takes actions in an environment and learns a policy from rewards. Self-supervised learning creates its own labels from the data, for example predicting the next word, and it is how large language models are pretrained.

## What is a loss function?
A loss function is a number that measures how wrong the model's predictions are, and training tries to minimise it. Mean squared error is common for regression, binary cross-entropy for two classes, and categorical cross-entropy for many classes. The loss must be differentiable so that gradients can be computed, which is why accuracy itself is not used as a training loss, even though it is a useful evaluation metric.

## What is the difference between parameters and hyperparameters?
Parameters are the values the model learns from data, such as weights and biases. Hyperparameters are settings you choose before training, such as the learning rate, batch size, number of layers, tree depth, regularisation strength and number of epochs. Hyperparameters are tuned using a validation set or cross-validation, never the test set.

## What is the difference between an epoch, a batch and an iteration?
An epoch is one full pass over the training dataset. A batch is the small group of examples used for one parameter update. An iteration is one such update. With 1000 examples and a batch size of 100, one epoch has 10 iterations.

## What is regularisation and why is it used?
Regularisation reduces overfitting by discouraging overly complex models. Examples are the L1 and L2 penalties on the weights, dropout, early stopping, data augmentation and limiting tree depth. It trades a little training accuracy for better performance on new data.

## What is the difference between L1 and L2 regularisation?
L2 regularisation (ridge, weight decay) adds the sum of squared weights to the loss and shrinks all weights smoothly toward zero without making them exactly zero. L1 regularisation (lasso) adds the sum of absolute weights and tends to push many weights to exactly zero, which produces sparse models and acts as automatic feature selection. Elastic net combines both.

## Why do we normalise or standardise features?
Features with very different scales make gradient descent slow and unstable, and they dominate distance-based methods such as k-nearest neighbours, k-means, SVMs and PCA. Standardisation subtracts the mean and divides by the standard deviation, and min-max scaling maps values to a fixed range. Compute the statistics on the training set only and apply the same transformation to validation and test data, otherwise you leak information. Tree-based models do not need scaling.

## What is the vanishing gradient problem?
In deep networks, gradients are multiplied through many layers during backpropagation. If the factors are smaller than one, as with saturating sigmoid or tanh activations, the gradient shrinks toward zero in the early layers and they stop learning. Remedies are ReLU-type activations, careful initialisation, normalisation layers and residual connections. The opposite problem, exploding gradients, is handled with gradient clipping.

## What is transfer learning?
Transfer learning reuses a model trained on a large dataset as the starting point for a new task. You keep the pretrained layers that learned general features, replace the output layer, and train on your smaller dataset. It needs far less data and time than training from scratch and is the standard approach for images and language.

## What is the difference between CNNs, RNNs and transformers?
Convolutional neural networks use small shared filters that slide over the input and are ideal for images and other grid-like data. Recurrent networks process sequences step by step with a hidden state and were used for text and time series, but they are slow to train and struggle with long dependencies. Transformers use attention to relate all positions of a sequence to each other in parallel, and they dominate language, and increasingly images and audio.

## What is attention in simple words?
Attention lets a model decide, for each element of the input, which other elements are most relevant to it. Each token produces a query, a key and a value. The similarity of a query to all keys gives weights, and the output is the weighted average of the values. In the sentence about an animal that did not cross the street because it was tired, attention helps connect the word it with the animal.

## What is the difference between bagging and boosting?
Bagging trains many models independently on random samples of the data and averages them, which reduces variance, and random forest is the best-known example. Boosting trains models one after another, each one correcting the errors of the previous ones, which reduces bias, and gradient boosting, XGBoost and LightGBM are examples. Bagging is easy to parallelise and hard to overfit, boosting is often more accurate but needs careful tuning.

## How do I choose the number of clusters in k-means?
Try several values of k. With the elbow method plot the within-cluster sum of squares against k and pick the point where improvement slows sharply. With the silhouette score choose the k that gives the highest average silhouette. Also use domain knowledge, since the best number of groups for your purpose may be fixed by the application.

## How do I handle imbalanced classes?
First use metrics that fit the problem, such as precision, recall, F1 and the precision-recall curve, instead of accuracy. Then try class weights so that mistakes on the rare class cost more, resampling by oversampling the rare class (for example with SMOTE, which creates synthetic examples) or undersampling the common class, and tuning the decision threshold. Collecting more examples of the rare class is often the best fix. Do resampling only on the training data, never before splitting.

## What is feature engineering?
Feature engineering means creating better inputs for a model from raw data, for example extracting the day of the week from a date, combining two columns into a ratio, encoding categories as numbers with one-hot encoding, or computing counts and averages per customer. For classic machine learning on tabular data it often improves results more than changing the algorithm. Deep learning reduces the need for it on images and text.

## What is the curse of dimensionality?
As the number of features grows, the volume of the space grows so fast that data becomes sparse, distances between points become less meaningful, and models need exponentially more data to generalise. Remedies include feature selection, dimensionality reduction such as PCA, regularisation and using algorithms that cope better with many features.

## What is the difference between generative and discriminative models?
A discriminative model learns the boundary between classes, that is the probability of the label given the input, as logistic regression and most neural classifiers do. A generative model learns how the data itself is produced, so it can create new examples, as GANs, diffusion models, variational autoencoders and language models do. Naive Bayes is a classic generative classifier.

## How much data do I need for deep learning?
There is no fixed number. Training from scratch typically needs thousands to millions of examples, depending on the task and model size, while fine-tuning a pretrained model can work with hundreds. More important than the exact count is quality and coverage of the data. Learning curves, which plot validation performance against the amount of training data, show whether collecting more data would help. If the curve is still rising, more data helps.

## How do I tune hyperparameters?
Grid search tries every combination from a list and becomes expensive quickly. Random search samples combinations at random and usually finds good settings faster, because only a few hyperparameters matter much. Bayesian optimisation uses previous results to choose promising settings, and tools such as Optuna implement it. Always evaluate on a validation set or with cross-validation, and keep the test set untouched until the end.

## What are the ROC curve and AUC?
The ROC curve plots the true positive rate against the false positive rate for all possible decision thresholds. The area under it, AUC, ranges from 0.5 for random guessing to 1.0 for a perfect ranking, and it equals the probability that a random positive example is scored higher than a random negative one. With highly imbalanced data the precision-recall curve is usually more informative than ROC.

## What is a confusion matrix?
A confusion matrix is a table that compares predicted classes with true classes. For two classes it has four cells: true positives, false positives, false negatives and true negatives. Precision, recall, accuracy and F1 are all computed from these four numbers.

## My model has 100 percent training accuracy but low test accuracy. What is wrong?
The model is overfitting: it has memorised the training data. Try more data, a simpler model, regularisation, dropout, early stopping or data augmentation, and check that there is no data leakage and that the train and test sets come from the same distribution. If the test accuracy is far lower than validation accuracy, check whether the test set differs from the data used for tuning.

## What is early stopping?
Early stopping monitors the validation loss during training and stops when it has not improved for a set number of epochs (the patience), then restores the best weights. It prevents overfitting and saves time, and it works like a form of regularisation.

## What is RLHF?
Reinforcement learning from human feedback is a way to align language models with human preferences. People compare pairs of model answers, a reward model is trained to predict their preferences, and the language model is then optimised to produce answers that receive higher reward. Direct preference optimisation achieves a similar goal without a separate reward model and a reinforcement learning loop.

## What is the difference between fine-tuning and RAG?
Fine-tuning changes the weights of the model to adapt its style, format or behaviour, and it is a poor way to add facts that change. Retrieval-augmented generation keeps the model unchanged and gives it relevant documents at question time, which lets answers use up-to-date or private knowledge and cite sources. Many production systems combine both.

<!-- id: ml_dl_qa_ar; topics: ai -->
# أسئلة وأجوبة شائعة في تعلم الآلة والتعلم العميق

## ما الفرق بين تعلم الآلة (machine learning) والتعلم العميق (deep learning)؟
تعلم الآلة هو المجال الواسع للخوارزميات التي تتعلم الأنماط من البيانات. والتعلم العميق جزء منه يستخدم شبكات عصبية بطبقات كثيرة. الطرق الكلاسيكية مثل الانحدار الخطي (linear regression) والأشجار (decision trees) وآلة المتجهات الداعمة (SVM) تحتاج غالباً إلى ميزات (features) يصممها الإنسان وتعمل جيداً مع البيانات الصغيرة والجدولية. أما التعلم العميق فيتعلم الميزات بنفسه من البيانات الخام مثل الصور والصوت والنصوص، لكنه يحتاج بيانات أكثر وقدرة حسابية أكبر وضبطاً أكثر.

## متى أستخدم تعلم الآلة الكلاسيكي بدل التعلم العميق؟
استخدم الطرق الكلاسيكية عندما تكون بياناتك جدولاً (tabular) بحجم صغير أو متوسط، أو عندما تكون البيانات قليلة، أو تريد تدريباً سريعاً على جهاز عادي، أو تحتاج لتفسير القرارات. غالباً تتفوق خوارزميات gradient boosting وrandom forest على الشبكات العصبية في البيانات الجدولية. واستخدم التعلم العميق للصور والصوت والفيديو والنصوص، أو عندما تتوفر بيانات ضخمة وعتاد قوي.

## ما هي أنواع التعلم: الموجَّه وغير الموجَّه والمعزَّز؟
التعلم الموجَّه (supervised) يتعلم من أمثلة لها إجابات صحيحة (labels) للتصنيف أو التنبؤ بأرقام. التعلم غير الموجَّه (unsupervised) يكتشف بنية في بيانات بلا إجابات مثل التجميع (clustering). التعلم المعزَّز (reinforcement learning) يتعلم فيه وكيل (agent) باتخاذ إجراءات في بيئة ويحصل على مكافآت. والتعلم الذاتي الإشراف (self-supervised) يصنع إجاباته من البيانات نفسها، مثل توقع الكلمة التالية، وبه تُدرَّب النماذج اللغوية الكبيرة.

## ما الفرق بين المعاملات (parameters) والمعاملات الفائقة (hyperparameters)؟
المعاملات هي القيم التي يتعلمها النموذج مثل الأوزان (weights) والانحيازات (biases). أما المعاملات الفائقة فهي إعدادات تختارها قبل التدريب مثل معدل التعلم (learning rate) وحجم الدفعة (batch size) وعدد الطبقات وعمق الشجرة وقوة التنظيم. تُضبط المعاملات الفائقة باستخدام بيانات التحقق أو التحقق المتقاطع، وليس بيانات الاختبار أبداً.

## ما الفرق بين epoch وbatch وiteration؟
الـ epoch هو مرور كامل على بيانات التدريب. والـ batch مجموعة صغيرة من الأمثلة تُستخدم لتحديث واحد للأوزان. والـ iteration هو تحديث واحد. فإذا كان عندك 1000 مثال وحجم الدفعة 100 فكل epoch فيه 10 iterations.

## ما هو فرط التخصيص (overfitting) وكيف أعالجه؟
هو أن يحفظ النموذج بيانات التدريب فيحقق دقة عالية عليها ويفشل مع بيانات جديدة. العلاج: بيانات أكثر، نموذج أبسط، التنظيم (regularization) مثل L1 وL2 وdropout، الإيقاف المبكر (early stopping)، زيادة البيانات (data augmentation)، والتحقق من عدم وجود تسرب بيانات (data leakage). وإذا كانت دقة التدريب 100% ودقة الاختبار منخفضة فالسبب غالباً فرط التخصيص.

## ما هو التنظيم (regularization) وما الفرق بين L1 وL2؟
التنظيم يحد من تعقيد النموذج لتقليل فرط التخصيص. عقوبة L2 (ridge أو weight decay) تقلص كل الأوزان بنعومة نحو الصفر دون أن تصبح صفراً تماماً. وعقوبة L1 (lasso) تدفع كثيراً من الأوزان إلى صفر تماماً فينتج نموذج متناثر (sparse) وكأنه اختار الميزات تلقائياً.

## لماذا نطبّع الميزات (feature scaling)؟
لأن الميزات ذات المقاييس المختلفة تبطئ التدريب وتجعل الخوارزميات المعتمدة على المسافات مثل k-NN وk-means وSVM وPCA تتأثر بالميزة الأكبر قيمة. يمكن استخدام التوحيد القياسي (standardization) أو min-max. احسب المتوسط والانحراف من بيانات التدريب فقط ثم طبّقهما على التحقق والاختبار حتى لا يحدث تسرب. النماذج الشجرية لا تحتاج تطبيعاً.

## ما هي مشكلة تلاشي المشتقات (vanishing gradient)؟
في الشبكات العميقة تتضاعف المشتقات عبر الطبقات أثناء الانتشار الخلفي (backpropagation). إذا كانت العوامل أصغر من واحد، كما في دوال sigmoid وtanh، تتقلص المشتقات حتى تقترب من الصفر في الطبقات الأولى فتتوقف عن التعلم. الحلول: دوال تنشيط مثل ReLU، التهيئة الجيدة للأوزان، طبقات التطبيع، والوصلات المتبقية (residual connections). والمشكلة المعاكسة انفجار المشتقات تُعالج بقص المشتقات (gradient clipping).

## ما هو نقل التعلم (transfer learning)؟
هو استخدام نموذج مدرَّب مسبقاً على بيانات ضخمة كنقطة بداية لمهمة جديدة. تحتفظ بالطبقات التي تعلمت ميزات عامة وتستبدل طبقة الإخراج وتدرب على بياناتك الصغيرة. يحتاج بيانات ووقتاً أقل بكثير من التدريب من الصفر، وهو الأسلوب المعتاد للصور واللغة.

## ما الفرق بين CNN وRNN وTransformer؟
الشبكات الالتفافية (CNN) تستخدم مرشحات صغيرة مشتركة تنزلق على المدخلات وتناسب الصور. الشبكات التكرارية (RNN) تعالج التسلسلات خطوة بخطوة بحالة مخفية وكانت تُستخدم للنصوص والسلاسل الزمنية لكنها بطيئة وضعيفة مع الاعتماديات الطويلة. أما المحوّلات (Transformers) فتستخدم الانتباه (attention) لربط كل المواضع ببعضها بالتوازي، وهي المهيمنة على اللغة وبدأت تهيمن على الصور والصوت.

## ما هو الانتباه (attention) بكلمات بسيطة؟
هو آلية تجعل النموذج يقرر لكل عنصر في المدخل أي العناصر الأخرى أهم له. كل رمز (token) ينتج استعلاماً (query) ومفتاحاً (key) وقيمة (value). تشابه الاستعلام مع كل المفاتيح يعطي أوزاناً، والناتج هو المتوسط الموزون للقيم.

## ما الفرق بين bagging وboosting؟
الـ bagging يدرب نماذج كثيرة باستقلال على عينات عشوائية من البيانات ثم يأخذ المتوسط، فيقلل التباين (variance)، ومثاله random forest. أما الـ boosting فيدرب النماذج بالتتابع بحيث يصحح كل نموذج أخطاء السابق، فيقلل الانحياز (bias)، ومثاله gradient boosting وXGBoost وLightGBM. الأول أسهل في التوازي وأصعب في فرط التخصيص، والثاني أدق غالباً لكنه يحتاج ضبطاً.

## كيف أختار عدد المجموعات k في k-means؟
جرّب عدة قيم لـ k. بطريقة المرفق (elbow) ارسم مجموع المربعات داخل المجموعات مقابل k واختر النقطة التي يتباطأ عندها التحسن. وبمعيار silhouette اختر k صاحب أعلى متوسط. واستعن بمعرفتك بالمجال لأن الغرض من التطبيق قد يحدد العدد.

## كيف أتعامل مع البيانات غير المتوازنة (imbalanced data)؟
استخدم مقاييس مناسبة مثل precision وrecall وF1 بدل الدقة (accuracy). ثم جرّب أوزان الفئات (class weights) لتكون أخطاء الفئة النادرة أغلى، أو إعادة العينات بزيادة الفئة النادرة (مثل SMOTE الذي ينشئ أمثلة اصطناعية) أو تقليل الفئة الشائعة، أو ضبط عتبة القرار (threshold). وغالباً أفضل حل هو جمع أمثلة أكثر من الفئة النادرة. طبّق إعادة العينات على بيانات التدريب فقط بعد التقسيم.

## ما هو منحنى ROC وما هو AUC؟
منحنى ROC يرسم معدل الموجب الحقيقي مقابل معدل الموجب الكاذب عند كل عتبات القرار الممكنة. والمساحة تحته AUC تتراوح من 0.5 للتخمين العشوائي إلى 1.0 للترتيب المثالي. ومع البيانات شديدة عدم التوازن يكون منحنى precision-recall أكثر فائدة غالباً.

## ما هي مصفوفة الالتباس (confusion matrix)؟
جدول يقارن الفئات المتوقعة بالفئات الحقيقية. في التصنيف الثنائي فيها أربع خانات: موجب حقيقي (TP) وموجب كاذب (FP) وسالب كاذب (FN) وسالب حقيقي (TN). ومنها تُحسب الدقة (accuracy) وprecision وrecall وF1.

## كم بيانات أحتاج للتعلم العميق؟
لا يوجد رقم ثابت. التدريب من الصفر يحتاج عادة آلاف إلى ملايين الأمثلة بحسب المهمة وحجم النموذج، بينما الضبط الدقيق (fine-tuning) لنموذج مدرب مسبقاً قد يعمل بمئات الأمثلة. الأهم جودة البيانات وتغطيتها. ويمكن رسم منحنى التعلم (learning curve) لمعرفة هل ستفيد بيانات إضافية: إذا كان المنحنى ما زال يرتفع فالمزيد من البيانات مفيد.

## ما الفرق بين الضبط الدقيق (fine-tuning) وRAG؟
الضبط الدقيق يغيّر أوزان النموذج ليتكيف مع أسلوب أو صيغة أو سلوك معين، وهو طريقة ضعيفة لإضافة معلومات تتغير. أما RAG فيترك النموذج كما هو ويعطيه مستندات ذات صلة وقت السؤال، فيستخدم معرفة حديثة أو خاصة ويذكر المصادر. وكثير من الأنظمة تجمع الاثنين.

## ما هو RLHF؟
هو التعلم المعزَّز من تغذية راجعة بشرية لمواءمة النموذج اللغوي مع تفضيلات الناس. يقارن البشر بين أجوبة النموذج، ويُدرَّب نموذج مكافأة (reward model) ليتنبأ بتفضيلاتهم، ثم يُحسَّن النموذج اللغوي ليعطي أجوبة بمكافأة أعلى. وطريقة DPO تحقق هدفاً مشابهاً بدون نموذج مكافأة منفصل.

## كيف أبدأ بمشروع تعلم آلة من الصفر؟
حدد المشكلة والمقياس المطلوب أولاً. اجمع البيانات ونظفها وقسمها إلى تدريب وتحقق واختبار. ابدأ بنموذج بسيط كنقطة مقارنة (baseline) مثل الانحدار اللوجستي أو شجرة. ثم جرّب نماذج أقوى وحسّن الميزات واضبط المعاملات الفائقة بالتحقق المتقاطع. قيّم مرة واحدة على بيانات الاختبار، ثم انشر وراقب الأداء مع الوقت لأن البيانات تتغير.

<!-- id: ml_dl_books_extended; topics: ai,programming -->
# More Books and Free Resources for Machine Learning and Deep Learning

## How this list is organised
This is a second, longer list that complements the earlier recommendations. It was written from general knowledge, not from an official ranking, so check the newest edition, the price and whether a free version is still available. Books are grouped by level and by topic. A good rule is to pair one practical book with one theory book, and to build projects while reading.

## Absolute beginners and general introductions
Python Data Science Handbook by Jake VanderPlas covers NumPy, pandas, matplotlib and scikit-learn with runnable notebooks, and it is available free online. Python for Data Analysis by Wes McKinney, the creator of pandas, teaches data wrangling, and an open edition can be read online. The Hundred-Page Machine Learning Book by Andriy Burkov is a very compact overview of the main algorithms. Machine Learning Yearning by Andrew Ng is a short free guide on how to structure and debug machine learning projects. Grokking Deep Learning by Andrew Trask builds neural networks from scratch in NumPy with friendly explanations. Neural Networks and Deep Learning by Michael Nielsen is a free online book that explains neural networks and backpropagation step by step with code and is excellent for intuition.

## Practitioner books for classic machine learning
Hands-On Machine Learning with Scikit-Learn, Keras and TensorFlow by Aurélien Géron remains the best-known practical book. Feature Engineering and Selection by Max Kuhn and Kjell Johnson is free online and covers how to prepare features. Interpretable Machine Learning by Christoph Molnar is free online and explains how to understand model predictions with methods such as feature importance, partial dependence and SHAP. An Introduction to Statistical Learning with Applications in Python (ISLP) is the free statistical foundation, and it pairs well with the hands-on books.

## Deep learning books
Deep Learning with Python by François Chollet, the creator of Keras, is clear and example-driven. Deep Learning for Coders with fastai and PyTorch by Jeremy Howard and Sylvain Gugger is the companion of the fast.ai course and teaches top-down. Deep Learning with PyTorch by Stevens, Antiga and Viehmann is a practical introduction to PyTorch. Dive into Deep Learning (d2l.ai) is free and interactive. Understanding Deep Learning by Simon Prince (2023) is a modern and very well illustrated textbook that is free to download from its website. The Little Book of Deep Learning by François Fleuret is a short free book with a compact view of the main ideas. Deep Learning by Goodfellow, Bengio and Courville is the classic reference and free to read online. Generative Deep Learning by David Foster covers GANs, variational autoencoders, diffusion models and language models with code.

## Language models, natural language processing and computer vision
Hands-On Large Language Models by Jay Alammar and Maarten Grootendorst is a visual, practical guide to tokens, embeddings, retrieval and fine-tuning. Natural Language Processing with Transformers by Tunstall, von Werra and Wolf teaches the Hugging Face libraries. Build a Large Language Model From Scratch by Sebastian Raschka implements a GPT-style model step by step. Speech and Language Processing by Jurafsky and Martin is the standard textbook, with a free draft online. Computer Vision: Algorithms and Applications by Richard Szeliski is a comprehensive free textbook on vision. The free Hugging Face LLM course teaches transformers, fine-tuning and tokenisers with hands-on notebooks.

## Theory, mathematics and probability
Pattern Recognition and Machine Learning by Christopher Bishop and Machine Learning: A Probabilistic Perspective by Kevin Murphy are the classic theory books, with the newer Probabilistic Machine Learning books by Murphy available as free drafts. The Elements of Statistical Learning by Hastie, Tibshirani and Friedman is the advanced statistical reference and free as a PDF. Mathematics for Machine Learning by Deisenroth, Faisal and Ong is a free book on linear algebra, calculus, probability and optimisation written for machine learning learners. The video series Essence of Linear Algebra and the neural network series by 3Blue1Brown give visual intuition and are free, and StatQuest on YouTube explains statistics and machine learning concepts step by step.

## Reinforcement learning and artificial intelligence in general
Reinforcement Learning: An Introduction by Richard Sutton and Andrew Barto is the standard text, and the second edition is free from the authors. Artificial Intelligence: A Modern Approach by Stuart Russell and Peter Norvig is the standard broad textbook covering search, logic, probability, learning and more.

## Engineering and putting models into production
Designing Machine Learning Systems by Chip Huyen explains data pipelines, deployment, monitoring and iteration. Machine Learning Engineering by Andriy Burkov and the many MLOps guides explain the practical lifecycle. For building applications with language models, the documentation and courses from Hugging Face, and the guides of the model providers, are the most current sources because the field changes quickly.

## Free courses to pair with the books
Andrew Ng's Machine Learning Specialization, fast.ai Practical Deep Learning for Coders, Andrej Karpathy's Neural Networks: Zero to Hero, Stanford CS229, CS231n and CS224n, Google's Machine Learning Crash Course, and the Kaggle Learn micro-courses are all free, and together they cover most of what a beginner needs.

## A study plan in three levels
Level one, about two months: Python, NumPy and pandas, then Ng's course or ISLP, and one small project such as predicting house prices with a table. Level two, about three months: Géron's book, a Kaggle competition for practice, then fast.ai or Dive into Deep Learning for neural networks, and a project with images or text. Level three: choose a direction. For language models read Alammar's or Raschka's book and Karpathy's videos, for theory read Bishop or Murphy and Mathematics for Machine Learning, and for engineering read Huyen's book and deploy a model as a small web service.

<!-- id: ml_dl_books_extended_ar; topics: ai,programming -->
# المزيد من الكتب والمصادر المجانية لتعلم الآلة والتعلم العميق

## قائمة ثانية مكملة
هذه قائمة ثانية أطول تكمل التوصيات السابقة، كُتبت من المعرفة العامة وليست ترتيباً رسمياً. تأكد من أحدث طبعة والسعر وهل ما زالت نسخة مجانية متاحة. اجمع بين كتاب عملي وكتاب نظري، وابنِ مشاريع أثناء القراءة.

## للمبتدئين
كتاب Python Data Science Handbook لـ Jake VanderPlas يغطي NumPy وpandas وmatplotlib وscikit-learn بدفاتر قابلة للتشغيل ومتاح مجاناً على الإنترنت. وكتاب Python for Data Analysis لـ Wes McKinney (مؤلف مكتبة pandas) لتعلم تجهيز البيانات. وكتاب The Hundred-Page Machine Learning Book لـ Andriy Burkov نظرة مختصرة جداً على أهم الخوارزميات. وكتاب Machine Learning Yearning لـ Andrew Ng مجاني وقصير عن كيفية تنظيم مشاريع تعلم الآلة. وكتاب Neural Networks and Deep Learning لـ Michael Nielsen مجاني على الإنترنت ويشرح الشبكات العصبية والانتشار الخلفي خطوة بخطوة، وممتاز لبناء الحدس.

## كتب عملية لتعلم الآلة الكلاسيكي
كتاب Hands-On Machine Learning لـ Aurélien Géron هو الأشهر عملياً. وكتاب Feature Engineering and Selection لـ Kuhn وJohnson مجاني على الإنترنت ويشرح تجهيز الميزات. وكتاب Interpretable Machine Learning لـ Christoph Molnar مجاني ويشرح فهم تنبؤات النماذج بطرق مثل أهمية الميزات وSHAP. وكتاب ISLP هو الأساس الإحصائي المجاني.

## كتب التعلم العميق
كتاب Deep Learning with Python لـ François Chollet (مؤلف Keras) واضح ومليء بالأمثلة. وكتاب Deep Learning for Coders with fastai and PyTorch لـ Jeremy Howard وSylvain Gugger مرافق لدورة fast.ai. وكتاب Deep Learning with PyTorch مقدمة عملية لـ PyTorch. وكتاب Dive into Deep Learning مجاني وتفاعلي على d2l.ai. وكتاب Understanding Deep Learning لـ Simon Prince (2023) كتاب حديث وموضح بالرسوم ويمكن تحميله مجاناً من موقعه. وكتاب The Little Book of Deep Learning لـ François Fleuret مختصر ومجاني. وكتاب Deep Learning لـ Goodfellow وBengio وCourville هو المرجع الكلاسيكي ومجاني للقراءة على الإنترنت. وكتاب Generative Deep Learning لـ David Foster عن GANs وVAE ونماذج الانتشار (diffusion) والنماذج اللغوية.

## النماذج اللغوية والمعالجة اللغوية والرؤية الحاسوبية
كتاب Hands-On Large Language Models لـ Jay Alammar وMaarten Grootendorst دليل مصور وعملي عن الرموز والتضمينات والاسترجاع والضبط الدقيق. وكتاب Natural Language Processing with Transformers لتعلم مكتبات Hugging Face. وكتاب Build a Large Language Model From Scratch لـ Sebastian Raschka يبني نموذجاً شبيهاً بـ GPT خطوة بخطوة. وكتاب Speech and Language Processing لـ Jurafsky وMartin هو المرجع الدراسي القياسي ومسودته مجانية. وكتاب Computer Vision: Algorithms and Applications لـ Richard Szeliski مجاني وشامل. ودورة Hugging Face LLM Course المجانية تعلم المحوّلات والضبط الدقيق.

## النظرية والرياضيات
كتاب Pattern Recognition and Machine Learning لـ Bishop وكتاب Machine Learning: A Probabilistic Perspective لـ Murphy هما المرجعان النظريان الكلاسيكيان، وكتب Murphy الأحدث Probabilistic Machine Learning متاحة كمسودات مجانية. وكتاب The Elements of Statistical Learning مجاني بصيغة PDF. وكتاب Mathematics for Machine Learning مجاني ويغطي الجبر الخطي والتفاضل والاحتمالات والتحسين لمتعلمي تعلم الآلة. وسلسلتا 3Blue1Brown عن الجبر الخطي والشبكات العصبية تعطيان حدساً بصرياً مجانياً، وقناة StatQuest تشرح الإحصاء وتعلم الآلة خطوة بخطوة.

## التعلم المعزَّز والذكاء الاصطناعي العام
كتاب Reinforcement Learning: An Introduction لـ Sutton وBarto هو المرجع القياسي وطبعته الثانية مجانية من موقع المؤلفين. وكتاب Artificial Intelligence: A Modern Approach لـ Russell وNorvig هو الكتاب الشامل القياسي في الذكاء الاصطناعي.

## الهندسة والنشر
كتاب Designing Machine Learning Systems لـ Chip Huyen يشرح خطوط البيانات والنشر والمراقبة. ولبناء تطبيقات النماذج اللغوية فإن وثائق ودورات Hugging Face وأدلة مزودي النماذج هي الأحدث لأن المجال يتغير بسرعة.

## دورات مجانية ترافق الكتب
دورة Machine Learning Specialization لـ Andrew Ng، ودورة fast.ai، وسلسلة Neural Networks: Zero to Hero لـ Karpathy، ومحاضرات Stanford CS229 وCS231n وCS224n، وGoogle Machine Learning Crash Course، ودورات Kaggle Learn القصيرة.

## خطة دراسة بثلاث مراحل
المرحلة الأولى (شهران تقريباً): بايثون وNumPy وpandas، ثم دورة Ng أو ISLP، ومشروع صغير مثل التنبؤ بأسعار المنازل. المرحلة الثانية (ثلاثة أشهر تقريباً): كتاب Géron ومسابقة على Kaggle، ثم fast.ai أو Dive into Deep Learning، ومشروع بالصور أو النصوص. المرحلة الثالثة: اختر اتجاهاً. للنماذج اللغوية اقرأ Alammar أو Raschka وشاهد Karpathy، وللنظرية اقرأ Bishop أو Murphy مع Mathematics for Machine Learning، وللهندسة اقرأ كتاب Huyen وانشر نموذجاً كخدمة ويب صغيرة.

<!-- id: robotics_fundamentals; topics: robotics -->
# Robotics Fundamentals: From Sensors and Motors to Planning and ROS 2

## What is a robot?
A robot is a machine that senses its environment, makes decisions, and acts on the physical world, usually under computer control. The classic way to describe any robot is the sense, think, act loop. Sensors measure the world and the robot itself, software processes these measurements and decides what to do, and actuators such as motors move the robot. This loop repeats many times per second, and the quality of each part decides how well the robot works. A machine that only follows a fixed sequence without sensing, such as a simple automatic door opener, is usually called automation, and a robot adds sensing, flexibility and decision making.
Robotics is a multidisciplinary field that combines mechanical engineering (structure, joints, gears), electrical and electronic engineering (motors, drivers, power, sensors), computer science (software, perception, planning, learning) and control theory (making motion accurate and stable).

## The main parts of a robot
The mechanical structure is the body: links, joints, wheels or legs, and the end effector, which is the tool at the end of an arm such as a gripper, a welding torch or a suction cup. Actuators produce motion. Sensors give information. A controller, which can be a microcontroller or a small computer, runs the software. A power system, usually batteries for mobile robots, supplies energy, and power is often the limiting factor of a mobile robot. Software ties all of this together, from low-level motor control that runs at hundreds or thousands of times per second to high-level planning that runs a few times per second.

## Types of robots
Industrial manipulators are robot arms in factories that weld, paint, assemble and move parts, and they are fast, strong and very repeatable. Collaborative robots, called cobots, are designed to work next to people, with force limits and safety sensing. Mobile ground robots move on wheels or tracks, for example warehouse robots, robot vacuum cleaners and delivery robots. Legged robots, from four-legged robots to humanoids, can cross uneven terrain and stairs but are harder to build and control. Aerial robots are drones, including quadcopters. Underwater robots are remotely operated or autonomous vehicles used for inspection and research. Soft robots use flexible materials. Swarm robotics studies many simple robots cooperating. Surgical, agricultural, space and rescue robots are examples of application-specific systems.

## Degrees of freedom, joints and workspace
A degree of freedom (DOF) is an independent way the robot can move. A revolute joint rotates and a prismatic joint slides. To place an object at any position and any orientation in 3D space you need at least 6 degrees of freedom, three for position and three for orientation, which is why many industrial arms have six joints. A robot with more than six has redundancy, which allows it to reach the same pose in several ways and to avoid obstacles. A planar arm moving in a plane needs only 3 for position and angle in that plane.
The workspace is the set of positions the end effector can reach. The configuration space is the space of all joint angle combinations, and motion planning for arms is done in it. A mobile robot driving on a floor has 3 degrees of freedom, x, y and heading, but a car-like or differential drive robot cannot move sideways instantly, which is called a nonholonomic constraint.

## Actuators and power
A brushed DC motor is simple and cheap and it is speed-controlled by changing the voltage with PWM (pulse width modulation) through a motor driver such as an H-bridge, which also lets you reverse the direction. A brushless DC motor (BLDC) is more efficient and lasts longer but needs an electronic speed controller. A hobby servo has a motor, gearbox and position feedback in one case and is commanded by a 50 Hz pulse train whose pulse width, normally between 1 ms and 2 ms, sets the angle. A stepper motor moves in fixed steps, 200 steps per revolution is common (1.8 degrees per step), and can be positioned without feedback as long as it does not skip steps, and microstepping gives smoother and finer motion. Linear actuators, hydraulic and pneumatic actuators are used when large forces are needed.
Motors usually spin fast with low torque, so a gearbox trades speed for torque. Output torque is about the motor torque times the gear ratio times the efficiency, and the output speed is the motor speed divided by the ratio. Backlash, the small play between gear teeth, reduces accuracy. Harmonic drives and planetary gearboxes are common in robot arms.
For batteries, lithium polymer cells have a nominal voltage of 3.7 V per cell and are fully charged at 4.2 V, and they must be charged with a proper charger and never over-discharged. Motors draw large current when they start or stall, which can reset the controller if it shares the same supply, so power the motors and the logic carefully, keep a common ground, and add decoupling capacitors.

## Sensors
Proprioceptive sensors measure the robot itself: encoders count wheel or joint rotation, potentiometers measure angle, current sensors estimate motor load. Exteroceptive sensors measure the outside world: ultrasonic and infrared distance sensors, lidar, cameras, force and torque sensors, bumpers, and GPS.
An incremental encoder produces pulses, and a quadrature encoder has two channels that give both the count and the direction, and counting all edges gives four ticks per cycle. An IMU (inertial measurement unit) combines an accelerometer, a gyroscope and sometimes a magnetometer. The gyroscope gives angular velocity, which drifts when integrated over time, and the accelerometer gives the direction of gravity but is noisy when the robot moves. An ultrasonic sensor such as the HC-SR04 measures distance by echo time over roughly 2 cm to 4 m but is affected by soft or angled surfaces. A lidar measures distance with laser light in many directions and is a standard sensor for mapping. Standard GPS is accurate to a few metres outdoors, and RTK GPS can reach centimetres, and GPS does not work indoors. Cameras give rich information but need heavy processing, and depth cameras and stereo cameras add distance.
All sensors have noise, bias and limits, and they need calibration. A robust robot combines several sensors, which is called sensor fusion.

## Control and PID
In open-loop control the command is sent without checking the result. In closed-loop or feedback control the robot measures its output and corrects the error, which is the difference between the target and the measured value. The PID controller is the most widely used feedback controller. Its output is the sum of three terms: the proportional term Kp times the error reacts to the present error, the integral term Ki times the accumulated error removes steady-state error, and the derivative term Kd times the rate of change of the error damps oscillation.
A practical tuning method is manual: set Ki and Kd to zero, raise Kp until the system responds quickly but begins to oscillate, then back off a little, add Kd to reduce overshoot, and add a small Ki only if a steady error remains. Ziegler-Nichols is a classic rule-based method that starts from the gain at which the loop oscillates steadily. The integral term can wind up when the actuator is saturated, so real implementations include anti-windup, which limits the integral. The derivative term amplifies sensor noise, so filter it. Cascade control uses nested loops, for example an outer position loop that commands an inner velocity loop, which commands an inner current loop. The control loop should run at a fixed rate, and the sampling rate must be fast compared with the dynamics. Feedforward adds a predicted command, for example gravity compensation for an arm, so the feedback only corrects the remaining error. Trajectory generation creates smooth motion between points, for example a trapezoidal velocity profile or splines, instead of commanding a sudden jump.

## Kinematics
Forward kinematics computes the position and orientation of the end effector from the joint angles, and it always has one answer. Inverse kinematics does the opposite: it finds the joint angles that place the end effector at a desired pose, and it can have no solution if the target is out of reach, one, several (for example elbow up and elbow down) or infinitely many for redundant robots. Simple arms have analytic solutions, and general ones use numerical methods based on the Jacobian. The Denavit-Hartenberg convention is a standard way to describe the geometry of a serial arm with four parameters per joint.
The Jacobian relates joint velocities to end effector velocity. At a singularity the Jacobian loses rank, the arm loses the ability to move in some direction, and joint speeds required for small end effector motion can become huge. A fully stretched or fully folded arm is the classic example.
For wheeled robots, a differential drive robot has two independently driven wheels, and it turns by running them at different speeds. An Ackermann steering robot is like a car. An omnidirectional robot with mecanum or omni wheels can move sideways. A robot cannot be positioned correctly using kinematics alone if the wheels slip.

## Localisation, mapping and SLAM
Odometry estimates the robot's pose by integrating wheel encoder counts or other motion measurements. Errors accumulate without limit, so the estimate drifts, and wheel slip, uneven wheel diameters and uncertainty about the wheelbase make it worse. To correct drift the robot compares sensor readings with a map or with landmarks.
The Kalman filter combines a motion model and noisy measurements to estimate the state and its uncertainty, and it is optimal for linear systems with Gaussian noise. The extended Kalman filter handles mild non-linearity. The particle filter represents the belief with many samples and handles multi-modal uncertainty, and Monte Carlo localisation (AMCL in ROS) uses it to localise in a known map. An occupancy grid map divides space into cells that are free, occupied or unknown. SLAM (simultaneous localisation and mapping) builds a map while estimating the robot's pose in it, and uses loop closure, which recognises a revisited place and corrects accumulated drift. Common approaches are filter-based, graph-based and visual or lidar SLAM.

## Planning
Path planning finds a collision-free route from a start to a goal. Graph search methods such as Dijkstra's algorithm and A* work on grids or roadmaps. A* adds a heuristic estimate of the remaining distance to guide the search, and it finds an optimal path when the heuristic never overestimates the true cost. Sampling-based planners such as PRM and RRT (rapidly-exploring random tree) work well in high-dimensional spaces like a robot arm's configuration space, but the paths are not optimal, and RRT* improves them. Potential field methods treat the goal as attractive and obstacles as repulsive, which is simple but can get stuck in local minima. A local planner such as the dynamic window approach avoids obstacles in real time while following the global path.
For arms, motion planning must also check collisions between all links and the environment, and MoveIt is the common ROS framework. Trajectory optimisation can add smoothness and torque limits. At the task level, finite state machines and behaviour trees organise what the robot does, for example search, grasp, carry and place.

## Perception and learning
Computer vision gives robots object detection, segmentation, pose estimation and visual odometry, and OpenCV is the standard library. Deep learning models such as convolutional networks and transformers detect objects and understand scenes. Point clouds from lidar or depth cameras are processed with libraries such as PCL and Open3D. Robot learning includes imitation learning, where the robot learns from demonstrations, and reinforcement learning, which is usually trained in simulation and then transferred to the real robot, which is called sim-to-real, and domain randomisation, which varies simulation parameters, helps close the gap between them. Large vision-language and vision-language-action models are an active research area for giving robots general instructions, and they are not yet as reliable as classic control for safety-critical work. A practical robot normally combines classic control and planning with learned perception.

## Software: ROS 2
The Robot Operating System (ROS) is not an operating system but a framework and a set of tools and libraries for robot software. ROS 2 is the current generation. Its main concepts are nodes (separate programs), topics (publish and subscribe data streams, such as sensor data), services (request and reply), actions (long-running tasks with feedback and cancellation, such as navigate to a goal), and parameters (configuration). Launch files start many nodes together. The tf2 library tracks coordinate frames and the transforms between them, for example from the map to the base of the robot to the camera. URDF describes a robot's links and joints, rviz2 visualises data, and rosbag2 records and replays data. ROS 2 uses DDS middleware for communication with configurable quality of service, and ros2_control, Nav2 (navigation) and MoveIt 2 (manipulation) are major packages. micro-ROS brings ROS 2 to microcontrollers.
ROS 2 releases come every year on May 23, alternating between long-term support releases in even years and shorter releases in odd years. At the time of writing, Lyrical Luth (released in May 2026) is the newest long-term support release and is supported until May 2031. Jazzy Jalisco (May 2024) is a long-term support release supported until May 2029, and Kilted Kaiju (May 2025) is supported until December 2026. ROS 1 reached end of life in May 2025 with Noetic, so new projects should use ROS 2. Distribution names and dates change every year, so always check docs.ros.org for the current list, and use the distribution that matches your Ubuntu version.
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__("talker")
        self.pub = self.create_publisher(String, "chatter", 10)
        self.timer = self.create_timer(0.5, self.tick)
        self.count = 0

    def tick(self):
        msg = String()
        msg.data = f"hello {self.count}"
        self.pub.publish(msg)
        self.count += 1

def main():
    rclpy.init()
    rclpy.spin(Talker())
    rclpy.shutdown()

if __name__ == "__main__":
    main()
```
This minimal node publishes a message on the topic chatter twice per second. Useful commands are colcon build to build a workspace, source install/setup.bash to activate it, ros2 run package executable to start a node, ros2 topic list and ros2 topic echo /chatter to inspect data, ros2 node list, and ros2 launch to start a launch file.

## Simulation
Simulation lets you test code safely and cheaply before using real hardware. Gazebo is the standard simulator for ROS. Webots is an open-source simulator that is easy to start with. MuJoCo and PyBullet are physics engines that are popular for control and reinforcement learning research, and NVIDIA Isaac Sim is a GPU-based robotics simulator. A simulator is never exactly the real world, so test on hardware early and expect differences in friction, delays and sensor noise.

## Hardware for students and makers
An Arduino board with an ATmega328 microcontroller runs one program in real time, uses 5 V logic, has a 10-bit analogue-to-digital converter that returns values from 0 to 1023, and has PWM pins, and it is ideal for motors and sensors. An ESP32 runs at 3.3 V and has Wi-Fi and Bluetooth. A Raspberry Pi is a small Linux computer that can run ROS 2, cameras and Python, and an NVIDIA Jetson adds a GPU for vision and neural networks. A common design is a small computer for high-level tasks connected to a microcontroller for real-time motor control. The common communication buses are UART (serial), I2C (two wires, many devices with different addresses), SPI (faster, with a select line for each device) and CAN (robust, used in vehicles and industrial robots). Do not connect a 5 V signal to a 3.3 V input without level shifting.
```cpp
#include <Servo.h>
Servo s;
void setup() { s.attach(9); }
void loop() {
  s.write(0);   delay(1000);
  s.write(90);  delay(1000);
  s.write(180); delay(1000);
}
```
This Arduino program moves a hobby servo connected to pin 9 between 0, 90 and 180 degrees. Power a servo or motor from a separate supply, not from the board's 5 V pin, connect the grounds together, and use flyback diodes across motor coils.

## Safety, standards and ethics
Every robot that can hurt people needs an emergency stop, and a risk assessment before it is used. ISO 10218 covers the safety of industrial robots, and ISO/TS 15066 covers collaborative robots, with methods such as safety-rated monitored stop, hand guiding, speed and separation monitoring, and power and force limiting. Lithium batteries can catch fire if damaged or overcharged. Test new code with the wheels off the ground or with limited speed and torque. Ethical questions include job changes, privacy from cameras and microphones, bias in perception systems, accountability when a robot causes harm, and the debate on autonomous weapons. Isaac Asimov's three laws of robotics are a fictional device and not an engineering standard.

## How to build your first robot project
Choose a small goal such as a line-following robot, an obstacle-avoiding car, or a two-joint arm. List the requirements, then choose a chassis, motors with encoders, a motor driver, a microcontroller, sensors and a battery that supplies enough current. Test each part separately: spin each motor, read each sensor, and print values. Then write the control loop, start with simple behaviour and add complexity step by step, log data, and tune parameters. Simulate first if you can. Document your work with photos, a wiring diagram and code in a repository.
Good competitions for students include FIRST Robotics Competition, FIRST Tech Challenge and FIRST LEGO League, VEX Robotics, RoboCup, the World Robot Olympiad, and the RoboMaster challenge, and many universities run rover and drone contests.

<!-- id: robotics_math_and_code; topics: robotics -->
# Robotics Mathematics and Algorithms With Working Code

## About these examples
All the code in this note was run, and the numbers shown are the real outputs. It uses NumPy only, so you can run it without a robot or a simulator. The blocks continue each other, so later blocks reuse np and the functions defined earlier.

## Forward and inverse kinematics of a 2-link planar arm
Consider an arm with two links in a plane, link lengths l1 and l2, and joint angles q1 and q2. The forward kinematics of the end effector are x = l1 cos q1 + l2 cos(q1 + q2) and y = l1 sin q1 + l2 sin(q1 + q2). For inverse kinematics we first find the cosine of the elbow angle with the law of cosines: cos q2 = (x squared + y squared - l1 squared - l2 squared) divided by (2 l1 l2). If the absolute value of this number is greater than 1, the target is out of reach, because the farthest reach is l1 + l2 and the nearest is the absolute value of l1 - l2. Otherwise q2 is plus or minus arccos of it, which are the two solutions called elbow up and elbow down, and q1 is the angle of the target minus the angle that the second link contributes.
```python
import numpy as np

def fk(q1, q2, l1=1.0, l2=0.8):
    x = l1 * np.cos(q1) + l2 * np.cos(q1 + q2)
    y = l1 * np.sin(q1) + l2 * np.sin(q1 + q2)
    return x, y

def ik(x, y, l1=1.0, l2=0.8, elbow_up=True):
    c2 = (x**2 + y**2 - l1**2 - l2**2) / (2 * l1 * l2)
    if abs(c2) > 1:
        return None
    q2 = np.arccos(c2) if elbow_up else -np.arccos(c2)
    q1 = np.arctan2(y, x) - np.arctan2(l2 * np.sin(q2), l1 + l2 * np.cos(q2))
    return q1, q2

q = ik(1.2, 0.9)
print(np.round(q, 4), np.round(fk(*q), 4))
print(ik(3.0, 0.0))
```
For the target (1.2, 0.9) with l1 = 1.0 and l2 = 0.8 the solution is q1 = 0.1279 rad and q2 = 1.1796 rad, and the forward kinematics of this solution return (1.2, 0.9), which confirms the answer. The target (3.0, 0.0) is farther than the maximum reach of 1.8, so ik returns None.

## The Jacobian and singularities
The Jacobian maps joint velocities to end effector velocity. For this arm the determinant of the Jacobian equals l1 times l2 times sin q2, so it becomes zero when q2 is 0 (arm fully stretched) or pi (arm folded back). These are the singular configurations, where the arm cannot move its end effector along the direction of the arm, and inverse velocity control would demand infinite joint speed.
```python
def jacobian(q1, q2, l1=1.0, l2=0.8):
    return np.array([[-l1*np.sin(q1) - l2*np.sin(q1+q2), -l2*np.sin(q1+q2)],
                     [ l1*np.cos(q1) + l2*np.cos(q1+q2),  l2*np.cos(q1+q2)]])

for q2 in (0.0, 0.5, np.pi/2, np.pi):
    print(round(q2, 2), round(np.linalg.det(jacobian(0.3, q2)), 4))
```
The determinants are 0.0 at q2 = 0, 0.3835 at q2 = 0.5, 0.8 at q2 = pi/2 (the best-conditioned pose) and 0.0 at q2 = pi. The value does not depend on q1.

## Coordinate frames and homogeneous transforms
A 2D homogeneous transform combines a rotation by angle theta and a translation (x, y) in a 3 by 3 matrix. Multiplying it by a point written as (px, py, 1) converts the point from the robot frame to the world frame, and chaining frames is a matrix product.
```python
def T(theta, x, y):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, x], [s, c, y], [0, 0, 1]])

world_robot = T(np.pi / 2, 2.0, 1.0)
point_in_robot = np.array([1.0, 0.0, 1.0])
print(np.round(world_robot @ point_in_robot, 3))
```
A robot located at (2, 1) in the world and facing 90 degrees (up the y axis) sees an obstacle 1 m straight ahead. In the world frame that point is at (2, 2), and the code prints [2. 2. 1.]. The tf2 library of ROS manages exactly these transforms in 3D.

## PID control: a worked simulation
The plant is a unit mass that moves along a line with friction 0.5, the target is position 1.0, and the controller runs at 100 Hz for 10 seconds.
```python
def simulate(kp, ki, kd, target=1.0, dt=0.01, T_end=10.0, friction=0.5):
    x = v = integ = 0.0
    prev_err = target - x
    xs = []
    for _ in range(int(T_end / dt)):
        err = target - x
        integ += err * dt
        deriv = (err - prev_err) / dt
        u = kp * err + ki * integ + kd * deriv
        prev_err = err
        a = u - friction * v
        v += a * dt
        x += v * dt
        xs.append(x)
    return np.array(xs)

for name, g in [("P", (4, 0, 0)), ("PD", (4, 0, 3)), ("PID", (4, 1, 3))]:
    xs = simulate(*g)
    print(name, round(xs[-1], 3), round(max(0, (xs.max() - 1.0) * 100), 1))
```
With the proportional term alone (Kp = 4) the mass overshoots by 67 percent and is still oscillating after 10 seconds, because friction is small and nothing damps the motion. Adding the derivative term (Kd = 3) removes almost all oscillation: the overshoot is only 0.3 percent and the final position is 1.0. Adding the integral term (Ki = 1) gives an overshoot of 17.5 percent. The integral term is not useful here, but it matters when a constant disturbance acts, such as gravity or a steady push.
```python
def sim_dist(kp, ki, kd, dist=-0.5, dt=0.01):
    x = v = integ = 0.0
    prev = 1.0
    for _ in range(1000):
        err = 1.0 - x
        integ += err * dt
        d = (err - prev) / dt
        prev = err
        u = kp * err + ki * integ + kd * d
        a = u + dist - 0.5 * v
        v += a * dt
        x += v * dt
    return x

print(round(sim_dist(4, 0, 3), 3), round(sim_dist(4, 1, 3), 3))
```
With a constant disturbing force of -0.5, the PD controller settles at 0.875, so it has a steady-state error of 0.125, which is the disturbance divided by Kp (0.5 / 4). The PID controller reaches about 1.01, because the integral term keeps growing until the error vanishes. This is why the integral term is used: it removes steady-state error.

## Differential drive kinematics and odometry
For a differential drive robot with left and right wheel speeds vl and vr and wheel base L, the forward speed is v = (vl + vr) / 2 and the turning rate is w = (vr - vl) / L. If the speeds are different and constant, the robot drives on a circle of radius R = (L / 2) times (vr + vl) / (vr - vl). Odometry integrates these equations over time.
```python
def step(pose, vl, vr, wheel_base, dt):
    x, y, th = pose
    v = (vl + vr) / 2
    w = (vr - vl) / wheel_base
    return (x + v * np.cos(th) * dt, y + v * np.sin(th) * dt, th + w * dt)

pose = (0.0, 0.0, 0.0)
for _ in range(1000):
    pose = step(pose, 0.2, 0.3, 0.3, 0.01)
print(np.round(pose, 3))

pose = (0.0, 0.0, 0.0)
for _ in range(10000):
    pose = step(pose, 0.5, 0.505, 0.3, 0.01)
print(np.round(pose, 2))
```
With vl = 0.2 m/s, vr = 0.3 m/s and L = 0.3 m, the turning rate is 0.333 rad/s, the radius is 0.75 m and a full circle takes 18.85 s. After 10 s the pose is x = -0.14, y = 1.486, heading 3.333 rad. The second run shows why odometry drifts: the robot is commanded to go straight at 0.5 m/s, but the right wheel is just 1 percent faster. After 100 s the heading has turned by 1.67 rad (about 96 degrees) and the robot is at (30.0, 33.0) m instead of (50, 0) m. A tiny wheel mismatch causes a huge position error, which is why robots correct odometry with gyroscopes, lidar, cameras or GPS.
Converting encoder ticks to distance: a 600 counts-per-revolution encoder in quadrature mode gives 2400 ticks per revolution, and for wheels with radius 0.05 m each tick is 2 pi times 0.05 divided by 2400, about 0.131 mm. Wheel speed in m/s equals 2 pi times radius times revolutions per second, so one revolution per second gives 0.314 m/s for this wheel.

## A* path planning on a grid
A* keeps a priority queue of cells ordered by cost so far plus a heuristic estimate of the cost to the goal. With 4-connected moves the Manhattan distance is a heuristic that never overestimates, so A* returns a shortest path.
```python
import heapq

def astar(grid, start, goal):
    h = lambda a: abs(a[0] - goal[0]) + abs(a[1] - goal[1])
    open_set = [(h(start), 0, start)]
    came, g = {}, {start: 0}
    while open_set:
        _, cost, cur = heapq.heappop(open_set)
        if cur == goal:
            path = [cur]
            while cur in came:
                cur = came[cur]
                path.append(cur)
            return path[::-1]
        if cost > g[cur]:
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cur[0] + dr, cur[1] + dc)
            if 0 <= n[0] < len(grid) and 0 <= n[1] < len(grid[0]) and grid[n[0]][n[1]] == 0:
                ng = cost + 1
                if ng < g.get(n, 1e9):
                    g[n] = ng
                    came[n] = cur
                    heapq.heappush(open_set, (ng + h(n), ng, n))
    return None

grid = [[0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0]]
p = astar(grid, (0, 0), (4, 4))
print(len(p) - 1, p)
print(astar([[0, 1], [1, 0]], (0, 0), (1, 1)))
```
In this 5 by 5 grid, where 1 means an obstacle, the walls force a snake-shaped route, and A* finds a path of 16 moves: right along the top row, down the right side, left along the middle row, down the left side, and right along the bottom row. When the goal is completely blocked, as in the second grid, the function returns None. With a heuristic of zero A* becomes Dijkstra's algorithm, and it explores more cells.

## One-dimensional Kalman filter
A Kalman filter estimates a state from noisy measurements. In the simplest case of a constant value, each new measurement z updates the estimate x by a gain K: K = P / (P + R), x = x + K (z - x), P = (1 - K) P, where P is the variance of the estimate and R is the variance of the sensor noise. The gain is large when the estimate is uncertain and small when it is confident.
```python
rng = np.random.default_rng(0)
true = 5.0
meas = true + rng.normal(0, 1.0, 20)
x, P, Rn = 0.0, 100.0, 1.0
for z in meas:
    K = P / (P + Rn)
    x = x + K * (z - x)
    P = (1 - K) * P
print(round(x, 3), round(P, 4), round(meas.mean(), 3))
```
Starting from a very uncertain guess of 0 (variance 100), 20 measurements with noise standard deviation 1 give an estimate of 4.814 for a true value of 5.0, and the variance of the estimate falls from 100 to 0.05, so its standard deviation is about 0.22 instead of 1. The estimate is close to the plain average of the measurements (4.817), because for a constant value the Kalman filter is a running average. The difference from 5.0 is within the expected uncertainty. For moving robots the filter adds a prediction step with a motion model, and the extended Kalman filter handles non-linear models.

## Lidar scan to points and gearbox arithmetic
A lidar returns a range at each angle. Converting polar coordinates to Cartesian points in the sensor frame is x = r cos(angle) and y = r sin(angle).
```python
ranges = np.array([1.0, 2.0, 1.5])
angles = np.radians([0, 90, 180])
pts = np.c_[ranges * np.cos(angles), ranges * np.sin(angles)]
print(np.round(pts, 3).tolist())
```
The result is [[1.0, 0.0], [0.0, 2.0], [-1.5, 0.0]], which are points 1 m ahead, 2 m to the left and 1.5 m behind.
For a gearbox, a motor that delivers 0.1 N·m at 3000 rpm connected through a 50 to 1 gearbox with 80 percent efficiency gives an output torque of 0.1 times 50 times 0.8 = 4.0 N·m at 3000 / 50 = 60 rpm. Gearing trades speed for torque, and the efficiency losses reduce the torque.

<!-- id: robotics_qa; topics: robotics -->
# Robotics: Frequently Asked Questions

## What is the difference between forward kinematics and inverse kinematics?
Forward kinematics computes where the end effector is, given the joint angles, and it has exactly one answer. Inverse kinematics finds the joint angles needed to put the end effector at a desired position and orientation, and it can have no solution when the target is out of reach, several solutions such as elbow up and elbow down, or infinitely many for redundant arms. Inverse kinematics is harder and is solved analytically for simple arms and numerically with the Jacobian for general ones.

## What are degrees of freedom in a robot arm?
Degrees of freedom are the number of independent joints or motions, each one an independent way the robot can move. To place the end effector at any position and orientation in 3D space a robot needs 6 degrees of freedom, so most industrial arms have 6 joints. An arm with more than 6 is redundant, and an arm with fewer than 6 cannot reach every pose.

## What is a singularity in a robot arm?
A singularity is a configuration where the Jacobian loses rank, so the arm cannot move its end effector in some direction and the joint speeds needed for small motions become very large. For a two-link arm the determinant of the Jacobian is proportional to the sine of the elbow angle, so the singular poses are the fully stretched and the fully folded arm. Planners and controllers avoid singularities or slow down near them.

## How do I tune a PID controller?
Set Ki and Kd to zero. Increase Kp until the system responds quickly but starts to oscillate, then reduce it a little. Add Kd to reduce overshoot and oscillation. Add a small Ki only if a steady error remains, for example under a constant load such as gravity. The Ziegler-Nichols method is a rule-based alternative. Use anti-windup to limit the integral when the actuator saturates, and filter the derivative term because it amplifies noise.

## What is the difference between a servo motor, a stepper motor and a DC motor?
A DC motor spins continuously at a speed that depends on the voltage, and it needs an encoder to know its position. A hobby servo contains a motor, gearbox and position sensor, and you command an angle with a pulse of 1 to 2 ms repeated at 50 Hz. A stepper motor moves in fixed steps, typically 200 per revolution, and can be positioned without feedback if it does not skip steps, but it has lower torque at high speed and gets hot. Choose a servo for simple angle control, a stepper for open-loop precise positioning such as 3D printers, and a DC or brushless motor with an encoder for wheels and high speed.

## Why does wheel odometry drift?
Odometry integrates small errors in every step, and the errors never cancel. Wheel slip, unequal wheel diameters, an inaccurate wheelbase and encoder resolution all contribute. A 1 percent speed mismatch between two wheels, for example, can turn a straight 50 m path into a curve that ends tens of metres from the goal. Drift is reduced by fusing odometry with an IMU, and corrected by matching lidar or camera data to a map, GPS, or SLAM.

## What is SLAM?
SLAM stands for simultaneous localisation and mapping. The robot builds a map of an unknown environment while estimating its own position in that map, using sensors such as lidar, cameras and wheel odometry. It is difficult because the map needs the position and the position needs the map. Loop closure, recognising a place visited before, corrects accumulated drift. Popular approaches are filter-based, graph-based, and visual or lidar SLAM, and ROS 2 packages such as slam_toolbox provide ready implementations.

## How does A* path planning work?
A* searches a graph or grid and expands the cell with the lowest estimated total cost, which is the cost from the start so far plus a heuristic estimate of the remaining cost to the goal. If the heuristic never overestimates the true cost, such as the straight-line or Manhattan distance, A* is guaranteed to return an optimal path and usually explores far fewer cells than Dijkstra's algorithm. It needs a discretised map, and for high-dimensional spaces such as robot arms, sampling-based planners such as RRT are used instead.

## What is the difference between RRT and A*?
A* searches over a discretised grid or graph and returns an optimal path, but the number of cells grows exponentially with the dimensions, so it is not practical for a six-joint arm. RRT builds a tree by randomly sampling the configuration space and connecting samples to the nearest tree node, so it works in high dimensions and finds a feasible path quickly, but the path is jagged and not optimal, and RRT* improves it over time.

## What is ROS 2 and which version should I use?
ROS 2 is a framework with libraries and tools for robot software, based on nodes that exchange data through topics, services and actions. For a new project use the newest long-term support release that supports your operating system. At the time of writing, Lyrical Luth (May 2026) is the newest long-term support release and it is supported until May 2031, Jazzy Jalisco is supported until May 2029, and ROS 1 ended in May 2025. Check docs.ros.org for the current list, because a new release comes every May.

## What is the difference between a topic, a service and an action in ROS 2?
A topic is a continuous publish and subscribe stream, such as camera images or velocity commands, with many publishers and subscribers possible. A service is a request and reply for a quick one-time operation, such as asking a node to reset. An action is for long-running tasks with feedback and the ability to cancel, such as navigating to a goal position.

## Which sensors do I need for an autonomous mobile robot?
A minimal robot needs wheel encoders for odometry and a distance sensor such as ultrasonic or infrared for obstacle avoidance. A more capable one adds an IMU, a 2D lidar for mapping and localisation, and a camera for recognising objects. Outdoors, add GPS, and RTK GPS for centimetre accuracy. Combine sensors with a filter because every sensor has noise and failure modes.

## Should I use an Arduino or a Raspberry Pi?
An Arduino is a microcontroller that runs your code in real time with precise timing, so it is best for reading sensors, generating PWM and controlling motors. A Raspberry Pi is a small Linux computer that runs ROS 2, vision and Python, but it is not a real-time device. Many robots use both: the Pi for high-level decisions and the Arduino or another microcontroller for motor control, connected by USB serial or I2C.

## What is an IMU and what is it used for?
An inertial measurement unit contains an accelerometer, a gyroscope and often a magnetometer. It measures acceleration, rotation rate and magnetic heading, and it is used to estimate the orientation of a robot, to stabilise drones and balancing robots, and to improve odometry. A gyroscope drifts over time and an accelerometer is noisy during motion, so they are combined with a complementary or Kalman filter.

## What is the difference between a robot arm and a mobile robot in terms of control?
A robot arm is fixed to its base, so its position is determined by joint angles that can be measured accurately, and the main problems are kinematics, dynamics and collision-free motion. A mobile robot moves in the world, and its position must be estimated because wheel slip and drift make it uncertain, so the main problems are localisation, mapping and navigation. A mobile manipulator, which is an arm on a mobile base, combines both.

## What is a Kalman filter used for in robotics?
A Kalman filter combines a prediction from a motion model with noisy sensor measurements to estimate the state, such as position and velocity, together with its uncertainty. It is used for sensor fusion of IMU, GPS and odometry, for tracking objects, and in localisation. It is optimal for linear systems with Gaussian noise, and the extended Kalman filter handles mildly non-linear systems.

## How can I make my robot safe?
Add an emergency stop that cuts power to the motors, limit speed and torque, test with the wheels lifted off the ground, keep people out of the working area, and do a risk assessment. For arms that work near people use collaborative robot safety methods such as force limiting and speed and separation monitoring, as described in ISO/TS 15066. Handle lithium batteries carefully with a proper charger and protection circuit.

## How is machine learning used in robotics?
Learning is mostly used in perception, such as detecting objects, segmenting images and estimating pose, and increasingly in control. Imitation learning teaches a robot from human demonstrations. Reinforcement learning trains policies in simulation and transfers them to real robots, which is called sim-to-real, and randomising the simulation parameters helps the policy cope with the real world. Classic control and planning remain important for safety and reliability, and many robots combine both.

## How do I start learning robotics?
Learn basic programming in Python and C++, and electronics basics with an Arduino. Build a simple robot such as a line follower or obstacle-avoiding car. Learn the mathematics of kinematics and control with free resources such as the Modern Robotics course. Then learn ROS 2 and a simulator such as Gazebo, build a mobile robot with navigation, and join a competition such as FIRST, VEX or RoboCup.

<!-- id: robotics_qa_ar; topics: robotics -->
# أسئلة وأجوبة وقاموس مصطلحات في الروبوتات

## ما هو الروبوت (robot)؟
الروبوت آلة تستشعر بيئتها وتتخذ قرارات وتؤثر في العالم المادي بتحكم حاسوبي. حلقة العمل المعتادة هي: استشعار (sense)، ثم تفكير (think)، ثم فعل (act). الحساسات (sensors) تقيس، والبرمجيات تقرر، والمشغِّلات (actuators) مثل المحركات تحرك. الآلة التي تنفذ تسلسلاً ثابتاً بلا استشعار تسمى أتمتة، والروبوت يضيف الاستشعار والمرونة واتخاذ القرار.

## ما هي درجات الحرية (degrees of freedom) في الذراع الروبوتية؟
هي عدد الحركات المستقلة، أي عدد المفاصل المستقلة. لوضع الأداة النهائية (end effector) في أي موضع واتجاه في الفضاء ثلاثي الأبعاد تحتاج 6 درجات حرية، لذلك لمعظم الأذرع الصناعية 6 مفاصل. الذراع التي لها أكثر من 6 تسمى زائدة (redundant) ويمكنها بلوغ نفس الوضع بعدة طرق، والتي لها أقل من 6 لا تستطيع بلوغ كل الأوضاع.

## ما الفرق بين الحركيات الأمامية والعكسية (forward و inverse kinematics)؟
الحركيات الأمامية تحسب موضع الأداة النهائية من زوايا المفاصل، ولها جواب واحد دائماً. أما الحركيات العكسية فتجد زوايا المفاصل اللازمة لوضع الأداة في موضع مطلوب، وقد لا يكون لها حل إذا كان الهدف خارج المدى، أو يكون لها عدة حلول مثل المرفق للأعلى والمرفق للأسفل. وهي أصعب وتُحل تحليلياً للأذرع البسيطة وعددياً باستخدام مصفوفة جاكوبيان (Jacobian) للأذرع العامة.

## ما هي نقطة التفرد (singularity) في الذراع الروبوتية؟
هي وضع تفقد فيه مصفوفة جاكوبيان رتبتها، فلا تستطيع الذراع تحريك أداتها في اتجاه معين، وتصبح سرعات المفاصل المطلوبة لحركات صغيرة ضخمة جداً. في ذراع بوصلتين يكون محدد الجاكوبيان متناسباً مع جيب زاوية المرفق، فنقطتا التفرد هما الذراع ممدودة تماماً أو مطوية تماماً.

## ما هو متحكم PID وكيف أضبطه؟
المتحكم PID يجمع ثلاثة حدود: التناسبي (P) يستجيب للخطأ الحالي، والتكاملي (I) يزيل الخطأ المستقر (steady-state error)، والتفاضلي (D) يخمد التذبذب. للضبط: اجعل Ki وKd صفراً، ارفع Kp حتى تصبح الاستجابة سريعة ثم يبدأ تذبذب بسيط وأرجعها قليلاً، ثم أضف Kd لتقليل التجاوز (overshoot)، ثم أضف Ki صغيراً إذا بقي خطأ ثابت مثل حمل الجاذبية. استخدم anti-windup لحد التكامل، وصفِّ الحد التفاضلي لأنه يضخم الضجيج.

## ما الفرق بين محرك servo ومحرك stepper ومحرك DC؟
محرك DC يدور بسرعة تعتمد على الجهد ويحتاج مشفراً (encoder) ليعرف موضعه. محرك servo الهواة يضم محركاً وعلبة تروس وحساس موضع، وتعطيه زاوية بنبضة عرضها 1 إلى 2 ميلي ثانية تتكرر 50 مرة بالثانية. أما محرك stepper فيتحرك بخطوات ثابتة، غالباً 200 خطوة للدورة، ويمكن تحديد موضعه بدون تغذية راجعة إذا لم يفقد خطوات، لكن عزمه ينخفض عند السرعة العالية. استخدم servo لزاوية بسيطة، وstepper للتموضع الدقيق بدون تغذية راجعة مثل الطابعات ثلاثية الأبعاد، وDC مع encoder للعجلات.

## لماذا ينحرف قياس المسافة بالعجلات (odometry drift)؟
لأن الـ odometry يجمع أخطاء صغيرة في كل خطوة ولا تتلاشى. انزلاق العجلات واختلاف أقطارها وعدم دقة المسافة بين العجلتين كلها تسهم. فارق 1% بين سرعتي عجلتين قد يحوّل مساراً مستقيماً طوله 50 متراً إلى منحنى ينتهي بعيداً عن الهدف بعشرات الأمتار. يُخفَّف الانحراف بدمجه مع IMU، ويُصحَّح بمطابقة بيانات الليدار أو الكاميرا مع خريطة، أو بـ GPS أو SLAM.

## ما هو SLAM؟
هو التحديد المتزامن للموقع وبناء الخريطة (simultaneous localization and mapping). يبني الروبوت خريطة لبيئة مجهولة ويقدّر موقعه فيها في الوقت نفسه، باستخدام ليدار (LiDAR) أو كاميرات أو odometry. الصعوبة أن الخريطة تحتاج الموقع والموقع يحتاج الخريطة. وإغلاق الحلقة (loop closure)، أي التعرف على مكان زاره الروبوت سابقاً، يصحح الانحراف المتراكم. وفي ROS 2 توجد حزم جاهزة مثل slam_toolbox.

## كيف تعمل خوارزمية A* لتخطيط المسار؟
تبحث A* في شبكة أو رسم بياني وتوسّع الخلية ذات أقل كلفة كلية مقدّرة، وهي الكلفة منذ البداية زائد تقدير تقريبي (heuristic) للكلفة المتبقية إلى الهدف. إذا كان التقدير لا يبالغ في الكلفة الحقيقية، مثل المسافة المستقيمة أو مسافة مانهاتن، فإنها تضمن إيجاد المسار الأمثل وتفحص خلايا أقل بكثير من خوارزمية Dijkstra. وللفضاءات عالية الأبعاد مثل ذراع بستة مفاصل تُستخدم مخططات قائمة على العينات مثل RRT.

## ما هو ROS 2 وأي نسخة أستخدم؟
ROS 2 إطار عمل ومكتبات وأدوات لبرمجيات الروبوت، يقوم على عُقد (nodes) تتبادل البيانات عبر المواضيع (topics) والخدمات (services) والإجراءات (actions). استخدم أحدث نسخة دعم طويل (LTS) تدعم نظام تشغيلك. وقت كتابة هذه المعلومات، النسخة Lyrical Luth (مايو 2026) هي أحدث نسخة دعم طويل ويستمر دعمها حتى مايو 2031، ونسخة Jazzy Jalisco مدعومة حتى مايو 2029، أما ROS 1 فانتهى دعمه في مايو 2025. تحقق من docs.ros.org لأن إصداراً جديداً يصدر كل مايو.

## كيف أبدأ بتعلم الروبوتات؟
تعلم البرمجة بـ Python وC++، وأساسيات الإلكترونيات مع لوحة Arduino. ابنِ روبوتاً بسيطاً مثل متتبع الخط أو سيارة تتجنب العوائق. تعلم رياضيات الحركيات والتحكم من مصادر مجانية مثل دورة Modern Robotics. ثم تعلم ROS 2 ومحاكياً مثل Gazebo، وابنِ روبوتاً متحركاً بالملاحة، وشارك في مسابقة مثل FIRST أو VEX أو RoboCup.

## هل أستخدم Arduino أم Raspberry Pi؟
لوحة Arduino متحكم دقيق يشغّل الكود في الزمن الحقيقي بتوقيت دقيق، فهي الأفضل لقراءة الحساسات وتوليد PWM والتحكم بالمحركات. أما Raspberry Pi فحاسوب صغير بنظام لينكس يشغّل ROS 2 والرؤية الحاسوبية وPython، لكنه ليس جهازاً للزمن الحقيقي الصارم. كثير من الروبوتات تستخدم الاثنين: الـ Pi للقرارات العليا والـ Arduino للتحكم بالمحركات، ويتصلان عبر USB أو I2C.

## ما هي الحساسات التي يحتاجها روبوت متحرك ذاتي القيادة؟
الحد الأدنى هو مشفرات (encoders) على العجلات لقياس المسافة، وحساس مسافة مثل الموجات فوق الصوتية (ultrasonic) أو الأشعة تحت الحمراء لتجنب العوائق. وللأفضل أضف وحدة قياس القصور الذاتي IMU وليدار ثنائي الأبعاد للخرائط وتحديد الموقع وكاميرا للتعرف على الأشياء. وفي الخارج أضف GPS، وRTK GPS لدقة بالسنتيمترات. ادمج الحساسات بمرشح لأن لكل حساس ضجيجاً وحالات فشل.

## ما هو مرشح كالمان (Kalman filter) وفيم يُستخدم؟
هو خوارزمية تجمع تنبؤاً من نموذج حركة مع قياسات حساسات مشوشة لتقدير الحالة، مثل الموضع والسرعة، مع عدم اليقين فيها. يُستخدم لدمج IMU وGPS وodometry، ولتتبع الأجسام، وفي تحديد الموقع. وهو الأمثل للأنظمة الخطية بضجيج غاوسي، والنسخة الممتدة (EKF) تتعامل مع اللاخطية البسيطة.

## ما هي مسابقات الروبوتات المناسبة للطلاب؟
FIRST Robotics Competition وFIRST Tech Challenge وFIRST LEGO League، وVEX Robotics، وRoboCup، وWorld Robot Olympiad (WRO)، وRoboMaster. وكثير من الجامعات تنظم مسابقات للمركبات الجوالة والطائرات المسيّرة.

## كيف أجعل الروبوت آمناً؟
أضف زر إيقاف طوارئ يقطع الطاقة عن المحركات، وحدّد السرعة والعزم، واختبر والعجلات مرفوعة عن الأرض، وأبعد الأشخاص عن منطقة العمل، وأجرِ تقييم مخاطر. وللأذرع التي تعمل قرب البشر استخدم أساليب الروبوتات التعاونية مثل تحديد القوة ومراقبة السرعة والمسافة وفق ISO/TS 15066. وتعامل مع بطاريات الليثيوم بحذر باستخدام شاحن مناسب ودائرة حماية.

## قاموس مصطلحات الروبوتات
الروبوت (robot)، الحساس (sensor)، المشغِّل (actuator)، المتحكم الدقيق (microcontroller) مثل Arduino، الحاسوب أحادي اللوحة (single-board computer) مثل Raspberry Pi، المفصل (joint)، الوصلة (link)، الذراع الروبوتية (robot arm)، الأداة النهائية (end effector)، القابض (gripper)، درجات الحرية (degrees of freedom)، فضاء العمل (workspace)، الحركيات الأمامية (forward kinematics)، الحركيات العكسية (inverse kinematics)، مصفوفة جاكوبيان (Jacobian)، نقطة التفرد (singularity)، التحكم PID، المتحكم المتناسب التكاملي التفاضلي، محرك التيار المستمر (DC motor)، المحرك المؤازر (servo)، المحرك الخطوي (stepper)، علبة التروس (gearbox)، العزم (torque)، المشفر (encoder)، وحدة القياس بالقصور الذاتي (IMU)، الليدار (LiDAR) حساس مسافة بالليزر، الموجات فوق الصوتية (ultrasonic)، تقدير الموقع بالعجلات (odometry)، الدمج بين الحساسات (sensor fusion)، مرشح كالمان (Kalman filter)، مرشح الجسيمات (particle filter)، خريطة الإشغال (occupancy grid)، التحديد المتزامن للموقع وبناء الخريطة (SLAM)، تخطيط المسار (path planning)، تخطيط الحركة (motion planning)، تجنب العوائق (obstacle avoidance)، عُقدة (node) وموضوع (topic) في ROS، المحاكاة (simulation)، التعلم بالتقليد (imitation learning)، والانتقال من المحاكاة إلى الواقع (sim-to-real).

<!-- id: robotics_books_resources; topics: robotics -->
# Books, Courses and References for Robotics

## How to use this list
This list was written from general knowledge, not from an official ranking. Editions and availability change, so check the newest edition and whether a free version is available. Read one practical book and one theory book together, and build a project while reading. Resources marked free were available to read online at the time of writing.

## Core robotics textbooks
Modern Robotics: Mechanics, Planning, and Control by Kevin Lynch and Frank Park is a modern textbook on kinematics, dynamics, planning and control with a unified geometric approach. A free preprint and videos are available from the authors' site, and a matching Coursera specialization from Northwestern University teaches it, so it is the best starting point for a self-learner with some mathematics. Introduction to Robotics: Mechanics and Control by John Craig is a classic, readable introduction to manipulators and kinematics. Robot Modeling and Control by Spong, Hutchinson and Vidyasagar covers kinematics, dynamics and control with a rigorous approach. Robotics: Modelling, Planning and Control by Siciliano, Sciavicco, Villani and Oriolo is a comprehensive textbook for manipulators and mobile robots. The Springer Handbook of Robotics, edited by Siciliano and Khatib, is a large reference that covers nearly every area of robotics.

## Mobile robots, localisation and SLAM
Introduction to Autonomous Mobile Robots by Siegwart, Nourbakhsh and Scaramuzza is the standard textbook for wheeled robots, perception, localisation and navigation. Probabilistic Robotics by Thrun, Burgard and Fox is the reference for Kalman filters, particle filters, localisation, mapping and SLAM, and it is essential for any reader who wants to work on autonomous navigation. State Estimation for Robotics by Timothy Barfoot is a rigorous treatment of estimation on rotations and poses, and the author makes a PDF available. Principles of Robot Motion by Choset and colleagues covers path planning, configuration space and sensing.

## Planning, control and learning
Planning Algorithms by Steven LaValle covers motion planning, sampling-based planners, and decision making, and the author provides it free on his website. Underactuated Robotics by Russ Tedrake from MIT is a free online textbook with interactive notes on nonlinear dynamics, optimal control, trajectory optimisation, walking, flying and manipulation, and the lectures are on YouTube. Feedback Systems: An Introduction for Scientists and Engineers by Karl Åström and Richard Murray is a free PDF that teaches control theory clearly. Reinforcement Learning: An Introduction by Sutton and Barto is the reference for the learning side. Robotic Manipulation, the course notes by Russ Tedrake, covers grasping and manipulation with perception.

## Vision and perception for robots
Robotics, Vision and Control by Peter Corke combines kinematics, vision and control with code, and a Python edition is available. Multiple View Geometry in Computer Vision by Hartley and Zisserman is the reference on camera geometry and 3D reconstruction. Computer Vision: Algorithms and Applications by Richard Szeliski is a broad free textbook. The OpenCV documentation and tutorials are the practical starting point for image processing.

## ROS and software
The official ROS 2 documentation and tutorials at docs.ros.org are the main reference and are up to date, and they exist for each release. At the time of writing the newest long-term support release is Lyrical Luth. Older books teach ROS 1, which reached end of life in May 2025, so their ideas about nodes, topics and messages still help but their commands and build system do not match ROS 2. A Gentle Introduction to ROS by Jason O'Kane is free online and teaches ROS 1 concepts clearly. Programming Robots with ROS by Quigley, Gerkey and Smart is also ROS 1. The documentation of Nav2, MoveIt 2 and ros2_control is the best source for navigation, manipulation and hardware interfaces. The Articulated Robotics channel on YouTube builds a ROS 2 mobile robot step by step, and The Construct offers ROS courses.

## Electronics, microcontrollers and building
Practical Electronics for Inventors by Paul Scherz and Simon Monk is a broad reference for electronics. Make: Electronics by Charles Platt is a hands-on introduction that explains components by experiment. Arduino Workshop by John Boxall teaches Arduino through projects. Robot Builder by John Baichtal is a beginner's guide to building robots. Mechatronics by William Bolton explains the combination of mechanics, electronics and control. The documentation of Arduino, ESP32, Raspberry Pi and PlatformIO is the practical reference for your boards.

## Courses and videos
The Modern Robotics specialization on Coursera by Kevin Lynch is a structured course with exercises. Stanford's CS223A Introduction to Robotics by Oussama Khatib is available as lectures on YouTube. MIT's Underactuated Robotics and Robotic Manipulation by Russ Tedrake have lectures and notes online. Cyrill Stachniss from the University of Bonn publishes free lectures on mobile sensing, SLAM and photogrammetry. Brian Douglas explains control systems with short, clear videos. Many universities publish robotics and ROS lecture series, for example from ETH Zurich. The Kaggle and Hugging Face learning materials are useful for the machine learning side.

## Ethics and society
Robot Ethics: The Ethical and Social Implications of Robotics, edited by Patrick Lin, Keith Abney and George Bekey, is a collection of essays on robot ethics, safety and law. Standards such as ISO 10218 for industrial robots and ISO/TS 15066 for collaborative robots describe safety requirements.

## Tools to know
ROS 2, Gazebo, Webots, MuJoCo, PyBullet and NVIDIA Isaac Sim for simulation. OpenCV for vision, PCL and Open3D for point clouds. MoveIt 2 for arm motion planning, Nav2 for mobile navigation. Arduino, ESP32, Raspberry Pi and NVIDIA Jetson for hardware. CAD tools such as FreeCAD, Fusion 360, SolidWorks and Onshape for design, and KiCad for circuit boards.

## A study plan for a beginner in robotics
Months one and two: Python and basic electronics with an Arduino, and a simple line-following or obstacle-avoiding car. Months three to five: the mathematics of rotations, kinematics and PID control using Modern Robotics, and simulation of a two-link arm. Months six to nine: ROS 2 with a simulated mobile robot, then real navigation using lidar, odometry and Nav2. Then choose a path: manipulation with MoveIt and vision, mobile autonomy with SLAM and Probabilistic Robotics, or learning-based control with reinforcement learning and imitation learning. Enter a competition and publish your projects on GitHub.

<!-- id: robotics_books_resources_ar; topics: robotics -->
# كتب ومصادر لتعلم الروبوتات

## ملاحظات قبل القراءة
هذه قائمة من معرفتي العامة وليست ترتيباً رسمياً. تأكد من أحدث طبعة ومن توفر نسخة مجانية. اقرأ كتاباً عملياً وآخر نظرياً معاً، وابنِ مشروعاً أثناء القراءة.

## أفضل كتب الروبوتات
كتاب Modern Robotics: Mechanics, Planning, and Control لـ Kevin Lynch وFrank Park هو أفضل بداية لمن يتعلم ذاتياً ولديه أساس رياضي، وتتوفر نسخة أولية مجانية ومحاضرات فيديو من موقع المؤلفين، وله دورة مطابقة على Coursera من جامعة Northwestern. وكتاب Introduction to Robotics: Mechanics and Control لـ John Craig مقدمة كلاسيكية سهلة القراءة عن الأذرع والحركيات. وكتاب Robot Modeling and Control لـ Spong وHutchinson وVidyasagar يغطي الحركيات والديناميكا والتحكم بدقة. وكتاب Robotics: Modelling, Planning and Control لـ Siciliano وزملائه شامل للأذرع والروبوتات المتحركة. و Springer Handbook of Robotics مرجع ضخم يغطي كل مجالات الروبوتات.

## الروبوتات المتحركة وتحديد الموقع وSLAM
كتاب Introduction to Autonomous Mobile Robots لـ Siegwart وNourbakhsh وScaramuzza هو الكتاب القياسي للروبوتات ذات العجلات والإدراك وتحديد الموقع والملاحة. وكتاب Probabilistic Robotics لـ Thrun وBurgard وFox هو المرجع لمرشحات كالمان ومرشحات الجسيمات وتحديد الموقع والخرائط وSLAM. وكتاب State Estimation for Robotics لـ Timothy Barfoot معالجة دقيقة لتقدير الأوضاع والدورانات ونسخة PDF منه متاحة من المؤلف. وكتاب Principles of Robot Motion لـ Choset وزملائه عن تخطيط المسار وفضاء التهيئة.

## التخطيط والتحكم والتعلم
كتاب Planning Algorithms لـ Steven LaValle عن تخطيط الحركة والمخططات القائمة على العينات واتخاذ القرار، ويوفره المؤلف مجاناً على موقعه. وكتاب Underactuated Robotics لـ Russ Tedrake من MIT كتاب مجاني على الإنترنت بملاحظات تفاعلية عن الديناميكا اللاخطية والتحكم الأمثل والمشي والطيران والإمساك، والمحاضرات على يوتيوب. وكتاب Feedback Systems لـ Åström وMurray مجاني بصيغة PDF ويشرح نظرية التحكم بوضوح. وكتاب Reinforcement Learning: An Introduction لـ Sutton وBarto هو مرجع جانب التعلم.

## الرؤية الحاسوبية للروبوتات
كتاب Robotics, Vision and Control لـ Peter Corke يجمع الحركيات والرؤية والتحكم مع كود، وتتوفر نسخة بايثون. وكتاب Multiple View Geometry in Computer Vision لـ Hartley وZisserman مرجع هندسة الكاميرات وإعادة البناء ثلاثي الأبعاد. ووثائق مكتبة OpenCV هي البداية العملية لمعالجة الصور.

## ROS والبرمجيات
وثائق ROS 2 الرسمية ودروسها على docs.ros.org هي المرجع الرئيسي الأحدث. وقت كتابة هذه المعلومات أحدث نسخة دعم طويل هي Lyrical Luth. الكتب الأقدم تعلّم ROS 1 الذي انتهى دعمه في مايو 2025، فأفكارها عن العقد والمواضيع مفيدة لكن أوامرها ونظام البناء فيها لا تطابق ROS 2. كتاب A Gentle Introduction to ROS لـ Jason O'Kane مجاني ويشرح مفاهيم ROS 1، وكتاب Programming Robots with ROS كذلك لـ ROS 1. وثائق Nav2 وMoveIt 2 وros2_control أفضل مصدر للملاحة والتحكم بالأذرع وواجهات العتاد. وقناة Articulated Robotics على يوتيوب تبني روبوتاً متحركاً بـ ROS 2 خطوة بخطوة.

## الإلكترونيات وبناء الروبوتات
كتاب Practical Electronics for Inventors لـ Scherz وMonk مرجع واسع في الإلكترونيات. وكتاب Make: Electronics لـ Charles Platt مقدمة عملية. وكتاب Arduino Workshop لـ John Boxall يعلّم Arduino بالمشاريع. وكتاب Robot Builder لـ John Baichtal دليل مبتدئ لبناء الروبوتات. وكتاب Mechatronics لـ William Bolton يشرح دمج الميكانيكا والإلكترونيات والتحكم.

## دورات ومحاضرات
دورة Modern Robotics على Coursera لـ Kevin Lynch منظمة وبها تمارين. ومحاضرات CS223A من Stanford لـ Oussama Khatib على يوتيوب. ومحاضرات Underactuated Robotics وRobotic Manipulation لـ Russ Tedrake من MIT مع الملاحظات. وقناة Cyrill Stachniss من جامعة Bonn بمحاضرات مجانية عن SLAM والاستشعار المتنقل. وقناة Brian Douglas تشرح أنظمة التحكم بمقاطع واضحة.

## خطة دراسة لمبتدئ في الروبوتات
الشهران الأول والثاني: بايثون وأساسيات الإلكترونيات مع Arduino وسيارة تتبع الخط أو تتجنب العوائق. من الشهر الثالث إلى الخامس: رياضيات الدورانات والحركيات والتحكم PID بكتاب Modern Robotics ومحاكاة ذراع بوصلتين. من الشهر السادس إلى التاسع: ROS 2 مع روبوت متحرك محاكى ثم ملاحة حقيقية بالليدار وodometry وNav2. بعدها اختر مساراً: الإمساك والتحكم بالأذرع مع MoveIt والرؤية، أو الاستقلالية للروبوتات المتحركة مع SLAM وكتاب Probabilistic Robotics، أو التحكم بالتعلم مع التعلم المعزز والتعلم بالتقليد. وشارك في مسابقة وانشر مشاريعك على GitHub.
