"""
Tool definitions and executor for the AI Executive Search Associate.
15 tools covering the full executive recruiting workflow.

Tool categories:
  1. Candidate Sourcing      — source_candidates, build_boolean_search, candidate_market_map
  2. Profile Analysis        — analyze_resume, evaluate_fit, candidate_scorecard
  3. Candidate Communication — draft_outreach, outreach_personalization
  4. Interview Preparation   — generate_interview_questions, interview_strategy
  5. Summaries & Shortlists  — summarize_interview, create_shortlist
  6. Compensation            — compensation_analysis
  7. Job Definition          — job_brief_builder
  8. Strategic Intelligence  — talent_insight
"""

import json

# ── Tool schemas ───────────────────────────────────────────────────────────────

TOOLS: list[dict] = [

    # ── 1. CANDIDATE SOURCING ─────────────────────────────────────────────────

    {
        "name": "source_candidates",
        "description": (
            "Build an ideal candidate profile and end-to-end sourcing strategy for an executive role. "
            "Returns a structured profile with required skills, years of experience, career trajectory, "
            "target companies to poach from, and recommended sourcing channels "
            "(LinkedIn Recruiter, headhunting communities, alumni networks, etc.). "
            "Supports analysis in Portuguese, English, and Spanish."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_title": {"type": "string", "description": "Title of the role (e.g. CFO, VP Engineering)"},
                "company": {"type": "string", "description": "Hiring company name"},
                "industry": {"type": "string", "description": "Industry or sector (e.g. fintech, healthtech, retail)"},
                "geography": {"type": "string", "description": "Location or market (e.g. Brazil, LATAM, São Paulo)"},
                "company_stage": {
                    "type": "string",
                    "enum": ["Startup", "Series A", "Series B", "Series C+", "Scale-up", "Enterprise", "PE-backed", "Public"],
                    "description": "Stage of the hiring company",
                },
                "key_responsibilities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Main responsibilities of the role",
                },
                "seniority_level": {
                    "type": "string",
                    "enum": ["C-Suite", "VP", "Director", "Senior Manager", "Partner", "Board"],
                    "description": "Seniority level of the position",
                },
                "must_have_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Non-negotiable requirements",
                },
                "language": {
                    "type": "string",
                    "enum": ["pt", "en", "es"],
                    "description": "Language for the output (default: match user's language)",
                },
            },
            "required": ["job_title", "industry"],
        },
    },

    {
        "name": "build_boolean_search",
        "description": (
            "Generate advanced Boolean search strings optimized for LinkedIn Recruiter, "
            "LinkedIn Sales Navigator, and Google X-Ray searches. "
            "Creates multiple search variants for different levels of specificity. "
            "Useful for finding passive candidates in any market."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_title": {"type": "string", "description": "Target role title"},
                "required_skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Must-have skills or keywords",
                },
                "target_companies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Companies to source from",
                },
                "seniority_level": {
                    "type": "string",
                    "description": "Seniority keywords (e.g. VP, Director, Head of, Chief)",
                },
                "location": {
                    "type": "string",
                    "description": "Target location or region",
                },
                "industry_keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Industry-specific keywords to include",
                },
                "exclude_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Terms to exclude from results",
                },
            },
            "required": ["job_title"],
        },
    },

    {
        "name": "candidate_market_map",
        "description": (
            "Map the talent market for a specific role, industry, or geography. "
            "Identifies: top feeder companies, talent hotspots, competitor hiring patterns, "
            "talent pools by seniority level, and recommended search strategy. "
            "Essential for understanding where the best candidates come from."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Target role or function (e.g. CFO, Head of Sales)"},
                "industry": {"type": "string", "description": "Industry or sector to map"},
                "geography": {
                    "type": "string",
                    "description": "Geographic scope (e.g. Brazil, LATAM, São Paulo metro)",
                },
                "company_stage": {
                    "type": "string",
                    "description": "Stage filter for target candidates' current companies",
                },
                "depth": {
                    "type": "string",
                    "enum": ["overview", "detailed"],
                    "description": "Overview: top-line map. Detailed: deep dive with sub-segments.",
                },
                "additional_context": {
                    "type": "string",
                    "description": "Any specific focus areas or constraints for the mapping",
                },
            },
            "required": ["role", "industry"],
        },
    },

    # ── 2. PROFILE ANALYSIS ───────────────────────────────────────────────────

    {
        "name": "analyze_resume",
        "description": (
            "Parse and analyze a candidate's resume, CV, or LinkedIn profile text. "
            "Extracts and structures: career timeline, companies, roles and tenure, "
            "promotions, education, key achievements, skills, and career trajectory narrative. "
            "Works with documents in Portuguese, English, or Spanish."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "resume_text": {
                    "type": "string",
                    "description": "Full text of the resume, CV, or LinkedIn profile",
                },
                "candidate_name": {
                    "type": "string",
                    "description": "Name of the candidate (if known)",
                },
                "source": {
                    "type": "string",
                    "enum": ["resume", "cv", "linkedin", "other"],
                    "description": "Source type of the profile data",
                },
            },
            "required": ["resume_text"],
        },
    },

    {
        "name": "evaluate_fit",
        "description": (
            "Evaluate how well a candidate matches a specific role. "
            "Returns: overall fit score (0–100), dimension scores (experience, leadership, "
            "culture, technical, sector), detailed strengths and gaps analysis, "
            "key risks, and a clear hire/no-hire/conditional recommendation with rationale."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "candidate_profile": {
                    "type": "string",
                    "description": "Candidate background, experience, and skills summary",
                },
                "job_description": {
                    "type": "string",
                    "description": "Full job description or role requirements",
                },
                "must_have_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Non-negotiable requirements (automatic disqualifiers if missing)",
                },
                "nice_to_have_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Preferred but not required criteria",
                },
                "company_culture": {
                    "type": "string",
                    "description": "Description of the company culture and values for culture fit assessment",
                },
            },
            "required": ["candidate_profile", "job_description"],
        },
    },

    {
        "name": "candidate_scorecard",
        "description": (
            "Generate a competency-based scorecard for structured candidate evaluation. "
            "Scores each competency on a 1–5 scale with evidence-based rationale. "
            "Produces a consistent evaluation framework that can be compared across candidates. "
            "Ideal for panel interviews and structured hiring processes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "candidate_name": {"type": "string", "description": "Candidate's full name"},
                "candidate_profile": {
                    "type": "string",
                    "description": "Candidate background, CV summary, or interview notes",
                },
                "competencies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Competency name"},
                            "description": {"type": "string", "description": "What this competency means for the role"},
                            "weight": {"type": "number", "description": "Importance weight 0–1 (optional)"},
                        },
                        "required": ["name"],
                    },
                    "description": "List of competencies to evaluate",
                },
                "role_context": {
                    "type": "string",
                    "description": "Role and company context to calibrate scoring",
                },
            },
            "required": ["candidate_profile", "competencies"],
        },
    },

    # ── 3. CANDIDATE COMMUNICATION ────────────────────────────────────────────

    {
        "name": "draft_outreach",
        "description": (
            "Draft a personalized outreach message to a passive candidate. "
            "Creates a professional, compelling message that highlights the opportunity "
            "without overselling. Tone is warm and peer-to-peer, not salesy. "
            "Supports LinkedIn InMail, email, and WhatsApp formats."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "candidate_name": {"type": "string", "description": "Candidate's first name or full name"},
                "candidate_current_role": {
                    "type": "string",
                    "description": "Candidate's current title and company",
                },
                "opportunity_title": {"type": "string", "description": "Title of the open role"},
                "hiring_company": {"type": "string", "description": "Hiring company name"},
                "key_selling_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Why this opportunity is attractive (growth, mission, comp, brand, etc.)",
                },
                "channel": {
                    "type": "string",
                    "enum": ["LinkedIn", "Email", "WhatsApp"],
                    "description": "Communication channel",
                },
                "language": {
                    "type": "string",
                    "enum": ["pt", "en", "es"],
                    "description": "Language for the outreach message",
                },
            },
            "required": ["candidate_name", "opportunity_title", "hiring_company"],
        },
    },

    {
        "name": "outreach_personalization",
        "description": (
            "Create a hyper-personalized outreach message by referencing specific details "
            "from the candidate's profile, achievements, and career story. "
            "Goes beyond generic outreach — references specific projects, companies they built, "
            "awards, publications, or career moves that show you've done your homework. "
            "Much higher response rates than standard outreach."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "candidate_name": {"type": "string", "description": "Candidate's name"},
                "candidate_profile": {
                    "type": "string",
                    "description": "Full LinkedIn profile text, CV, or detailed background",
                },
                "specific_achievements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific achievements, projects, or career highlights to reference",
                },
                "opportunity_title": {"type": "string", "description": "Title of the open role"},
                "hiring_company": {"type": "string", "description": "Hiring company name"},
                "value_proposition": {
                    "type": "string",
                    "description": "Why this specific opportunity is a logical next step for this candidate",
                },
                "channel": {
                    "type": "string",
                    "enum": ["LinkedIn", "Email", "WhatsApp"],
                    "description": "Communication channel (affects length and format)",
                },
                "language": {
                    "type": "string",
                    "enum": ["pt", "en", "es"],
                    "description": "Language for the message",
                },
            },
            "required": ["candidate_name", "candidate_profile", "opportunity_title", "hiring_company"],
        },
    },

    # ── 4. INTERVIEW PREPARATION ──────────────────────────────────────────────

    {
        "name": "generate_interview_questions",
        "description": (
            "Generate a tailored set of interview questions for a specific candidate and role. "
            "Produces behavioral (STAR format), technical/functional, situational, "
            "and culture-fit questions. Questions are calibrated to the seniority level "
            "and the candidate's specific background to probe the right areas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Job title or role being interviewed for"},
                "candidate_background": {
                    "type": "string",
                    "description": "Brief summary of candidate's background and experience",
                },
                "focus_areas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific competencies or areas to probe",
                },
                "red_flags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Potential concerns or gaps to investigate",
                },
                "num_questions": {
                    "type": "integer",
                    "description": "Total number of questions to generate (default: 12)",
                },
                "interview_stage": {
                    "type": "string",
                    "enum": ["screening", "first_round", "final_round", "panel", "board"],
                    "description": "Interview stage (affects depth and format of questions)",
                },
            },
            "required": ["role"],
        },
    },

    {
        "name": "interview_strategy",
        "description": (
            "Create a structured interview strategy and flow for an executive interview. "
            "Defines: interview objectives, opening/rapport building, discovery questions, "
            "technical/functional validation, leadership assessment, culture fit probes, "
            "red flag investigation, candidate's questions phase, and evaluation gates. "
            "Includes time allocation and interviewer guidance notes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Role being interviewed for"},
                "candidate_background": {
                    "type": "string",
                    "description": "Summary of candidate's background",
                },
                "interview_stage": {
                    "type": "string",
                    "enum": ["screening", "first_round", "final_round", "panel", "board"],
                    "description": "Stage of the interview process",
                },
                "competencies_to_assess": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key competencies to evaluate in this interview",
                },
                "red_flags_to_probe": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific concerns or gaps to investigate",
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "Total interview duration in minutes (default: 60)",
                },
                "interviewer_profile": {
                    "type": "string",
                    "description": "Who is conducting the interview (CEO, HR, panel, etc.)",
                },
            },
            "required": ["role", "interview_stage"],
        },
    },

    # ── 5. SUMMARIES & SHORTLISTS ─────────────────────────────────────────────

    {
        "name": "summarize_interview",
        "description": (
            "Convert raw interview notes or a transcript into a structured recruiter summary. "
            "Produces: executive summary, key highlights, competency assessments, "
            "cultural alignment, concerns and risks, compensation expectations, "
            "availability and motivation, and overall recommendation. "
            "Ready-to-send to the client or hiring team."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "candidate_name": {"type": "string", "description": "Candidate's full name"},
                "role": {"type": "string", "description": "Role interviewed for"},
                "interview_notes": {
                    "type": "string",
                    "description": "Raw interview notes, transcript, or observations",
                },
                "interview_stage": {
                    "type": "string",
                    "enum": ["screening", "first_round", "final_round", "panel"],
                    "description": "Stage of the interview",
                },
                "interviewer": {
                    "type": "string",
                    "description": "Name/role of the interviewer",
                },
                "interview_date": {
                    "type": "string",
                    "description": "Date of the interview (YYYY-MM-DD)",
                },
            },
            "required": ["candidate_name", "interview_notes"],
        },
    },

    {
        "name": "create_shortlist",
        "description": (
            "Generate a formatted candidate shortlist for a role. "
            "Compares candidates side-by-side with: fit score, key highlights, "
            "strengths and gaps, compensation expectations, availability, "
            "key risks, and a recommended ranking with rationale. "
            "Ready to be shared with the hiring manager or client."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Role for the shortlist"},
                "company": {"type": "string", "description": "Hiring company"},
                "candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "current_role": {"type": "string"},
                            "profile_summary": {"type": "string"},
                            "fit_score": {"type": "number", "description": "Score 0–100"},
                            "comp_expectation": {"type": "string"},
                            "availability": {"type": "string"},
                            "key_strengths": {"type": "array", "items": {"type": "string"}},
                            "risks": {"type": "array", "items": {"type": "string"}},
                            "notes": {"type": "string"},
                        },
                        "required": ["name"],
                    },
                    "description": "List of candidates to include in the shortlist",
                },
                "shortlist_size": {
                    "type": "integer",
                    "description": "Number of candidates to include in the final shortlist",
                },
                "ranking_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Criteria used to rank candidates",
                },
            },
            "required": ["role", "candidates"],
        },
    },

    # ── 6. COMPENSATION BENCHMARKING ─────────────────────────────────────────

    {
        "name": "compensation_analysis",
        "description": (
            "Analyze and benchmark compensation structures for executive roles. "
            "Compares base salary, variable bonus, OTE, equity (options/RSU), "
            "and total compensation across candidates or against market benchmarks. "
            "Provides recommendations for competitive offer structuring. "
            "Supports multiple currencies (BRL, USD, EUR)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Role title for benchmarking"},
                "market": {
                    "type": "string",
                    "description": "Geographic market (e.g. Brazil, São Paulo, US, Europe)",
                },
                "industry": {"type": "string", "description": "Industry for benchmark calibration"},
                "company_stage": {
                    "type": "string",
                    "description": "Company stage (affects equity/bonus structures)",
                },
                "candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "base_salary": {"type": "number"},
                            "variable_bonus": {"type": "number"},
                            "equity": {"type": "string", "description": "Equity details (options, RSU, %)"},
                            "benefits": {"type": "string"},
                            "current_total": {"type": "number"},
                            "expectation": {"type": "string"},
                        },
                        "required": ["name"],
                    },
                    "description": "Candidate compensation data to compare",
                },
                "budget_range": {
                    "type": "string",
                    "description": "Hiring company's compensation budget range",
                },
                "currency": {
                    "type": "string",
                    "enum": ["BRL", "USD", "EUR", "GBP"],
                    "description": "Primary currency for analysis (default: BRL)",
                },
            },
            "required": ["role"],
        },
    },

    # ── 7. JOB DEFINITION ────────────────────────────────────────────────────

    {
        "name": "job_brief_builder",
        "description": (
            "Transform a client briefing or intake notes into a structured job description "
            "and comprehensive hiring strategy. Produces: role overview, key responsibilities, "
            "success metrics (30/60/90 day), required qualifications, ideal candidate profile, "
            "interview process design, and sourcing strategy. "
            "Used at the start of a new search engagement."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Client company name"},
                "company_context": {
                    "type": "string",
                    "description": "Company background, stage, culture, challenges",
                },
                "role_title": {"type": "string", "description": "Title of the role"},
                "reporting_to": {
                    "type": "string",
                    "description": "Who the role reports to",
                },
                "team_size": {
                    "type": "string",
                    "description": "Size of team the candidate will lead or join",
                },
                "key_objectives": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Main goals and objectives for the role in year 1",
                },
                "success_metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "How success will be measured (KPIs, OKRs)",
                },
                "budget_range": {
                    "type": "string",
                    "description": "Total compensation budget range",
                },
                "timeline": {
                    "type": "string",
                    "description": "Desired start date or urgency level",
                },
                "location_type": {
                    "type": "string",
                    "enum": ["On-site", "Hybrid", "Remote", "Flexible"],
                    "description": "Work arrangement",
                },
                "dealbreakers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Absolute disqualifiers for the role",
                },
            },
            "required": ["company_name", "role_title"],
        },
    },

    # ── 8. STRATEGIC INTELLIGENCE ────────────────────────────────────────────

    {
        "name": "talent_insight",
        "description": (
            "Analyze talent patterns, hiring trends, and candidate positioning across "
            "markets, roles, and companies. Answers strategic questions like: "
            "'Where do the best CFOs in Brazilian fintechs come from?', "
            "'Which companies produce the strongest CTOs for scale-ups?', "
            "'How competitive is the VP Sales talent market in LATAM?', "
            "'How should a candidate position their background for a PE-backed company?'. "
            "Provides market intelligence to inform sourcing strategy and client advisory."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "analysis_type": {
                    "type": "string",
                    "enum": [
                        "talent_mapping",
                        "hiring_trends",
                        "company_analysis",
                        "candidate_positioning",
                        "market_competitiveness",
                        "feeder_companies",
                    ],
                    "description": "Type of strategic analysis to perform",
                },
                "role": {"type": "string", "description": "Target role or function"},
                "industry": {"type": "string", "description": "Industry or sector to analyze"},
                "geography": {
                    "type": "string",
                    "description": "Geographic scope (e.g. Brazil, LATAM, São Paulo)",
                },
                "company_stage": {
                    "type": "string",
                    "description": "Target company stage for context",
                },
                "target_companies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific companies to include in the analysis",
                },
                "question": {
                    "type": "string",
                    "description": "The specific strategic question to answer",
                },
                "context": {
                    "type": "string",
                    "description": "Additional context for the analysis",
                },
            },
            "required": ["analysis_type", "industry"],
        },
    },
]


# ── Tool executor ──────────────────────────────────────────────────────────────

def execute_tool(name: str, tool_input: dict) -> str:
    """
    Execute a tool call and return a JSON string result.

    Current implementation: returns structured confirmation of inputs received.
    Claude uses these inputs as context to generate the actual analysis.

    In production, replace each handler with real integrations:
    - LinkedIn Recruiter / Sales Navigator API
    - ATS (Greenhouse, Lever, Workable)
    - Internal resume/candidate database
    - Compensation databases (Radford, Mercer, local market data)
    - CRM (Salesforce, HubSpot for client management)
    """

    # Sourcing tools
    if name == "source_candidates":
        return json.dumps({
            "status": "ok",
            "tool": "source_candidates",
            "received": {
                "job_title": tool_input.get("job_title"),
                "industry": tool_input.get("industry"),
                "geography": tool_input.get("geography", "not specified"),
                "seniority_level": tool_input.get("seniority_level", "not specified"),
                "company_stage": tool_input.get("company_stage", "not specified"),
                "must_have_criteria": tool_input.get("must_have_criteria", []),
                "key_responsibilities": tool_input.get("key_responsibilities", []),
            },
            "instruction": (
                "Use these parameters to generate a comprehensive ideal candidate profile "
                "and sourcing strategy, including target companies, talent pools, and channels."
            ),
        })

    elif name == "build_boolean_search":
        return json.dumps({
            "status": "ok",
            "tool": "build_boolean_search",
            "received": {
                "job_title": tool_input.get("job_title"),
                "required_skills": tool_input.get("required_skills", []),
                "target_companies": tool_input.get("target_companies", []),
                "seniority_level": tool_input.get("seniority_level", ""),
                "location": tool_input.get("location", ""),
                "exclude_terms": tool_input.get("exclude_terms", []),
            },
            "instruction": (
                "Generate 3 Boolean search strings: "
                "(1) Broad - LinkedIn Recruiter, "
                "(2) Targeted - LinkedIn Sales Navigator, "
                "(3) X-Ray - Google site:linkedin.com search. "
                "Each should use proper Boolean operators (AND, OR, NOT, quotes, parentheses)."
            ),
        })

    elif name == "candidate_market_map":
        return json.dumps({
            "status": "ok",
            "tool": "candidate_market_map",
            "received": {
                "role": tool_input.get("role"),
                "industry": tool_input.get("industry"),
                "geography": tool_input.get("geography", "not specified"),
                "company_stage": tool_input.get("company_stage", "not specified"),
                "depth": tool_input.get("depth", "overview"),
            },
            "instruction": (
                "Generate a comprehensive talent market map including: "
                "top feeder companies by tier, talent pool sizing, "
                "key hiring patterns, recommended target list, and search strategy."
            ),
        })

    # Profile analysis tools
    elif name == "analyze_resume":
        text = tool_input.get("resume_text", "")
        return json.dumps({
            "status": "ok",
            "tool": "analyze_resume",
            "received": {
                "candidate_name": tool_input.get("candidate_name", "Unknown"),
                "source": tool_input.get("source", "resume"),
                "text_length": len(text),
                "resume_text": text,
            },
            "instruction": (
                "Analyze the provided resume/profile text and extract: "
                "structured career timeline, total years of experience, company progression, "
                "role evolution, promotions, education, key achievements with metrics, "
                "technical skills, and overall career trajectory narrative."
            ),
        })

    elif name == "evaluate_fit":
        return json.dumps({
            "status": "ok",
            "tool": "evaluate_fit",
            "received": {
                "candidate_profile": tool_input.get("candidate_profile"),
                "job_description": tool_input.get("job_description"),
                "must_have_criteria": tool_input.get("must_have_criteria", []),
                "nice_to_have_criteria": tool_input.get("nice_to_have_criteria", []),
                "company_culture": tool_input.get("company_culture", "not specified"),
            },
            "instruction": (
                "Evaluate fit with: overall score (0-100), dimension scores "
                "(experience fit, leadership fit, cultural fit, technical fit, sector fit), "
                "top 3 strengths, top 3 gaps, key risks, must-have criteria check, "
                "and final recommendation: STRONG FIT / FIT / CONDITIONAL / NO FIT."
            ),
        })

    elif name == "candidate_scorecard":
        return json.dumps({
            "status": "ok",
            "tool": "candidate_scorecard",
            "received": {
                "candidate_name": tool_input.get("candidate_name", "Unknown"),
                "candidate_profile": tool_input.get("candidate_profile"),
                "competencies": tool_input.get("competencies", []),
                "role_context": tool_input.get("role_context", "not specified"),
            },
            "instruction": (
                "Generate a structured competency scorecard: "
                "score each competency 1-5 (1=Does not meet, 3=Meets, 5=Exceeds expectations), "
                "provide evidence-based rationale for each score, "
                "calculate weighted overall score if weights provided, "
                "and include development areas and summary recommendation."
            ),
        })

    # Communication tools
    elif name == "draft_outreach":
        return json.dumps({
            "status": "ok",
            "tool": "draft_outreach",
            "received": {
                "candidate_name": tool_input.get("candidate_name"),
                "candidate_current_role": tool_input.get("candidate_current_role", ""),
                "opportunity_title": tool_input.get("opportunity_title"),
                "hiring_company": tool_input.get("hiring_company"),
                "channel": tool_input.get("channel", "LinkedIn"),
                "language": tool_input.get("language", "auto"),
                "key_selling_points": tool_input.get("key_selling_points", []),
            },
            "instruction": (
                "Draft a professional, warm, peer-to-peer outreach message. "
                "Not salesy. Concise for LinkedIn (300 chars max for InMail preview). "
                "Include a soft CTA. Write in the specified language."
            ),
        })

    elif name == "outreach_personalization":
        return json.dumps({
            "status": "ok",
            "tool": "outreach_personalization",
            "received": {
                "candidate_name": tool_input.get("candidate_name"),
                "candidate_profile": tool_input.get("candidate_profile"),
                "specific_achievements": tool_input.get("specific_achievements", []),
                "opportunity_title": tool_input.get("opportunity_title"),
                "hiring_company": tool_input.get("hiring_company"),
                "value_proposition": tool_input.get("value_proposition", ""),
                "channel": tool_input.get("channel", "LinkedIn"),
                "language": tool_input.get("language", "auto"),
            },
            "instruction": (
                "Write a hyper-personalized message that references specific details "
                "from the candidate's profile. Show you've done your homework. "
                "Connect their specific experience to why this role is a logical next step. "
                "Aim for 80% personalization, 20% opportunity description."
            ),
        })

    # Interview tools
    elif name == "generate_interview_questions":
        return json.dumps({
            "status": "ok",
            "tool": "generate_interview_questions",
            "received": {
                "role": tool_input.get("role"),
                "candidate_background": tool_input.get("candidate_background", ""),
                "focus_areas": tool_input.get("focus_areas", []),
                "red_flags": tool_input.get("red_flags", []),
                "num_questions": tool_input.get("num_questions", 12),
                "interview_stage": tool_input.get("interview_stage", "first_round"),
            },
            "instruction": (
                "Generate questions organized by type: "
                "Behavioral (STAR format), Functional/Technical, Situational, "
                "Leadership & Culture, and Red Flag probes. "
                "Include follow-up probes for each main question."
            ),
        })

    elif name == "interview_strategy":
        return json.dumps({
            "status": "ok",
            "tool": "interview_strategy",
            "received": {
                "role": tool_input.get("role"),
                "candidate_background": tool_input.get("candidate_background", ""),
                "interview_stage": tool_input.get("interview_stage"),
                "competencies_to_assess": tool_input.get("competencies_to_assess", []),
                "red_flags_to_probe": tool_input.get("red_flags_to_probe", []),
                "duration_minutes": tool_input.get("duration_minutes", 60),
                "interviewer_profile": tool_input.get("interviewer_profile", ""),
            },
            "instruction": (
                "Create a structured interview guide with: "
                "objectives, time-boxed sections (opening, discovery, competency assessment, "
                "red flag probes, candidate Q&A, wrap-up), "
                "specific questions per section, evaluation gates, "
                "and scoring guidance for the interviewer."
            ),
        })

    # Summary & shortlist tools
    elif name == "summarize_interview":
        return json.dumps({
            "status": "ok",
            "tool": "summarize_interview",
            "received": {
                "candidate_name": tool_input.get("candidate_name"),
                "role": tool_input.get("role", "not specified"),
                "interview_notes": tool_input.get("interview_notes"),
                "interview_stage": tool_input.get("interview_stage", "not specified"),
                "interviewer": tool_input.get("interviewer", "not specified"),
                "interview_date": tool_input.get("interview_date", ""),
            },
            "instruction": (
                "Generate a professional recruiter summary with sections: "
                "Executive Summary (3-4 sentences), Career Highlights, "
                "Competency Assessment, Cultural Alignment, Motivation & Availability, "
                "Compensation Expectations, Key Concerns & Risks, "
                "and Overall Recommendation (proceed / hold / decline + rationale)."
            ),
        })

    elif name == "create_shortlist":
        return json.dumps({
            "status": "ok",
            "tool": "create_shortlist",
            "received": {
                "role": tool_input.get("role"),
                "company": tool_input.get("company", "not specified"),
                "candidates": tool_input.get("candidates", []),
                "shortlist_size": tool_input.get("shortlist_size", len(tool_input.get("candidates", []))),
                "ranking_criteria": tool_input.get("ranking_criteria", []),
            },
            "instruction": (
                "Generate a formatted shortlist document: "
                "executive summary of search, candidate comparison table, "
                "individual candidate profiles (highlights, strengths, risks, comp, availability), "
                "ranking rationale, and recommendation for next steps."
            ),
        })

    # Compensation tool
    elif name == "compensation_analysis":
        return json.dumps({
            "status": "ok",
            "tool": "compensation_analysis",
            "received": {
                "role": tool_input.get("role"),
                "market": tool_input.get("market", "Brazil"),
                "industry": tool_input.get("industry", "not specified"),
                "company_stage": tool_input.get("company_stage", "not specified"),
                "candidates": tool_input.get("candidates", []),
                "budget_range": tool_input.get("budget_range", "not specified"),
                "currency": tool_input.get("currency", "BRL"),
            },
            "instruction": (
                "Produce a compensation analysis with: "
                "market benchmark ranges by percentile (P25/P50/P75/P90), "
                "candidate comparison table (base/variable/equity/total), "
                "gap analysis vs. market and vs. budget, "
                "and offer structuring recommendations."
            ),
        })

    # Job definition tool
    elif name == "job_brief_builder":
        return json.dumps({
            "status": "ok",
            "tool": "job_brief_builder",
            "received": {
                "company_name": tool_input.get("company_name"),
                "role_title": tool_input.get("role_title"),
                "company_context": tool_input.get("company_context", ""),
                "reporting_to": tool_input.get("reporting_to", "not specified"),
                "team_size": tool_input.get("team_size", "not specified"),
                "key_objectives": tool_input.get("key_objectives", []),
                "success_metrics": tool_input.get("success_metrics", []),
                "budget_range": tool_input.get("budget_range", "not specified"),
                "timeline": tool_input.get("timeline", "not specified"),
                "location_type": tool_input.get("location_type", "not specified"),
                "dealbreakers": tool_input.get("dealbreakers", []),
            },
            "instruction": (
                "Build a complete search brief including: "
                "company overview, role overview, key responsibilities (8-10), "
                "30/60/90-day success metrics, required qualifications, "
                "ideal candidate profile narrative, culture and values fit, "
                "interview process design (stages + assessors), "
                "and sourcing strategy recommendations."
            ),
        })

    # Strategic intelligence tool
    elif name == "talent_insight":
        return json.dumps({
            "status": "ok",
            "tool": "talent_insight",
            "received": {
                "analysis_type": tool_input.get("analysis_type"),
                "role": tool_input.get("role", "not specified"),
                "industry": tool_input.get("industry"),
                "geography": tool_input.get("geography", "not specified"),
                "company_stage": tool_input.get("company_stage", "not specified"),
                "target_companies": tool_input.get("target_companies", []),
                "question": tool_input.get("question", ""),
                "context": tool_input.get("context", ""),
            },
            "instruction": (
                "Provide a strategic talent market analysis with: "
                "key findings, talent flow patterns, top feeder companies (tiered), "
                "market dynamics and trends, hiring competition landscape, "
                "and actionable recommendations for the search strategy."
            ),
        })

    return json.dumps({"error": f"Unknown tool: {name}", "available_tools": [t["name"] for t in TOOLS]})
