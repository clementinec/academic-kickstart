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
#### What's Python?

Python is a high-level programming language. Essentially a scripting language, it does not require compilations, and provide data scientists a very intuitive and fast working environment through its edit-test-debug cycle. Featuring simple and easy-to-learn syntax, Python can be used in examples as simple as the example shown below(calculation of tips), or as heavy-lifting as multi-dimensional time series analytics or the gluing language of pre-existing compiled components written in Python or other languages. It is also a freely usable and distributable even for commercial use since it is developed under an open source license. 

```
def calculatetip(x):
	return x*0.15
print calculatetip(45)
6.75
```

#### What's multi-label classification?

Multi-label classification allows the same set of data to be described using different labels - very similar to what we may observe under the "Read reviews that mention" on Amazon. It's important to point out multi-label classification is different from multi-class classification - it is very similar to how a wrestling athelete can be fit into different weight groups when fighting different styles (multi-label) at the same weight (singular value among many other classes that the athelete can be categorized, sex, age, year of competition, etc.).

#### Why is this study of particular interests to our data scientists?

The multi-label classification can help our data scientists when attempting to automize the categorisation of texts. Using multiple categories suggested by domain experts to train a multi-label model, data scientists can avoid the _curse of dimensionality_ <cite>[2]</cite> and generate a prediction of multiple labels associated with a new instance. A common example of this could be, for example, if we were to train a model that predicts the genre of a movie <cite>[3]</cite>with its IMDb summary. Using a reasonably large dataset of storylines and the genres that they are commonly associated with on IMDb, we could train a model that predicts the genres of a new movie once its storyline is fed to the model. The output will likely be a list of probabilities associated with each genre, as seen on the IMDb page for the 2019 movie Joker: crime, drama and thriller. 

#### What's new about this approach?

The most prominnet multi-label classification stacks to date are MULAN <cite>[4]</cite> and MEKA <cite>[5]</cite> , both implemented in Java and heavily reliant on a famous WEKA library that wasn't compatible with Python's scientific ecosystem's philosophy. The library published by the Polish researchers is by far the most extensive scikit-learn compatible multi-label classification library so far, providing fast and memory-efficient implmentations of both the most popular algorithms and new families of methods in Python comparing to other alternatives.

Cross-lingual Speech-based Tobi Label Generation Using Bidirectional Lstm
-------------------------
Another very interesting study came from researchers in Japan, where they attempted to use prosody-based Japanese-trained model to recognize English<cite>[6]</cite>. Their fundamental logic was interestingly simple: infants were shown to recognize prosody before further segmenting speech into words and cluases, so generating prosodic boundaries may allow them to recreate this further segmentation with a trained model - and apply that on another langugage such as English. 

This is a particularly interesting study since not only the prosody labels were automatically generated, the Japanese speech samples are also spontaneous, i.e. without predefined contexts. The researchers used the PyTorch deep learning platform to first, train a model from the continuous Japanese speech <cite>[7]</cite>, and then compare its performance in recognizing the prosodic boundaries in the test data against a model trained on English. The researchers were able to show that the Japanese-trained model, without being exposed to English before, can retain much of its predictive power in cross-lingual application - especially when given a longer temporal tolerance of more than 80ms. Although both Japanese and English are big languages with many users, the most exciting part about this study is its promises on being applied to less common (or lesser used) languages whose samples are much more scarce - and still being able to discern the prosodic information - and ultimately, automatic lexical discovery through a limited sound sample.



[1]Piotr Szymański, Tomasz Kajdanowicz, _scikit-multilearn: A Python library for Multi-Label Classification_; Journal of Machine Learning Research, 20(6):1−22, 2019.

[2]Curse of dimensioality refers to various phenomena that arise when analyzing multi-faceted data and attempting to extract as much feature sets as necessary, which could result in the amount of data needing to support result growing exponentially. For machine learning purposes, the typical rule of thumb is at least 5 training examples for each dimension/feature. Accessed on Nov. 14th, 2019 at :https://en.wikipedia.org/wiki/Curse_of_dimensionality

[3]Kartik Nooney, Deep dive into multi-label classification..! (With detailed Case Study). Accessed on Nov. 13th, 2019 at: https://towardsdatascience.com/journey-to-the-center-of-multi-label-classification-384c40229bff


[4]Grigorios Tsoumakas, Eleftherios Spyromitros-Xioufis, Jozef Vilcek, and Ioannis Vlahavas. Mulan: A java library for multi-label learning. Journal of Machine Learning Research, 12:2411–2414, 2011b.

[5]Jesse Read, Peter Reutemann, Bernhard Pfahringer, and Geoff Holmes. MEKA: A multi- label/multi-target extension to Weka. Journal of Machine Learning Research, 17(21):1–5, 2016.

[6]Marco Vetter ; Sakriani Sakti ; Satoshi Nakamura, Cross-lingual Speech-based Tobi Label Generation Using Bidirectional Lstm,  ICASSP 2019 - 2019 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Brighton, United Kingdom, Apr. 17th, 2019.

[7]M. Vetter, M. Müller, F. Hamlaoui, G. Neubig, S. Nakamura, S. Stüker, A. Waibel, "Unsuper-vised phoneme segmentation of previously unseen languages", Proceedings of the Interspeech, 2016.
