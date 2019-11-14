---
title: "Recent development in machine learning"
description: "Specialist-facing research development on Python deployment in machinelearning - specifically focusing on sckit-based appraoches!"
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
Building on the existing Python 3 sckikit-learn library, researchers from Poland recently published a new multi-label classification library, scikit-multilearn (skml in short) on Journal of Machine Learning Research. Compatible with sciki-learn and scipy ecosystems, this library provides native Python implementations of mutli-label classification methods, allowing the single-label deep learning methods to be extended into multi-label tasks - which is particularly efficient in problem transformation than other established libraries.

Sciki-multilearn Out of the three groups of multi-label classification (Madjarov et al., 2012), the new skml library is presented as a viable alternative to the conventional approach through MULAN and MEKA: other than adapting the decision tree methods, it is presented to be ready for algorithm adaption, problem transformation as well as ensemble approaches. Developed based on the Python scientific ecosystem and independent of the famous WEKA library, the researchers tested the new skml library to be faster, more less memory-intensive, and more efficient in label space divisioning. Promising to provide full Java stack (MEKA, MULAN and WEKA through MEKA when necessary), this new library apepars to be an interesting addition to the machine learning field and Python enthusiasts. The skml library also provides a wrapper that allows using any Keras, Tensorflow, CNTK or PyTorch backend to solve multi-label problems through problem transformation, suggesting interesting implementation even in the Deep Learning end. 

The project source code and documentation can be downloaded from http://scikit.ml as well as via pip, and is BSD-licensed. 


P2 - TBD <cite>[?]</cite>
-------------------------


[1]Piotr Szymański, Tomasz Kajdanowicz, _scikit-multilearn: A Python library for Multi-Label Classification_; Journal of Machine Learning Research, 20(6):1−22, 2019.

[?]