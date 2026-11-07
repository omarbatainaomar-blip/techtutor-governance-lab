<!-- topics: programming,web_security -->
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
