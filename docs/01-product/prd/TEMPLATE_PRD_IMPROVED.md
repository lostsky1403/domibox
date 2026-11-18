# PRD: <Product/Feature Name>

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `YYYY-MM-DD`  
**Owner:** `<name/role>`  
**Reviewers:** `<names/roles or TBD>`  
**Related Docs:** `<links/paths>`  

## 1. Document Control
| Version | Date | Author | Summary of Change | Status |
| --- | --- | --- | --- | --- |
| 0.1 | YYYY-MM-DD | <author> | Initial draft | PROPOSED |

## 2. Executive Summary
- **Problem:** <what user/business problem is being solved>
- **Proposed Solution:** <high-level solution>
- **Target Users:** <primary/secondary users>
- **Business Value:** <why now / expected impact>
- **Evidence Status:** <key claims marked VERIFIED / ASSUMPTION / PROPOSED>

## 3. Background & Context
### 3.1 Current State
<current situation, constraints, known pain points>

### 3.2 Research & Evidence Inputs
| Source | Type | Date | Key Insight | Evidence Status | Notes |
| --- | --- | --- | --- | --- | --- |
| <doc/link> | research/benchmark/interview | YYYY-MM-DD | <insight> | VERIFIED/ASSUMPTION | <gap if any> |

## 4. Goals, Non-Goals, and Success Metrics
### 4.1 Goals
- <goal>

### 4.2 Non-Goals
- <explicitly out of scope>

### 4.3 Success Metrics
| Metric ID | Metric | Baseline | Target | Timeframe | Measurement Method | Evidence Status |
| --- | --- | --- | --- | --- | --- | --- |
| SM-001 | <metric> | <baseline/TBD> | <target> | <timeframe> | <how measured> | VERIFIED/ASSUMPTION/PROPOSED |

## 5. Users, Personas, and Key Use Cases
### 5.1 Personas
| Persona | Needs | Pain Points | Success Criteria |
| --- | --- | --- | --- |
| <persona> | <needs> | <pain points> | <what success looks like> |

### 5.2 Primary Use Cases / User Journeys
1. <use case>
2. <use case>

## 6. Scope Definition
### 6.1 In Scope
- <item>

### 6.2 Out of Scope
- <item>

### 6.3 Assumptions
| ID | Assumption | Impact if Wrong | Owner | Evidence Status |
| --- | --- | --- | --- | --- |
| A-001 | <assumption> | <impact> | <owner> | ASSUMPTION/PROPOSED |

### 6.4 Dependencies
| ID | Dependency | Type | Owner | Due/Needed By | Risk |
| --- | --- | --- | --- | --- | --- |
| D-001 | <dependency> | internal/external/technical | <owner> | <date/TBD> | <risk> |

## 7. Requirements
### 7.1 Business Requirements (`BR-*`)
| ID | Requirement | Rationale | Priority | Source/Trace |
| --- | --- | --- | --- | --- |
| BR-001 | <business requirement> | <why> | Must/Should/Could | <research/goal> |

### 7.2 Functional Requirements (`FR-*`)
| ID | Requirement | User/Actor | Priority | Acceptance Criteria (summary) | Traces To |
| --- | --- | --- | --- | --- | --- |
| FR-001 | <functional requirement> | <actor> | Must/Should/Could | <testable summary> | BR-001 |

### 7.3 Non-Functional Requirements (`NFR-*`)
| ID | Category | Requirement | Target/Threshold | Priority | Traces To |
| --- | --- | --- | --- | --- | --- |
| NFR-001 | Performance/Security/Availability/etc. | <requirement> | <measurable target> | Must/Should/Could | BR-001/FR-001 |

### 7.4 Security & Privacy Requirements (`SEC-*`)
| ID | Requirement | Threat/Concern | Control/Expectation | Priority | Traces To |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | <security/privacy requirement> | <threat> | <control> | Must/Should/Could | FR-001/NFR-001 |

## 8. UX / IA Scope (Documentation-Level)
- **User flows in scope:** <list or link to UX docs>
- **Screens/views in scope:** <list>
- **Prototype status:** <VERIFIED prototype exists / NOT AVAILABLE - documentation only>
- **Accessibility considerations:** <WCAG/keyboard/contrast/focus expectations>
- **Content/empty/error states:** <requirements>

## 9. Risks, Mitigations, and Open Questions
### 9.1 Risks
| Risk ID | Description | Likelihood | Impact | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RISK-001 | <risk> | Low/Med/High | Low/Med/High | <mitigation> | <owner> | Open/Mitigated |

### 9.2 Open Questions
| Q ID | Question | Why It Matters | Owner | Needed By | Status |
| --- | --- | --- | --- | --- | --- |
| Q-001 | <question> | <impact> | <owner> | <date/TBD> | Open |

## 10. Delivery Mapping (Jira-Ready)
### 10.1 Proposed Epics / Stories
| Epic/Story Ref | Type | Summary | Requirement IDs | Priority | Notes |
| --- | --- | --- | --- | --- | --- |
| EPIC-TBD | Epic | <summary> | BR/FR/NFR/SEC | Must/Should/Could | <mapping note> |

### 10.2 Acceptance Criteria Guidance
- Use testable, observable outcomes.
- Prefer Gherkin format for MVP stories where applicable (`Given/When/Then`).
- Include negative/edge cases for abuse, validation, and permission boundaries.

## 11. Analytics, Telemetry, and Reporting
- **Events/telemetry needed:** <events>
- **Dashboards/reports:** <who needs what>
- **Privacy considerations:** <minimization, retention, consent implications>

## 12. Rollout & Operational Considerations
- **Release strategy:** <phased/big-bang/flagged>
- **Support/ops impact:** <runbooks, on-call, admin tasks>
- **Migration/backfill needs:** <if any>

## 13. Approval & Sign-off
| Role | Name | Decision | Date | Notes |
| --- | --- | --- | --- | --- |
| Product | <name/TBD> | Pending/Approved/Rejected | YYYY-MM-DD/TBD | <notes> |
| Engineering | <name/TBD> | Pending/Approved/Rejected | YYYY-MM-DD/TBD | <notes> |
| Security/Compliance | <name/TBD> | Pending/Approved/Rejected | YYYY-MM-DD/TBD | <notes> |
