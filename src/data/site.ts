export const lab = {
  name: "FORGE",
  longName: "Future, Occupant, Risk, and Generative Environments",
  shortDescription:
    "A design-science lab for human-building-climate systems at The University of Hong Kong.",
  pitch:
    "FORGE studies how buildings and environmental systems perform for actual people across uncertain, climate-stressed futures.",
  why:
    "The lab is built on a simple position: architecture and energy systems have drifted too far from the people they claim to serve. FORGE writes people back into simulation, control, climate risk, and design reasoning.",
  pillars: [
    "Future-facing weather, control, and resilience modeling for buildings and cities.",
    "Occupant-centered evidence that treats comfort, equity, and behavior as central design variables.",
    "Risk-aware and generative computational methods that remain legible to designers."
  ]
};

export const homeTeamSummary =
  "FORGE is a compact research group spanning a postdoctoral researcher, PhD students, research assistants on site at HKU and remote locations, and undergraduate RAs. The team is currently working across ASHRAE 1959-TRP on updating real human heat assumptions, climate stress-testing and stochastic future weather modeling, ordinal thermal comfort, and Socratic Oracle as a design-pedagogy platform.";

export const homeFocus = {
  intro:
    "The current agenda is concentrated around standards revision, future weather uncertainty, thermal comfort prediction, and AI-supported design pedagogy.",
  items: [
    "ASHRAE 1959-TRP",
    "Human Heat Standards",
    "Climate Stress-Testing",
    "Ordinal Thermal Comfort",
    "Risk-Aware Control",
    "Socratic Oracle"
  ]
};

export const homeWork = {
  intro:
    "FORGE moves between building simulation, comfort science, climate futures, and design-facing AI through a small set of recurring technical workflows.",
  methods: [
    "EnergyPlus",
    "Climate Forcing",
    "Monte Carlo",
    "Physics-Informed Neural Networks",
    "Mean Radiant Temperature",
    "ERA5 / CMIP6",
    "Hidden Markov Models",
    "State-Based Inference",
    "Ordinal Learning",
    "Co-Simulation",
    "Stochastic Weather",
    "Sensitivity Analysis"
  ]
};

const avatarPalettes = [
  { bg: "#f6aaa8", bust: "#fff4dd", accent: "#a8d4ee", text: "#111111" },
  { bg: "#f7c782", bust: "#fff4dd", accent: "#f6aaa8", text: "#111111" },
  { bg: "#a8d4ee", bust: "#fff4dd", accent: "#f7c782", text: "#111111" },
  { bg: "#fff4dd", bust: "#f6aaa8", accent: "#a8d4ee", text: "#111111" }
];

const svgToDataUri = (svg: string) =>
  `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;

function makePlaceholderAvatar(name: string, variant: number) {
  const palette = avatarPalettes[variant % avatarPalettes.length];
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" role="img" aria-label="Placeholder avatar for ${name}">
      <rect width="160" height="160" rx="30" fill="${palette.bg}" />
      <rect x="16" y="16" width="128" height="128" rx="24" fill="${palette.bust}" />
      <circle cx="54" cy="56" r="20" fill="${palette.accent}" opacity="0.9" />
      <circle cx="110" cy="44" r="14" fill="${palette.bg}" opacity="0.95" />
      <path d="M26 116c18-18 38-28 60-28c17 0 33 5 48 16v24H26z" fill="${palette.accent}" />
      <path d="M40 128c13-10 26-15 42-15c13 0 26 4 40 13" fill="none" stroke="${palette.text}" stroke-width="6" stroke-linecap="round" opacity="0.28" />
    </svg>
  `;
  return svgToDataUri(svg);
}

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

export const team = {
  principalInvestigator: {
    name: "Hongshan Guo",
    role: "Principal Investigator",
    avatar: "/images/profile.png",
    detail:
      "Assistant Professor, Department of Architecture, The University of Hong Kong.",
    bio:
      "Works across human-building-climate systems, probabilistic modeling, physics-informed machine learning, co-simulation, and design-facing AI."
  },
  collaborators: [
    {
      name: "Xinting Gao",
      role: "Postdoctoral Researcher",
      avatar: "/images/xinting-gao.jpg",
      detail: "FORGE, HKU",
      bio:
        "Focuses on building energy systems under climate change."
    },
    {
      name: "Yu Chang",
      role: "PhD Student",
      avatar: "/images/yu-chang.jpg",
      detail: "HKU, 2024-present",
      bio:
        "Studies cross-cultural thermal comfort and indoor CO₂, with interests in data harmonization, spatial distribution, and occupancy-related dynamics."
    },
    {
      name: "Kanxuan He",
      role: "PhD Student",
      avatar: "/images/kanxuan-he.jpg",
      detail: "HKU, 2025-present",
      bio:
        "Focuses on climate resilience and thermal dynamics through interpretable modeling."
    },
    {
      name: "Yizhi Liang",
      role: "Research Assistant",
      avatar: "/images/yizhi-liang.jpg",
      detail: "Master's student in Mechanical Engineering, FORGE, 2025-present",
      bio:
        "Contributes to the ASHRAE 1959-TRP project on updating real human load assumptions, supporting data, analysis, and modeling work at FORGE."
    },
    {
      name: "Di Zhang",
      role: "Research Assistant",
      avatar: "/images/di-zhang.jpg",
      detail: "FORGE, 2026-present",
      bio:
        "Works on ordinal thermal comfort, supporting risk-aware comfort modeling and related analysis at FORGE."
    },
    {
      name: "Shunuke Sani",
      role: "PhD Student / Research Assistant",
      avatar: "/images/shunuke-sani.jpg",
      detail: "DUPAD, HKU and FORGE, 2026-present",
      bio:
        "Focuses on architectural education AI and urban pedestrian mobility and trajectory research."
    },
    {
      name: "Akshay Thanipet Padmanabhan",
      role: "Undergraduate Research Assistant",
      avatar: "/images/akshay-thanipet-padmanabhan.png",
      detail: "FORGE, 2026-present",
      bio:
        "Works on the technical implementation and scaling up of Socratic Oracle through the TDLEG grant."
    },
    {
      name: "Samanyu Gaur",
      role: "Undergraduate Research Assistant",
      avatar: "/images/samanyu-gaur.JPG",
      detail: "FORGE, 2026-present",
      bio:
        "Works on the technical implementation and scaling up of Socratic Oracle through the TDLEG grant."
    }
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
    title: "Human heat, comfort, and standards",
    text:
      "Research here spans demographic metabolic rates, MRT-aware comfort analysis, ordinal prediction, and physiology-constrained models. The through-line is to replace abstract default occupants with measurable human heat and comfort response."
  },
  {
    title: "Climate futures and stochastic weather",
    text:
      "FORGE studies how future weather assumptions alter building performance using climate forcing, ERA5 or CMIP chains, stochastic generation, and uncertainty propagation. The goal is not just future files, but defensible stress-tests for design and operation."
  },
  {
    title: "Operation, ventilation, and design-facing systems",
    text:
      "Work extends from EnergyPlus co-simulation and risk-aware control to wet-market ventilation retrofits and AI-supported pedagogy platforms. The point is to turn models into operational, institutional, and design tools rather than leaving them as standalone predictions."
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
    area: "Thermal comfort, human heat, and MRT",
    items: [
      "Ordinal and probabilistic thermal comfort prediction from seven-point sensation votes",
      "Physics-informed neural networks with physiological constraints",
      "Mean radiant temperature sensitivity analysis for HVAC control",
      "Demographic-aware metabolic-rate modeling and ASHRAE standards revision",
      "Fan-assisted cooling, gender differences, and cross-cultural comfort evidence"
    ]
  },
  {
    area: "Climate forcing, weather futures, and uncertainty",
    items: [
      "Climate-adapted weather file evaluation using causal decomposition of degree-day errors",
      "Scenario-conditioned and stochastic weather generation from long observational records",
      "ERA5 / CMIP6 forcing chains for climate stress-testing",
      "Monte Carlo propagation and uncertainty benchmarking across future scenarios",
      "Building performance evaluation under climate-stressed futures through 2100"
    ]
  },
  {
    area: "Control, co-simulation, and interpretable learning",
    items: [
      "EnergyPlus-based co-simulation for occupant-aware building control",
      "Risk-aware control framing from probabilistic comfort outputs",
      "Interpretable ML, feature attribution, and sensitivity tracing",
      "Indoor temperature forecasting and competition-tested predictive workflows",
      "Digital twins that connect learned models to operational testing"
    ]
  },
  {
    area: "Ventilation, public institutions, and design-facing AI",
    items: [
      "Wet-market ventilation retrofits and IEQ-energy trade-off analysis",
      "Field measurement in mixed-mode and public-building contexts",
      "Design pedagogy systems such as Socratic Oracle and AI Design Coach",
      "Evidence-based generative design workflows for architecture education",
      "Research legible to design studios, standards work, and public-sector collaboration"
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
  "ASHRAE Research Project 1959-TRP, PI, awarded February 2026 and commencing April 2026.",
  "Teaching Development and Language Enhancement Grant, HKU, PI, Socratic Oracle (2025-2028).",
  "Teaching Development Grant, HKU, PI, AI Design Coach (2026-2028).",
  "ICML 2025 CO-BUILD Smart Building Competition, first place as faculty mentor and author.",
  "NeurIPS 2025 Urban AI Workshop Buildings Challenge, third place as faculty mentor.",
  "Gartner Eye on Innovation Award, BNY Mellon, 2021.",
  "Lowry Methodology Award, International Conference of Urban Climate, 2018."
];

export const publications = {
  journals: [
    {
      authors: "Hongshan Guo, Dorit Aviv",
      title:
        "From Seven Points to Probabilities: Ordinal Learning for Risk-Aware Thermal Comfort Prediction.",
      venue: "Building and Environment",
      year: "2026",
      status: "Published",
      note: "Ordinal learning, risk-aware prediction.",
      summary:
        "Reframes thermal sensation prediction as an ordinal learning problem with calibrated probabilities for risk-aware comfort decisions. The model yields confidence-aware outputs that are more useful for control and design decisions under uncertainty than a flat seven-point label alone.",
      doi: "https://doi.org/10.1016/j.buildenv.2026.114426",
      tags: ["thermal comfort", "control"]
    },
    {
      authors: "Hongshan Guo, Ilaria Pigliautile, Yu Chang, Qingyao Qiao, Yichun Li",
      title:
        "Toward Smarter HVAC Control: Machine Learning Reveals Hidden Drivers in Thermal Comfort Databases.",
      venue: "Energy and AI",
      year: "2026",
      status: "Published",
      note: "Sensitivity analysis, MRT, and data quality.",
      summary:
        "Shows how missing-data policy reshapes feature sensitivity rankings and supports MRT-aware, occupant-centric HVAC control. The paper makes clear that preprocessing decisions materially affect what machine-learning models appear to learn from thermal comfort databases.",
      doi: "https://doi.org/10.1016/j.egyai.2026.100709",
      tags: ["thermal comfort", "control", "energy"]
    },
    {
      authors: "Chao Cen, Hongshan Guo, Lup Wai Chew, Nyuk Hien Wong",
      title:
        "Experimental Study on Gender Differences in Thermal Comfort and Physiological Responses in Fan-Assisted Cooling Environments.",
      venue: "Energy and Buildings",
      year: "2026",
      status: "Published",
      note: "Fan-assisted cooling, gender differences, and tropical mixed-mode comfort.",
      summary:
        "Finds that gender differences become most pronounced under high-velocity cooling at lower temperatures, with implications for equitable fan-cooling design. By connecting subjective votes with skin-temperature responses, the study shows why mixed-mode cooling strategies should not assume uniform comfort response.",
      doi: "https://doi.org/10.1016/j.enbuild.2026.117365",
      tags: ["thermal comfort", "human heat"]
    },
    {
      authors: "Hongshan Guo, Kanxuan He",
      title:
        "Input Quality, Not Statistical Complexity, Determines Climate-Adapted Weather File Fidelity: A Causal Decomposition of Degree-Day Errors.",
      venue: "Energy",
      year: "2026",
      status: "Published",
      note: "Weather file validation and causal analysis.",
      summary:
        "Shows that weather-file baseline quality dominates future demand bias, outperforming more complex workflows for climate-adapted energy projections. Rather than rewarding statistical complexity for its own sake, the paper identifies input fidelity as the main determinant of robust downstream building simulation.",
      doi: "https://doi.org/10.1016/j.energy.2026.140867",
      tags: ["climate", "energy"]
    },
    {
      authors:
        "Hongshan Guo, Yu Chang, Yichun Li, Ying Zhou, Qingyao Qiao, Chun Yin Lai, Eric Schuldenfrei",
      title:
        "Ventilation-Energy Trade-offs in Retrofitted Hong Kong Wet Markets.",
      venue: "Energy and Buildings",
      year: "2026",
      status: "Published",
      note: "Field measurement and IEQ-energy retrofit trade-offs.",
      summary:
        "Combines field diagnostics and cross-climate simulation to quantify ventilation, comfort, and energy trade-offs in retrofitted Hong Kong wet markets. It frames wet-market modernization as both a building-performance problem and a public-institution design question.",
      doi: "https://doi.org/10.1016/j.enbuild.2025.116918",
      tags: ["ventilation", "energy", "climate"]
    },
    {
      authors: "Hongshan Guo, Ruiji Sun, Youmin Xu",
      title:
        "Correcting the 120-Watt Assumption: Demographic-Aware Metabolic Rates for Energy Savings and Thermal Comfort Equity in Buildings.",
      venue: "Energy and Buildings",
      year: "2025",
      status: "Published",
      note: "Standards impact and equity; prompted ASHRAE 1959-TRP.",
      summary:
        "Demonstrates that demographic-aware metabolic loads can cut HVAC energy use and reduce gender-based comfort bias relative to the legacy 120 W/person assumption. The work directly challenged a century-old default embedded in standards and helped motivate ASHRAE 1959-TRP.",
      doi: "https://doi.org/10.1016/j.enbuild.2025.116525",
      tags: ["human heat", "energy"]
    },
    {
      authors: "Hongshan Guo, Kanxuan He, Youmin Xu, Yue Lei",
      title:
        "A Co-Simulation Methodology for Integrating Data-Driven Thermal Sensation Models with Building Energy Control.",
      venue: "Energy and Buildings",
      year: "2026",
      status: "Published",
      note: "Digital twins, co-simulation, and validation across 13 climates.",
      summary:
        "Integrates data-driven thermal sensation models with building control workflows to benchmark occupant-aware control across multiple climates. It shows how co-simulation can move comfort models from offline prediction into actionable control testing.",
      doi: "https://doi.org/10.1016/j.enbuild.2025.116745",
      tags: ["thermal comfort", "control", "climate"]
    },
    {
      authors: "Hongshan Guo, Kanxuan He, Yongqiang Luo, Yu Chang",
      title:
        "Physics-Informed Neural Networks for Robust Thermal Comfort Prediction: Overcoming Data Quality Limitations Through Physiological Constraints.",
      venue: "Building and Environment",
      year: "2025",
      status: "Published",
      note: "PINNs and physiological constraints.",
      summary:
        "Uses physiological constraints inside a neural model to improve robustness and interpretability in large-scale thermal comfort prediction. The approach treats building-comfort ML as a physically informed modeling problem rather than a purely statistical fitting exercise.",
      doi: "https://doi.org/10.1016/j.buildenv.2025.113588",
      tags: ["thermal comfort", "human heat"]
    },
    {
      authors: "Yu Chang, Hongshan Guo, Yichun Li, Ilaria Pigliautile, Binlin Chi",
      title:
        "A Data-Driven Qualitative Review of Thermal Comfort Studies: Bridging the Gap Between Western and Eastern Perspectives.",
      venue: "Renewable and Sustainable Energy Reviews",
      year: "2025",
      status: "Published",
      note: "Data harmonization and benchmark framing.",
      summary:
        "Reviews how comfort studies use personal, contextual, and PMV-related variables, highlighting gaps that limit cross-cultural comparison and model transfer. It also establishes a benchmark-oriented framing for comparing Eastern and Western comfort evidence more systematically.",
      doi: "https://doi.org/10.1016/j.rser.2025.116020",
      tags: ["thermal comfort", "climate"]
    }
  ],
  chapters: [
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
      authors: "Guo H., Li Y., Zhou Y., Chang Y., Lai C.Y.",
      title:
        "From Open Air to Air-Tight: Analyzing the Ventilation Overhaul in Hong Kong's Wet Markets and Its Implications.",
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
