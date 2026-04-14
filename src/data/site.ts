export const profile = {
  name: "Hongshan Guo",
  role: "Assistant Professor",
  department: "Department of Architecture",
  institution: "The University of Hong Kong",
  since: "September 2023",
  email: "hongshan@hku.hk",
  phone: "+852 9677 8596",
  location: "Hong Kong",
  orcid: "0000-0002-8716-0343",
  hero:
    "Design science for human-building-climate systems.",
  summary:
    "Probabilistic modeling, physics-informed ML, co-simulation, climate stress-testing, and design-facing AI for buildings, cities, and public institutions.",
  profilePoints: [
    "Published a correction to the century-old 120 W metabolic default in comfort standards, prompting and winning ASHRAE 1959-TRP as PI in February 2026.",
    "Builds digital twins, probabilistic simulation pipelines, scenario-conditioned weather generation, and computer-vision methods for environmental design.",
    "Translates technical research into teaching, open benchmarks, and cross-disciplinary design pedagogy."
  ]
};

export const links = [
  { label: "Email", href: "mailto:hongshan@hku.hk" },
  { label: "ORCID", href: "https://orcid.org/0000-0002-8716-0343" },
  {
    label: "Google Scholar",
    href: "https://scholar.google.com/citations?hl=en&user=T34nzWsAAAAJ"
  },
  {
    label: "LinkedIn",
    href: "https://www.linkedin.com/in/hongshan-guo-b861a062"
  },
  {
    label: "ResearchGate",
    href: "https://www.researchgate.net/profile/Hongshan-Guo-3"
  },
  { label: "CV", href: "/cv.pdf" }
];

export const metrics = [
  {
    value: "1959-TRP",
    label: "ASHRAE project awarded",
    detail: "PI award in February 2026 after standards-impact work in Energy and Buildings."
  },
  {
    value: "HK$1.3M",
    label: "Teaching grants secured",
    detail: "Socratic Oracle and AI Design Coach across Architecture, Geography, and Computer Science."
  },
  {
    value: "13",
    label: "Climates used to validate co-simulation",
    detail: "Robust stress-testing of data-driven comfort models under uncertainty."
  },
  {
    value: "2100",
    label: "Climate horizon",
    detail: "Scenario-conditioned weather generation and resilience modeling through end-of-century futures."
  }
];

export const contributions = [
  {
    title: "Standards intervention",
    text:
      "Demonstrated demographic bias in prevailing metabolic defaults used in global thermal comfort standards, positioning the work for direct standards revision."
  },
  {
    title: "Playable performance models",
    text:
      "Built co-simulation workflows that integrate data-driven comfort models with EnergyPlus and tested them across 13 climates."
  },
  {
    title: "Design-facing AI infrastructure",
    text:
      "Led AI-enabled pedagogy platforms, including Socratic Oracle and AI Design Coach, to support evidence-based design reasoning."
  }
];

export const appointments = [
  {
    title: "Assistant Professor",
    org: "The University of Hong Kong",
    years: "2023-present",
    detail: "Department of Architecture."
  },
  {
    title: "Principal Data Scientist",
    org: "Bank of New York Mellon",
    years: "2020-2023",
    detail:
      "Led end-to-end ML deployment and model governance for daily USD 29-43 billion Federal Reserve account-balance forecasting."
  },
  {
    title: "Postdoctoral Researcher",
    org: "Princeton University",
    years: "2019-2020",
    detail: "Research at the intersection of building science, sensing, and environmental modeling."
  }
];

export const education = [
  {
    degree: "Ph.D., Architecture",
    school: "Princeton University",
    year: "2019",
    detail: "Architectural Technology and Computational Design."
  },
  {
    degree: "M.Eng., Mechanical Engineering",
    school: "Columbia University",
    year: "2013",
    detail: ""
  },
  {
    degree: "B.Eng., Architectural Engineering",
    school: "Harbin Institute of Technology",
    year: "2012",
    detail: "HVAC Engineering."
  }
];

export const expertise = [
  {
    area: "Design science and performance simulation",
    items: [
      "Digital twins and co-simulation frameworks",
      "Physics-informed machine learning",
      "Probabilistic design exploration under uncertainty",
      "EnergyPlus and Modelica workflows",
      "Reduced-order and surrogate models",
      "Post-occupancy evaluation and learning-enabled control"
    ]
  },
  {
    area: "AI and computational methods",
    items: [
      "Physics-informed neural networks",
      "Bayesian inference and calibration",
      "Uncertainty quantification",
      "Ordinal regression",
      "Model predictive control and reinforcement learning",
      "Computer vision for thermal imagery and synthetic data generation"
    ]
  },
  {
    area: "Environmental systems and resilience",
    items: [
      "Thermodynamics, heat and mass transfer, and HVAC control",
      "Thermal comfort prediction and sensor-driven analytics",
      "Synthetic weather generation with CORDEX and CMIP data",
      "Scenario-conditioned climate projections through 2100",
      "Urban microclimate sensing and thermal equity analysis"
    ]
  }
];

export const supervision = {
  doctoral: [
    "Kanxuan He, PhD (HKU, 2025-): probabilistic control; first place at the ICML 2025 CO-BUILD Smart Building Competition.",
    "Yu Chang, PhD (HKU, 2024-): cross-cultural thermal comfort; first-author review in Renewable and Sustainable Energy Reviews (2025)."
  ],
  theses: [
    "Multi-agentic, physics-informed occupant modeling for environmental evaluation in architectural design.",
    "Neuroarchitecture thesis using EEG to study occupant responses to spatial design conditions."
  ]
};

export const honors = [
  "ASHRAE Research Project 1959-TRP, PI, USD 55,000, awarded February 2026 and commencing April 2026.",
  "Teaching Development and Language Enhancement Grant, HKU, PI, Socratic Oracle, HK$1,000,000 (2025-2028).",
  "Teaching Development Grant, HKU, PI, AI Design Coach, HK$300,000 (2026-2028).",
  "ICML 2025 CO-BUILD Smart Building Competition, first place as faculty mentor and author.",
  "NeurIPS 2025 Urban AI Workshop Buildings Challenge, third place as faculty mentor.",
  "Gartner Eye on Innovation Award, BNY Mellon, 2021.",
  "Lowry Methodology Award, International Conference of Urban Climate, 2018."
];

export const publications = {
  journals: [
    {
      authors: "Guo H., Aviv D.",
      title:
        "From Seven Points to Probabilities: Ordinal Learning for Risk-Aware Thermal Comfort Prediction.",
      venue: "Building and Environment",
      year: "2026",
      status: "Accepted",
      note: "Ordinal learning, risk-aware prediction."
    },
    {
      authors: "Guo H., Pigliautile I., Chang Y., Qiao Q., Li Y.",
      title:
        "Toward Smarter HVAC Control: Machine Learning Reveals Hidden Drivers in Thermal Comfort Databases.",
      venue: "Energy and AI",
      year: "2026",
      status: "Accepted",
      note: "Sensitivity analysis, MRT, and data quality."
    },
    {
      authors: "Guo H., Chang Y., Li Y., Zhou Y., Qiao Q., Lai C.Y., Schuldenfrei E.",
      title:
        "Ventilation-Energy Trade-offs in Retrofitted Hong Kong Wet Markets.",
      venue: "Energy and Buildings",
      year: "2026",
      status: "Published",
      note: "Field measurement and IEQ-energy retrofit trade-offs."
    },
    {
      authors: "Guo H., Sun R., Xu Y.",
      title:
        "Correcting the 120-Watt Assumption: Demographic-Aware Metabolic Rates for Energy Savings and Thermal Comfort Equity in Buildings.",
      venue: "Energy and Buildings",
      year: "2025",
      status: "Published",
      note: "Standards impact and equity; prompted ASHRAE 1959-TRP."
    },
    {
      authors: "Guo H., He K., Xu Y., Lei Y.",
      title:
        "A Co-Simulation Methodology for Integrating Data-Driven Thermal Sensation Models with Building Energy Control.",
      venue: "Energy and Buildings",
      year: "2025",
      status: "Accepted",
      note: "Digital twins, co-simulation, and validation across 13 climates."
    },
    {
      authors: "Guo H., He K., Luo Y., Chang Y.",
      title:
        "Physics-Informed Neural Networks for Robust Thermal Comfort Prediction: Overcoming Data Quality Limitations Through Physiological Constraints.",
      venue: "Building and Environment",
      year: "2025",
      status: "Published",
      note: "PINNs and physiological constraints."
    },
    {
      authors: "Chang Y., Guo H., Li Y., Chi B., Pigliautile I.",
      title:
        "A Data-Driven Qualitative Review of Thermal Comfort Studies: Bridging the Gap Between Western and Eastern Perspectives.",
      venue: "Renewable and Sustainable Energy Reviews",
      year: "2025",
      status: "Published",
      note: "Data harmonization and benchmark framing."
    },
    {
      authors: "Guo H., Ferrara M., Coleman J., Loyola M., Meggers F.",
      title:
        "Simulation and Measurement of Air and Mean Radiant Temperatures in a Radiantly Heated Indoor Space.",
      venue: "Energy",
      year: "2020",
      status: "Published",
      note: ""
    },
    {
      authors:
        "Guo H., Aviv D., Loyola M., Teitelbaum E., Houchois N., Meggers F.",
      title:
        "On the Understanding of Mean Radiant Temperature Within Indoor and Outdoor Environments: A Critical Review.",
      venue: "Renewable and Sustainable Energy Reviews",
      year: "2019",
      status: "Published",
      note: ""
    }
  ],
  chapters: [
    {
      authors: "Guo H., Li Y., Zhou Y., Chang Y., Lai C.Y.",
      title:
        "From Open Air to Air-Tight: Analyzing the Ventilation Overhaul in Hong Kong's Wet Markets and Its Implications.",
      venue: "Multiphysics and Multiscale Building Physics, Springer",
      year: "2025",
      status: "Book chapter",
      note: ""
    },
    {
      authors: "Guo H., Coleman J., Gullapalli I.",
      title:
        "Accelerating NZEB Design Optimization Through LLM-Based Standardization and Compliance Checking.",
      venue: "Multiphysics and Multiscale Building Physics, Springer",
      year: "2024",
      status: "Book chapter",
      note: ""
    }
  ],
  proceedings: [
    {
      authors: "He K., Guo H.",
      title:
        "A Temporal Features-Enhanced Mixture-of-Experts Approach for Indoor Temperature Prediction.",
      venue: "ICML 2025 CO-BUILD Workshop",
      year: "2025",
      status: "Oral, first place",
      note: "Smart Building Competition winner."
    },
    {
      authors: "Niu S., Guo H., Ferrara M., Anselmo S.",
      title:
        "Thermal-SAM: Adversarial Prompt-Based Unsupervised Building Segmentation in Thermal Aerial Imagery.",
      venue: "ICML 2025 CO-BUILD Workshop",
      year: "2025",
      status: "Poster, third place",
      note: "Recognized at the NeurIPS 2025 Urban AI Workshop Buildings Challenge."
    },
    {
      authors: "Guo H., Chang Y., Hu D.",
      title:
        "ML-Driven Sensitivity Analysis for Lean HVAC: New Insights from Large-Scale Comfort Data.",
      venue: "ICML 2025 CO-BUILD Workshop",
      year: "2025",
      status: "Poster",
      note: ""
    },
    {
      authors: "Guo H., Zhou Y., Lai C.Y., Ren C.",
      title: "From Open Air to Air-Tight: Ventilation Overhaul in Hong Kong Wet Markets.",
      venue: "IBPC 2024",
      year: "2024",
      status: "Conference paper",
      note: ""
    },
    {
      authors: "Guo H., Coleman J., Gullapalli I.",
      title:
        "Accelerating NZEB Design Optimization Through LLM-Based Standardization and Compliance Checking.",
      venue: "IBPC 2024",
      year: "2024",
      status: "Conference paper",
      note: ""
    }
  ],
  underReview: [
    {
      authors: "Guo H., He K.",
      title:
        "Scenario-Conditioned Actual Meteorological Years (sAMY): A Stochastic Weather Generator Using Multi-Decadal Observations.",
      venue: "Energy and Buildings",
      year: "2026",
      status: "Under review",
      note: "Synthetic weather and scenario conditioning."
    },
    {
      authors: "Guo H., He K.",
      title:
        "Input Quality, Not Statistical Complexity, Determines Climate-Adapted Weather File Fidelity: A Causal Decomposition of Degree-Day Errors.",
      venue: "Energy",
      year: "2026",
      status: "Under review",
      note: "Weather file validation and causal analysis."
    },
    {
      authors: "Guo H., He K.",
      title:
        "Controller-Agnostic Benchmarking Across Five Climates: Comfort, Energy, and Peak Trade-offs to 2100.",
      venue: "Engineering Applications of Artificial Intelligence",
      year: "2025",
      status: "Under review",
      note: "Climate futures benchmarking."
    },
    {
      authors: "Guo H., He K., Xu Y., Shi Z., Aviv D.",
      title:
        "Probabilistic Thermal Comfort for Energy-Efficient Building Control: A Risk-Aware Framework.",
      venue: "Energy Conversion and Management",
      year: "2026",
      status: "Under review",
      note: "Control and learning."
    }
  ]
};

export const teaching = {
  courses: [
    {
      code: "ARCH7476",
      title: "Evidence-Based Generative Design",
      audience: "Mixed MArch, undergraduate, and PhD",
      years: "2025-present",
      href: "https://clementinec.github.io/ARCH7476",
      description:
        "Students frame design problems as testable claims, collect evidence, and build reproducible analyses with strong visual communication artifacts."
    },
    {
      code: "DESN2003",
      title: "Research for Innovation",
      audience: "Undergraduate",
      years: "2023-present",
      href: "https://clementinec.github.io/desn2003",
      description:
        "Research methodology from question framing through evidence gathering to communication, with tracks for frontier research and buildable outputs."
    },
    {
      code: "CCGL9065",
      title: "Our Response to Climate Change | Hong Kong 2100",
      audience: "Undergraduate",
      years: "2024-present",
      href: "https://clementinec.github.io/ccgl9065",
      description:
        "Climate action through critique, debate, and speculative design, culminating in a public interactive art-and-science exhibition."
    }
  ],
  pedagogy:
    "Evidence-based design workflows that combine low-code tools with Python and Colab notebooks, with strong emphasis on reproducibility, uncertainty quantification, and visual communication.",
  prior:
    "Princeton mini-courses on IoT sensing and thermodynamics labs, 2015-2018.",
  prepared:
    "MDes and MDE design science seminars, architecture studios integrating time-based environmental media, building performance, environmental systems, and design engineering methods."
};

export const service = [
  "ASHRAE Research Project 1959-TRP on metabolic rate standards revision, PI, awarded February 2026.",
  "Reviewer for CVPR, ICML and NeurIPS workshops, and journals including Energy and Buildings, Building and Environment, Applied Energy, Energy, Journal of Building Engineering, Sustainable Cities and Society, and Urban Climate.",
  "Co-Chair, Technical Development and Proceedings Integration, CAAD Futures 2025.",
  "Industry collaboration with the Hong Kong Green Building Council and the Electrical and Mechanical Services Department."
];

export const publicScholarship = [
  "Exhibitor and co-author, Social Condenser Extraordinaire: Hong Kong's Municipal Services Buildings, Projecting Future Heritage: A Hong Kong Archive, La Biennale di Venezia collateral event, May-November 2025.",
  "Lead instructor for the public student exhibition Our Response to Climate Change | Hong Kong 2100 at HKU."
];
