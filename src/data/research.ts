import { publications, researchAxes } from "./site";

export interface ResearchPaper {
  id: string;
  authors: string;
  title: string;
  areas: string[];
  venue: string;
  year: string;
  status: string;
  note: string;
  summary?: string;
  doi?: string;
  tags: string[];
}

// These IDs match the CV bibliography. Resolve highlights against the public
// citation records so titles, publication status, and DOI links stay in sync.
const publicPapers: ResearchPaper[] = [
  ...publications.accepted,
  ...publications.journals,
  ...publications.chapters,
  ...publications.proceedings
];
const papersById = new Map<string, ResearchPaper>();
for (const paper of publicPapers) {
  if (!paper.id || papersById.has(paper.id)) {
    throw new Error(`Missing or duplicate publication ID: ${paper.id}`);
  }
  papersById.set(paper.id, paper);
}

type SelectedWork = {
  paperId: string;
  label: string;
  contribution: string;
};

type ProgrammeDetail = {
  question: string;
  connection: string;
  works: SelectedWork[];
};

// Interpretive descriptions follow the author's programme framing; citation
// titles and publication status remain the records from site.ts.
const programmeDetails: Record<string, ProgrammeDetail> = {
  people: {
    question:
      "How can building decisions account for differences in human heat generation and the likelihood of discomfort?",
    connection:
      "Human heat defaults and contextual factors shape how we model thermal response. Predicting the probability of each sensation makes uncertainty in how people feel visible to design and control.",
    works: [
      {
        paperId: "J10",
        label: "Human heat defaults",
        contribution:
          "Re-examines the 120 W/person heat-generation assumption using demographic-aware metabolic rates and their implications for energy demand and thermal comfort."
      },
      {
        paperId: "J07",
        label: "Contextual drivers",
        contribution:
          "Examines sensitivity to thermal comfort drivers and shows how missing-data choices change their apparent importance in learned models."
      },
      {
        paperId: "J06",
        label: "Thermal sensation probabilities",
        contribution:
          "Estimates the probability of each response on the seven-point cold-to-hot scale, making uncertainty in thermal sensation available to design and control decisions."
      }
    ]
  },
  systems: {
    question:
      "How can building control weigh the likelihood of discomfort alongside energy demand and peak loads?",
    connection:
      "Co-simulation connects models of human response to building operation. Model benchmarking and probability-informed supervision then examine the energy and thermal trade-offs that emerge when those models inform system decisions.",
    works: [
      {
        paperId: "J09",
        label: "Co-simulation",
        contribution:
          "Links data-driven thermal sensation models to building energy control, creating a bridge from human-response prediction to testing how systems operate."
      },
      {
        paperId: "A02",
        label: "Model benchmarking",
        contribution:
          "Benchmarks machine-learning and deep-learning sensation models against predicted mean vote across five climates, comparing energy, comfort, and peak-demand trade-offs."
      },
      {
        paperId: "A01",
        label: "HVAC supervision using sensation probabilities",
        contribution:
          "Uses predicted sensation probabilities to inform HVAC supervision and examine delivered-energy and operative-temperature trade-offs across a weather stress grid."
      }
    ]
  },
  climate: {
    question:
      "How should buildings be tested when future weather and the people they serve are changing?",
    connection:
      "The paired sAMY studies examine how climate-adapted weather is generated and what determines its fidelity. The cooling-and-ageing study connects future weather with differences in the thermal outcomes people experience.",
    works: [
      {
        paperId: "J03",
        label: "sAMY: weather generation",
        contribution:
          "Generates scenario-conditioned weather from multi-decadal observations for building performance analysis under climate uncertainty."
      },
      {
        paperId: "J05",
        label: "sAMY: input fidelity",
        contribution:
          "Examines how input quality and statistical complexity affect climate-adapted weather fidelity through a decomposition of degree-day errors."
      },
      {
        paperId: "A03",
        label: "Cooling and ageing",
        contribution:
          "Examines how future weather and population ageing produce different residential thermal outcomes even when cooling setpoints are the same."
      }
    ]
  }
};

const selectedIds = new Set<string>();
export const researchProgramme = researchAxes.map((axis) => {
  const detail = programmeDetails[axis.id];
  if (!detail) {
    throw new Error(`Missing research programme detail: ${axis.id}`);
  }
  return {
    ...axis,
    question: detail.question,
    connection: detail.connection,
    works: detail.works.map((work) => {
      const paper = papersById.get(work.paperId);
      if (!paper) {
        throw new Error(`Missing public citation for research highlight: ${work.paperId}`);
      }
      if (selectedIds.has(work.paperId)) {
        throw new Error(`Duplicate research highlight: ${work.paperId}`);
      }
      selectedIds.add(work.paperId);
      return { ...work, paper };
    })
  };
});

export const selectedResearchIds = new Set(selectedIds);
