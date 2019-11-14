---
title: "Recent development in machine learning - Technical"
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

Sciki-multilearn Out of the three groups of multi-label classification <cite>[2]</cite>, the new skml library is presented as a viable alternative to the conventional approach through MULAN and MEKA: other than adapting the decision tree methods, it is presented to be ready for algorithm adaption, problem transformation as well as ensemble approaches. Developed based on the Python scientific ecosystem and independent of the famous WEKA library, the researchers tested the new skml library to be faster, more less memory-intensive, and more efficient in label space divisioning. Promising to provide full Java stack (MEKA <cite>[3]</cite>, MULAN <cite>[4]</cite> and WEKA <cite>[5]</cite> through MEKA when necessary), this new library apepars to be an interesting addition to the machine learning field and Python enthusiasts. The skml library also provides a wrapper that allows using any Keras, Tensorflow, CNTK or PyTorch backend to solve multi-label problems through problem transformation, suggesting interesting implementation even in the Deep Learning end. 

The project source code and documentation can be downloaded from http://scikit.ml as well as via pip, and is BSD-licensed. 


P2 - TBD
-------------------------
<cite>[?]</cite>

[1]Piotr Szymański, Tomasz Kajdanowicz, _scikit-multilearn: A Python library for Multi-Label Classification_; Journal of Machine Learning Research, 20(6):1−22, 2019.

[2]Gjorgji Madjarov, Dragi Kocev, Dejan Gjorgjevikj, and Saˇso Dˇzeroski. An extensive ex- perimental comparison of methods for multi-label learning. Pattern Recognition, 45(9): 3084–3104, September 2012.

[3]Grigorios Tsoumakas, Eleftherios Spyromitros-Xioufis, Jozef Vilcek, and Ioannis Vlahavas. Mulan: A java library for multi-label learning. Journal of Machine Learning Research, 12:2411–2414, 2011b.

[4]Jesse Read, Peter Reutemann, Bernhard Pfahringer, and Geoff Holmes. MEKA: A multi- label/multi-target extension to Weka. Journal of Machine Learning Research, 17(21):1–5, 2016.

[5]Mark Hall, Eibe Frank, Geoffrey Holmes, Bernhard Pfahringer, Peter Reutemann, and Ian H. Witten. The WEKA data mining software: An update. SIGKDD Explor. Newsl., 11(1):10–18, November 2009. ISSN 1931-0145.