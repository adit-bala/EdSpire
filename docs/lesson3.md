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
_footer: Slides available at https://edspire.aditbala.com/docs/lesson3 
_class: lead invert
-->

# <!--fit--> EdSpire Lecture 03

###  Deep Dive into LLMs

Aditya Balasubramanian and Saurav Suresh

---

# Embeddings

- How do machines represent text?

--- 

## One-Hot Encoding

- Assign a unique vector to each word
- EX: house, cat, dog
- house -> [1, 0, 0]
- cat -> [0, 1, 0]
- dog -> [0, 0, 1]
- Issues: arbitrary, not context aware, only word level, problems in higher dimensional space


---

<!--
_footer: source: https://jalammar.github.io/illustrated-word2vec/
-->

## Word2Vec

* Introduced in 2013
* What is a vector?
    * a list of numbers that represent something
* Example
    * Representing your personality with 5 numbers!
    * Let's say you take a test which rates different aspects of your personality (ex. Extraversion: 39/100)
    

![width:600px](../img/embedding1.png)

---


## Word2Vec

*  Hard to understand a person from only one trait, let's add one more dimension

* ![width:600px](../img/embedding2.png)

* Let's plot some more peeople's personality, who would replace Jay if he got hit by a bus

* ![width:600px](../img/embedding3.png)


---

## Word2Vec

* We can use `cosine_similarity` to find the most similar person to Jay

```python
# Jay's personality vector
jay = [-0.4, 0.8]

# Other people's personality vectors
person1 = [-0.3, 0.2]
person2 = [-0.5, -0.4]

cosine_similarity(jay, person1) # 0.87
cosine_similarity(jay, person2) # -0.20
```

* Person #1 is more similar to Jay in personality. Vectors pointing in the same direction (length plays a role as well) have a higher cosine similarity score.

--- 

## Word2Vec

* One Problem -- people are more complex than just 2 traits
    * Solution -- more dimensions!

```python
# Jay's personality vector (5 dimensions)
jay = [-0.4, 0.8, 0.5, -0.2, 0.3]

# Other people's personality vectors (5 dimensions)
person1 = [-0.3, 0.2, 0.3, -0.4, 0.9]
person2 = [-0.5, -0.4, -0.2, 0.7, -0.1]

cosine_similarity(jay, person1) # 0.66
cosine_similarity(jay, person2) # -0.37
```

* Important notes
    - We can represent people and other things as a vector
    - We can easily calculate the similarity between two vectors

---

## Word2Vec

* Let's take a look at examples for higher dimension embeddings
    * These embeddings are from the GloVe model trained on Wikipedia

* ![width:600px](../img/embedding4.png)

* Which ones are similar to each other?
* What are some interesting patterns?


---

## Word2Vec

- What can we do with embeddings?
* Powerful example -- King - Man + Woman = ?
    * Queen!
* ![width:600px](../img/embedding5.png)

---

## Transformers

- Input and Positional Encodings
- Attention Mechanism
- Multi-layer Perceptrons
- Encoders & Decoders
- Modern Variations (Modified encoders)

---

## LLM Inputs

- We prompt LLMs like ChatGPT with regular text (i.e. "How many human years are in one dog year?")
- The LLM transforms this text into a sequence of tokens (or embeddings)
- Ex: "How's it going?" -> <"How"> + <'s> + <it> + <gog + <in>>
