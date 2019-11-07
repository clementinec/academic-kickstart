---
title: "Vertical Borehole Heat Exchanger Length Estimation"
description: "More works published on the exploration of mean radiant temperature!"
date: "2019-11-06"
categories:
  - "publication"
  - "research"
tags:
  - "geothermal"
  - "analytical modeling"
  - "required borehole length"
---
The basics
-------------------------


Method to estimate required length of borehole
-------------------------
The methods required to estimate the length required by borehole is outlined in ASHRAE Handbook - Applications (2015). Specifically, we'll be looking at the sizing of a vertical geothermal heat pump system. The given (known) values that we have are $q_c$ and $q_h$, the cooling and heating load of the new campus in tons, which needs to be plugged into the following Equation (1) for the required length of cooling:

$$L_c = \frac{q_a R_{ga} + (q_{lc}-3.41 W_c) (R_b+PLF_m R_{gm}+R_{gd} F_{sc})}{t_g-\frac{t_{wi}+t_{wo}}{2}-t_p}$$ (1)

The required length for heating could, similarly, be calculated from Equation (2). Since $L_h$ is commonly smaller than $L_c$, it is very common to use $L_c$ instead of $L_h$ when sizing geothermal systems. 

$$L_h = \dfrac{q_aR_{ga} + (q_{lh}-3.41 W_h)(R_b+PLF_mR_{gm} + R_{gd} F_{sc})}{t_g- \frac{t_{wi} + t_{wo}}{2} - t_p}$$ (2)

Regarding the respective variables in Equation (1), $R_b$ is obviously the thermal resistance of the bore, which can be estimated from the different diameters of boreholes. $t_g$ is the undisturbed ground temperature, $t_{p}$ is the temperature penalty for interference of adjacent bores, and $t_{wi},t_{wo}$ the liquid temperature at heat pump inlet and outlet. The system power input as design cooling/heating load is expressed as $W_c$ or $W_h$. A few less common variables are the short-circuit heat loss factor $F_{sc}$, the part-load factor during design month, and the effective(equivalent) thermal resistance of the ground of an annual, daily, monthly basis as $R_{ga},R_{gd},R_{gm}$ as well as shorter terms $R_{gst}$. 

To evaluate the equivalent thermal resistances of the ground, the solution from Carslaw and Jaeger (1947) requires the time of operation, borehole diameter and thermal diffusivity of the ground to be related in the dimensionless Fourier number (Fo):

$$Fo = \frac{4\alpha_g \tau}{d_b^2}$$    (3)

Here the thermal diffusivity of the ground can be written as $$\alpha_g$$, and $$d_b$$ is the bore diameter, $\tau$ the time of operation in days. 

A geothermal system is therefore modelled in three phases, or as denoted by the 2015 ASHRAE Handbook, three pulses: 10 year (3650 days) pulse at $q_a$, 1 month (30 days) pulse at $$q_m$$, and a 4h (0.167 day) pulse of $$q_{st}$$:

$$\tau_1 = 3650 days$$ $$\tau_2 = 3680 days $$ $$ \tau_f = 3680.167 days$$

The corresponding Fourier number can then be computed with the following values:

$$Fo_f = 4\alpha \tau_f /d_b^2$$ $$ Fo_1 = 4\alpha (\tau_f - \tau_1)/d_b^2$$ $$Fo_2 = 4\alpha (\tau_f-\tau_2)/d_b^2$$    (4)

After the calculation of the Fourier factor, the corresponding G-factor - $G_1, G_2, G_f$ can be identified using the G-factor graph of ground thermal resistance as developed by Kavanaugh and Rafferty in 1997, such that we can estimate the corresponding $R_{ga}, R_{gm},R_{gst}$ assuming a known ground thermal conductivity:

$$R_{ga} = (G_f - G_1)/ k_g $$     (5)
$$R_{gm} = (G_1 - G_2)/ k_g $$     (6)
$$R_{gst} = G_2/k_g $$            (7)

More specifically with our example, we need to estimate the heat pump cooling and heating efficiency (which is unclear in MEPAssociate's analysis, so we will probably just take the ASHRAE Handbook's value) to estimate the resulting length of the borehole. 
