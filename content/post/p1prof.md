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
##### What was done in this study?

Building on the existing Python 3 sckikit-learn library, researchers from Poland recently published a new multi-label classification library, scikit-multilearn (skml in short) on Journal of Machine Learning Research. Compatible with sciki-learn and scipy ecosystems, this library provides native Python implementations of mutli-label classification methods, allowing the single-label deep learning methods to be extended into multi-label tasks - which is particularly efficient in problem transformation than other established libraries.

##### Why might this be interesting?

Sciki-multilearn Out of the three groups of multi-label classification <cite>[2]</cite>, the new skml library is presented as a viable alternative to the conventional approach through MULAN and MEKA: other than adapting the decision tree methods, it is presented to be ready for algorithm adaption, problem transformation as well as ensemble approaches. Developed based on the Python scientific ecosystem and independent of the famous WEKA library, the researchers tested the new skml library to be faster, more less memory-intensive, and more efficient in label space divisioning. Promising to provide full Java stack (MEKA <cite>[3]</cite>, MULAN <cite>[4]</cite> and WEKA <cite>[5]</cite> through MEKA when necessary), this new library apepars to be an interesting addition to the machine learning field and Python enthusiasts. The skml library also provides a wrapper that allows using any Keras, Tensorflow, CNTK or PyTorch backend to solve multi-label problems through problem transformation, suggesting interesting implementation even in the Deep Learning end. 

##### Some technical challenges/drawbacks of the approach

There does not appear to be any apparent disadvantage of the skml library according to the publication other than a somewhat less steep learning curve. The mere mentioning of potential necesesity of using currently-available approaches, i.e. the necessity of using WEKA, may indicate that there are some inherent weakness of the approach. However, a natural Python implimentaton of multi-label classification will, as the authors have pointed out, obviously speed up the production process. 

The project source code and documentation can be downloaded from http://scikit.ml as well as via pip, and is BSD-licensed. 


Cross-lingual Speech-based Tobi Label Generation Using Bidirectional Lstm
-------------------------
##### What was done in this study?
In addition, a recent publication on the Speech and Signal Processing conference showed some very interesting results they obtained by using Japanese-trained neural networks to discern English speeches, and provided evidence of success, particularly when there is a time lag larger than 80 ms<cite>[6]</cite>. The researchers used a light-weight BiLSTM with two hidden layers (1024 BiLSTM cells each) through PyTorch.

##### Why might this be interesting?

This may not be of extreme interests if the NLP-based learning is limited only to written text. However, as the project premise incorporates cross-lingual speech-based TOBI label generation, shall the need arises to implement analysis on documented conference recordings and proceedings with a cross-cultural nature, this would be a very interesting case study to go back to, or keep track of since the researchers are likely to continue along this path of investigation per their previous research record<cite>[7]</cite>. 


##### Some technical challenges/drawbacks of the approach
Japanese is a highly phonetic language, and has a hiragana system that adopts foreign language into its phonetic system. Since English is also a phonetic language, the results of this study may be skewed since both has limited fricative sounds. Application of the method reported in the study on a language that has less phonemic orthography - such as Chinese - may prove that the prosody-label-generation applies primarily to phonetic languages. 

[1]Piotr Szymański, Tomasz Kajdanowicz, _scikit-multilearn: A Python library for Multi-Label Classification_; Journal of Machine Learning Research, 20(6):1−22, 2019.

[2]Gjorgji Madjarov, Dragi Kocev, Dejan Gjorgjevikj, and Saˇso Dˇzeroski. An extensive ex- perimental comparison of methods for multi-label learning. Pattern Recognition, 45(9): 3084–3104, September 2012.

[3]Grigorios Tsoumakas, Eleftherios Spyromitros-Xioufis, Jozef Vilcek, and Ioannis Vlahavas. Mulan: A java library for multi-label learning. Journal of Machine Learning Research, 12:2411–2414, 2011b.

[4]Jesse Read, Peter Reutemann, Bernhard Pfahringer, and Geoff Holmes. MEKA: A multi- label/multi-target extension to Weka. Journal of Machine Learning Research, 17(21):1–5, 2016.

[5]Mark Hall, Eibe Frank, Geoffrey Holmes, Bernhard Pfahringer, Peter Reutemann, and Ian H. Witten. The WEKA data mining software: An update. SIGKDD Explor. Newsl., 11(1):10–18, November 2009. ISSN 1931-0145.

[6]Marco Vetter ; Sakriani Sakti ; Satoshi Nakamura, Cross-lingual Speech-based Tobi Label Generation Using Bidirectional Lstm,  ICASSP 2019 - 2019 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Brighton, United Kingdom, Apr. 17th, 2019.

[7]M. Vetter, M. Müller, F. Hamlaoui, G. Neubig, S. Nakamura, S. Stüker, A. Waibel, "Unsuper-vised phoneme segmentation of previously unseen languages", Proceedings of the Interspeech, 2016.
