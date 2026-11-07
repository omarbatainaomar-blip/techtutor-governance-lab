<!-- topics: programming -->
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
