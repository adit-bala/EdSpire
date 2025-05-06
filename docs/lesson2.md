---
marp: true
theme: uncover
class: invert
style: |
  section {
      font-size: 175%;
  }
  footer {
        font-size: .6em;
  }
paginate: true
---

<!--
_paginate: false
_footer: Slides available at https://edspire.aditbala.com/docs/lesson1 
_class: lead invert
-->

# <!--fit--> EdSpire Lecture 02

###  Python for AI Development

Aditya Balasubramanian and Saurav Suresh

---

<!-- 
_class: invert
_backgroundColor: #2222
-->


## <!-- fit --> Announcements :mega:

---

<!--
_class: invert
-->

# <!-- fit --> Control :robot:

---

<!--
_class: invert
-->

# Booleans

| Falsey                 | Truthy          |
| :--------------------- | :-------------- |
| `False`                | `True`          |
| `None`                 | Everything else |
| `0`                    |                 |
| `[]`, `""`, `()`, `{}` |                 |

---

<style scoped>
  pre > code {
    font-size: 150%;
  }
</style>

<!--
_class: invert

-->

## If Statements

- How to use `<conditional expressions>` to execute/skip lines of code?

```python
if <conditional expression>:
    <suite of statements>
elif <conditional expression>:
    <suite of statements>
else:
    <suite of statements>
```

- Colons after `if`, `elif`, `else` statements
- `else` doesn't need `<conditional expression>`

---

<!--
_class: invert
-->

<style scoped>
  pre > code {
    font-size: 150%;
  }
</style>

## If Statements Example

```python
wallet = 0

if wallet > 0:
    print('you are not broke')
else:
    print('you are broke')
if wallet == 0:
    print(0)
```

---

<!--
_class: invert
-->

<style scoped>
  pre > code {
    font-size: 150%;
  }
</style>

## If Statements Example

```python
wallet = 0

if wallet > 0:
    print('you are not broke')
else:
    print('you are broke')
if wallet == 0:
    print(0)
```

```python
 you are broke
 0
```


---

<!--
_class: invert
-->

<style scoped>
  pre > code {
    font-size: 170%;
  }
</style>

## While Loops

- How to execute a statement multiple times in a program?

```python
while <conditional clause>:
    <statements body>
```

- program executes until `<conditional clause>` is false
- In other words, only run when `<conditional clause>` evaluates to `true`

---

<!--
_class: invert
-->

## While Loop Examples

<style scoped>
  pre > code {
    font-size: 170%;
  }
</style>

```python
x = 3
while x > 0:
    print(x)
    x -= 1
```

---

<!--
_class: invert
-->

## While Loop Example

<style scoped>
  pre > code {
    font-size: 170%;
  }
</style>

```python
x = 3
while x > 0:
    print(x)
    x -= 1
    # x = x - 1
```

```python
3
2
1
```

---

<!--
_class: invert
-->

<style scoped>
  pre > code {
    font-size: 170%;
  }
</style>

## For Loops

- How to execute a statement multiple times in a program?

```python
for <variable> in <iterable>:
    <statements body>
```

- program executes for each element in `<iterable>`
- `<iterable>` can be a list, tuple, string, etc.
- `<variable>` is the current element in `<iterable>`

---

<!--
_class: invert
-->

## For Loop Examples

<style scoped>
  pre > code {
    font-size: 170%;
  }
</style>

```python
for i in range(3):
    print(i)
```

```python
0
1
2
```

---

## functions

<style scoped>
  pre > code {
    font-size: 170%;
  }
</style>


- functions are a reusable piece of code

```python
def say_hello_to_guest(guest_name):
    print(f"Hello {guest_name}!")
```

- functions are defined with the `def` keyword
- functions are called with the function name and parentheses
- functions can take in arguments
- functions can return values

---

## APIs

* What is an API
  * Application Programming Interface
  * Allows for communication between software applciations
* Key Components
  * Request: What you ask the API to do (e.g., "Give me user data").
  * Response: What the API sends back (e.g., the user’s name and email).
  * Endpoint: A specific URL where the API can be accessed.

---

## APIs in Machine Learning

- Many machine learning models are large and computationally expensive
- Running models locally can be infeasable for many
- Setting up the infastructure to run these models at larger scale may also be infeasable (expensive, time consuming, maintinance)
- Accessing models through APIs is great solution for many ML projects

---

## OpenAI's API

- Lets you access GPT-4.1, o4-mini, o3, and more
- Can be used for text generation, text embeddings, and computer vision tasks
* Is it free?
  * No

---

## OpenAI API Set Up

- Need an API key
- Install OpenAI Python library (pip install openai)

---

## Chat Completion Example

```python
from openai import OpenAI

# Initialize the client using your API key
client = OpenAI(api_key="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX")

# Make a chat completion request
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Tell me a fun fact about space!"}
    ]
)

print(response.choices[0].message.content)
```