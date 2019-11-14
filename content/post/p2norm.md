---
title: "Recent development in machine learning"
description: "Tailored to less-informed beginners of Machine learning."
date: "2019-11-14"
categories:
  - "machine learning"
  - "research"
tags:
  - "learn"
  - "labeling"

---


A scikit-based Python environment for performing multi-label classification<cite>[1]</cite>
-------------------------
What's Python?

Python is a high-level programming language. Essentially a scripting language, it does not require compilations, and provide data scientists a very intuitive and fast working environment through its edit-test-debug cycle. Featuring simple and easy-to-learn syntax, Python can be used in examples as simple as the example shown below(calculation of tips), or as heavy-lifting as multi-dimensional time series analytics or the gluing language of pre-existing compiled components written in Python or other languages. It is also a freely usable and sitributable even for commercial use since it is developed under an open source license. 

```
def calculatetip(x):
	return x*0.15
print calculatetip(45)
6.75
```

What's multi-label classification?
Multi-label classification allows the same set of data to be described using different labels - very similar to what we may observe under the "Read reviews that mention" on Amazon. It's important to point out multi-label classification is different from multi-class classification - it is very similar to how a wrestling athelete can be fit into different weight groups when fighting different styles (multi-label) at the same weight (singular value among many other classes that the athelete can be categorized, sex, age, year of competition, etc.).

Why is this study of particular interests to our data scientists?
The multi-label classification can help our data scientists when attempting to automize the categorisation of texts. Using multiple categories suggested by domain experts to train a multi-label model, data scientists can avoid the _curse of dimensionality_<cite>[2]</cite> and generate a prediction of multiple labels associated with a new instance. A common example of this could be, for example, if we were to train a model that predicts the genre of a movie with its IMDb summary. Using a reasonably large dataset of storylines and the genres that they are commonly associated with on IMDb, we could train a model that predicts the genres of a new movie once its storyline is fed to the model. 
The output, will likely be a list of probabilities associated with each genre, as seen on the IMDb page for the 2019 movie Joker: crime, drama and thriller. 

What's new about this approach?
The most prominnet multi-label classification stacks to date are MULAN (Tsoumakas et al., 2011) and MEKA (Read et al., 2016), both implemented in Java and heavily reliant on a famous WEKA library that wasn't compatible with Python's scientific ecosystem's philosophy. The library published by the Polish researchers is by far the most extensive scikit-learn compatible multi-label classification library so far, providing fast and memory-efficient implmentations of both the most popular algorithms and new families of methods in Python comparing to other alternatives.


P2 - TBD <cite>[?]</cite>
-------------------------


[1]Piotr Szymański, Tomasz Kajdanowicz, _scikit-multilearn: A Python library for Multi-Label Classification_; Journal of Machine Learning Research, 20(6):1−22, 2019.

[2]Curse of dimensioality refers to various phenomena that arise when analyzing multi-faceted data and attempting to extract as much feature sets as necessary, which could result in the amount of data needing to support result growing exponentially. For machine learning purposes, the typical rule of thumb is at least 5 training examples for each dimension/feature. https://en.wikipedia.org/wiki/Curse_of_dimensionality

[?]https://towardsdatascience.com/journey-to-the-center-of-multi-label-classification-384c40229bff

