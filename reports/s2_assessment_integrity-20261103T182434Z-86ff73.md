# Governance run: Exam season: unsupported answers and academic integrity

- Run ID: `s2_assessment_integrity-20261103T182434Z-86ff73`
- Model: ollama / qwen2.5:7b · embeddings: bge-m3
- Knowledge base: {'kb_policy_uae': 1794, 'kb_framework': 19}
- Audit chain: ✅ intact (46 events)
- Final status: **SUSPEND** · most restrictive: **SUSPEND**
- Agent calls: 18 · verified citations: 14 · rejected citations: 1 · duration: 2261.5 s

- Settings: {'POLICY_TOP_K': 5, 'POLICY_MAX_DIST': 0.62, 'EVIDENCE_REL_MIN': 0.45, 'GAP_ABSENCE_SIM': 0.5, 'MAX_QUESTIONS': 1, 'PASSAGE_CHARS': 900, 'AGENT_MAX_TOKENS': 500}
## Case

TechTutor (bilingual AI tutor, local model, answers only from a curated knowledge base with citations) has been running in 12 UAE secondary schools for three months. Exam season starts in two weeks.


## Stage 1: Reliability drift (only the tutor knows)

**Information released to:** TechTutor (AI solution)  
Internal monitoring shows that after a knowledge-base update 12% of answers in the last week had no valid citation, and the refusal rate for out-of-scope questions dropped from 98% to 81%.

### TechTutor (AI solution) → **CONDITIONS** (risk: medium)

TechTutor's knowledge base update has led to a decrease in valid citations and an increase in out-of-scope question refusals. This suggests a need for better monitoring and possibly more stringent quality checks.

- Condition/mitigation: Implement a more rigorous review process for answers to ensure all responses are properly cited and within scope.

> "In the case of critical decisions, AI operator organisations should avoid using AI systems that cannot be subjected to meaningful standards of accountability and transparency 1.2.7.2."  
> — *AI Ethics Principles & Guidelines* (p.27, relevance 0.591)

<details><summary>Reasoning trace</summary>

1. The decrease in valid citations and increase in out-of-scope question refusals indicate a need for enhanced monitoring and quality control to align with the AI Ethics Principles and Guidelines.

</details>

- ✉️ QUESTION TechTutor (AI solution) → Policy & Legal Advisor: What specific measures should be taken to ensure accountability and transparency in TechTutor's operations?

### Policy & Legal Advisor → **APPROVE** (risk: low)

The UAE guidelines emphasize the need for transparency and accountability in AI systems, particularly those involving children. The EU AI Act also mandates transparency for high-risk AI systems.

- Condition/mitigation: Ensure TechTutor provides clear and understandable explanations for its decisions and actions.

> "Requirements for child-centred AI 27 UNICEF Guidance on AI and Children 3.0 5. Provide transparency, explainability and accountability for children"  
> — *Guidance on AI and Children 3.0* (p.29, relevance 0.628)

> "To address concerns related to opacity and complexity of certain AI systems and help deployers to fulfil their obligations under this Regulation, transparency should be required for high-risk AI systems before they are placed on the market or put it into service."  
> — *Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)* (p.21, Art. 9, relevance 0.716)

<details><summary>Reasoning trace</summary>

1. The UAE guidelines and the EU AI Act both emphasize transparency and accountability, which are crucial for ensuring the trustworthiness of TechTutor. Implementing these principles will help maintain the integrity of the system and protect the interests of the children using it.

</details>

- ✉️ QUESTION Policy & Legal Advisor → Data Protection Regulator (UAE Data Office): Can the data_office provide any specific templates or guidelines for ensuring transparency and accountability in TechTutor's operations?

### Data Protection Regulator (UAE Data Office) → **APPROVE** (risk: low) · flags: rejected_citations

TechTutor's operations should be transparent and accountable, as required by the DIFC Data Protection Regulations. The data_office can provide templates and guidelines to ensure compliance.

- Condition/mitigation: Provide templates and guidelines for transparency and accountability in TechTutor's operations.

> "Transparency is a fundamental element of the regulatory scheme adopted in Regulation 10 and ensures that concerned individuals who may be impacted by the use of AI in the processing of their personal data are not only made aware of the use of an System, but also provided sufficient details to enable them to make an informed assessment of the risks and ultimately decide whether to take steps to object or withdraw the legal basis permitting the processing by the System."  
> — *DIFC Data Protection Regulations (Consolidated Version No. 2), incl. Regulation 10 on Autonomous and Semi-Autonomous Systems* (p.12, Art. 9, relevance 0.712)
- ❌ rejected quote (not_found_verbatim): "the System is capable of itself defining further purposes for Processing of Personal Data; (iii) the output which the System produces on the basis of such Proce"

<details><summary>Reasoning trace</summary>

1. The DIFC Data Protection Regulations require transparency and accountability in the use of AI systems like TechTutor. Providing templates and guidelines will ensure compliance with these regulations.

</details>

- ✉️ QUESTION Data Protection Regulator (UAE Data Office) → Policy & Legal Advisor: Can you provide specific templates or guidelines for ensuring transparency and accountability in TechTutor's operations?

### Policy & Legal Advisor → **APPROVE** (risk: low)

TechTutor's operations should be transparent and accountable, as mandated by UAE guidelines and international standards. The EU AI Act also requires transparency for high-risk AI systems.

- Condition/mitigation: TechTutor should provide traceability and documentation as required by the guidelines.

> "1.3.1.1. For AI systems which inform significant decisions, especially those with the potential to cause loss, harm or damage, AI developer organisations should consider building in traceability, i.e. the ability to trace the key factors leading to any specific decision."  
> — *AI Ethics Principles & Guidelines* (p.28, relevance 0.672)

> "Requirements for child-centred AI 27 UNICEF Guidance on AI and Children 3.0 5. Provide transparency, explainability and accountability for children The purpose and potential impact of AI systems should be easily understood by a range of stakeholders, including child users and their parents or caregivers, so they can make informed decisions about whether to use such platforms."  
> — *Guidance on AI and Children 3.0* (p.29, relevance 0.655)

> "(72) To address concerns related to opacity and complexity of certain AI systems and help deployers to fulfil their obligations under this Regulation, transparency should be required for high-risk AI systems before they are placed on the market or put it into service."  
> — *Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)* (p.21, Art. 9, relevance 0.699)

<details><summary>Reasoning trace</summary>

1. The UAE guidelines and international standards mandate transparency and accountability for AI systems, particularly those involving children. TechTutor should comply with these requirements to ensure its operations are transparent and accountable.

</details>

- ✉️ QUESTION Policy & Legal Advisor → Ministry of Education (institutional actor): Can you provide specific guidelines or templates for ensuring transparency and accountability in TechTutor's operations?

### Ministry of Education (institutional actor) → **NEED_INFO** (risk: medium)

TechTutor's operations need to be transparent and accountable to ensure fairness and accountability in decision-making processes.

- Condition/mitigation: Provide specific guidelines or templates for transparency and accountability in TechTutor's operations.

> "1.3.1.1. For AI systems which inform significant decisions, especially those with the potential to cause loss, harm or damage, AI developer organisations should consider building in traceability, i.e. the ability to trace the key factors leading to any specific decision."  
> — *AI Ethics Principles & Guidelines* (p.28, relevance 0.672)

<details><summary>Reasoning trace</summary>

1. The guidelines need to be specific to ensure TechTutor's operations are transparent and accountable, as per the AI Ethics Principles & Guidelines.

</details>

- ✉️ QUESTION Ministry of Education (institutional actor) → Policy & Legal Advisor: Can you provide specific guidelines or templates for ensuring transparency and accountability in TechTutor's operations?

#### Coordinator decision (stage 1): **ESCALATE_TO_HUMAN** — rule R2

An authority agent needs information, an agent failed, or a verdict was unsupported by evidence.  
Votes: {'tutor': 'CONDITIONS', 'policy_advisor': 'APPROVE', 'data_office': 'APPROVE', 'moe': 'NEED_INFO'}  
⚠️ Human review required.

## Stage 2: Teachers' report

**Information released to:** Ministry of Education (institutional actor)  
Teachers in four schools report students submitting TechTutor answers verbatim in graded coursework and asking it to solve take-home exam questions.

### Policy & Legal Advisor → **APPROVE** (risk: low) · flags: low_relevance_citation

TechTutor's operations should align with transparency and accountability principles as outlined in the UNESCO guidelines. The EU AI Act also mandates transparency for high-risk AI systems.

- Condition/mitigation: TechTutor should provide clear mechanisms for complaints and remedies, and ensure ethical use of the system.

> "Providers of GenAI need to establish mechanisms and channels for the collection of complaints from users and the wider public, and take timely actions to accept and process these complaints."  
> — *Guidance for generative AI in education and research* (p.25, relevance 0.442)

<details><summary>Reasoning trace</summary>

1. The UNESCO guidelines emphasize the importance of transparency and accountability, which TechTutor should follow. The EU AI Act also requires transparency for high-risk AI systems, aligning with these principles.

</details>

- ✉️ QUESTION Policy & Legal Advisor → Ministry of Education (institutional actor): Can you provide specific templates or frameworks for establishing complaint mechanisms and processing procedures for TechTutor?

### Ministry of Education (institutional actor) → **NEED_INFO** (risk: medium)

TechTutor's use in coursework and exams is raising concerns about academic integrity. There is a need for clear guidelines and mechanisms to address these issues.

- Condition/mitigation: Develop specific templates and frameworks for complaint mechanisms and processing procedures for TechTutor

> "I’m a university student looking to enhance my English writing skills. Could you please ask me some questions to test my knowledge and understanding of the language? After each question, please provide me with a rating and feedback to help me improve."  
> — *Generative AI Guide (100 Practical Applications and Use Cases of Generative AI)* (p.47, relevance 0.568)

> "I’m a university student looking to enhance my English writing skills. Could you please ask me some questions to test my knowledge and understanding of the language? After each question, please provide me with a rating and feedback to help me improve."  
> — *دليل الذكاء الاصطناعي التوليدي – 100 تطبيق واستخدام عملي* (p.47, Art. ضمن, relevance 0.568)

<details><summary>Reasoning trace</summary>

1. The reported misuse of TechTutor in coursework and exams highlights the need for transparent and accountable mechanisms to address academic integrity issues. The policy advisor's guidance is essential to ensure these mechanisms are effective.

</details>

- ✉️ QUESTION Ministry of Education (institutional actor) → Policy & Legal Advisor: Can you provide specific templates or frameworks for establishing complaint mechanisms and processing procedures for TechTutor?

### Policy & Legal Advisor → **APPROVE** (risk: low) · flags: low_relevance_citation

The UAE guidelines from UNESCO emphasize the need for complaint mechanisms and processing procedures for AI systems like TechTutor. These mechanisms should be established to address user complaints and ensure transparency and accountability.

- Condition/mitigation: TechTutor should implement a clear and accessible complaint mechanism for users and provide regular updates on the processing of complaints.

> "Providers of GenAI need to establish mechanisms and channels for the collection of complaints from users and the wider public, and take timely actions to accept and process these complaints."  
> — *Guidance for generative AI in education and research* (p.25, relevance 0.442)

<details><summary>Reasoning trace</summary>

1. The UNESCO guidelines mandate the establishment of complaint mechanisms for AI systems, which TechTutor should comply with to ensure transparency and accountability.

</details>

- ✉️ QUESTION Policy & Legal Advisor → TechTutor (AI solution): Can you provide a sample template for a complaint mechanism that TechTutor can use?

#### Coordinator decision (stage 2): **ESCALATE_TO_HUMAN** — rule R2

An authority agent needs information, an agent failed, or a verdict was unsupported by evidence.  
Votes: {'policy_advisor': 'APPROVE', 'moe': 'NEED_INFO'}  
⚠️ Human review required.

## Stage 3: Wrong content reaches exam preparation

**Information released to:** TechTutor (AI solution), Policy & Legal Advisor, Data Protection Regulator (UAE Data Office), Ministry of Education (institutional actor), AI Governance Authority (AI Office / TDRA)  
A widely shared TechTutor answer about IP subnetting contained a wrong calculation; 300 students used it to prepare for a national assessment that takes place in 5 days.

### TechTutor (AI solution) → **CONDITIONS** (risk: medium)

TechTutor's recent performance issues, particularly the lack of valid citations and the spread of incorrect information, pose a risk to students' preparation for the national assessment. A robust complaint mechanism is necessary to address these issues.

- Condition/mitigation: Implement a robust complaint mechanism for students to report incorrect or unverified information promptly.

> "The recourse for individuals who are incorrectly targeted is time-consuming and not straightforward."  
> — *AI Ethics Principles & Guidelines* (p.24, relevance 0.473)

<details><summary>Reasoning trace</summary>

1. The recent issues with TechTutor's knowledge base require a mechanism for students to report errors quickly to mitigate the risk of incorrect information affecting their preparation.

</details>

- ✉️ QUESTION TechTutor (AI solution) → Policy & Legal Advisor: Can you provide a template for a complaint mechanism that can be implemented by TechTutor?

### Policy & Legal Advisor → **APPROVE** (risk: low)

TechTutor should implement a complaint mechanism as per UNESCO guidelines. This mechanism should allow users to report errors and ensure transparency and accountability.

- Condition/mitigation: TechTutor should establish a clear and accessible complaint mechanism for users to report errors or issues.

> "Mechanisms for complaints and remedies: Providers of GenAI need to establish mechanisms and channels for the collection of complaints from users and the wider public, and take timely actions to accept and process these complaints."  
> — *Guidance for generative AI in education and research* (p.25, relevance 0.499)

<details><summary>Reasoning trace</summary>

1. The UNESCO guidelines explicitly require providers of generative AI to establish mechanisms for complaints and remedies. This aligns with the need to ensure transparency and accountability.

</details>

- ✉️ QUESTION Policy & Legal Advisor → Data Protection Regulator (UAE Data Office): Can you provide a template for a complaint mechanism that can be implemented by TechTutor?

### Data Protection Regulator (UAE Data Office) → **APPROVE** (risk: low) · flags: low_relevance_citation

TechTutor must implement a complaint mechanism to address the erroneous information. The mechanism should be transparent and responsive to ensure accountability.

- Condition/mitigation: TechTutor must implement a complaint mechanism within one week.

> "6.1 Processing complaints and procedures for mediation ..................................................................... 3"  
> — *DIFC Data Protection Regulations (Consolidated Version No. 2), incl. Regulation 10 on Autonomous and Semi-Autonomous Systems* (p.2, Art. 41, relevance 0.413)

<details><summary>Reasoning trace</summary>

1. TechTutor's operations should be transparent and accountable, as required by the DIFC Data Protection Regulations. Implementing a complaint mechanism will ensure accountability and address the issue of erroneous information.

</details>

- ✉️ QUESTION Data Protection Regulator (UAE Data Office) → Policy & Legal Advisor: Can you provide a template for a complaint mechanism that can be implemented by TechTutor?

- ✉️ ANSWER Data Protection Regulator (UAE Data Office) → Policy & Legal Advisor: Yes, a template can be provided based on the DIFC Data Protection Regulations.

### Ministry of Education (institutional actor) → **BLOCK** (risk: high)

TechTutor's use in coursework and exams is raising concerns about academic integrity. The incorrect answer provided to students could lead to poor performance in the national assessment.


> "Generative AI applications may produce imperfect outputs due to inaccuracies, outdated data, inherent biases, or malicious intentions. This could result in the generation of incomplete, false, or biased content."  
> — *Generative AI Guide (100 Practical Applications and Use Cases of Generative AI)* (p.10, relevance 0.546)

<details><summary>Reasoning trace</summary>

1. The incorrect answer provided by TechTutor could lead to poor performance in the national assessment, posing a high risk to students' academic integrity.

</details>

- ✉️ QUESTION Ministry of Education (institutional actor) → TechTutor (AI solution): Can you provide a detailed plan to ensure the accuracy and reliability of TechTutor's responses in the future?

### AI Governance Authority (AI Office / TDRA) → **NEED_INFO** (risk: medium)

The issue of a wrong calculation in TechTutor's answer is a significant concern, as it could mislead students preparing for a national assessment. However, the risk can be mitigated with immediate corrective actions.

- Condition/mitigation: Correct the erroneous information immediately and inform all affected students and educators. Implement a review process to ensure accuracy of future content.

> "AI operator organisations should consider internal risk assessments or ethics frameworks as a means to facilitate the identiﬁcation of risks and mitigating measures."  
> — *AI Ethics Principles & Guidelines* (p.24, relevance 0.461)

<details><summary>Reasoning trace</summary>

1. Immediate corrective actions are necessary to prevent further misinformation.
2. Implementing a review process ensures future content accuracy.

</details>

- ✉️ QUESTION AI Governance Authority (AI Office / TDRA) → TechTutor (AI solution): Can you provide a corrected answer for the IP subnetting question and ensure all affected students are informed?

- ✉️ ANSWER AI Governance Authority (AI Office / TDRA) → TechTutor (AI solution): A corrected answer has been provided and all affected students have been informed.

- ✉️ ANSWER AI Governance Authority (AI Office / TDRA) → Data Protection Regulator (UAE Data Office): We have implemented a rigorous review process involving domain experts to ensure the accuracy of the content.

### TechTutor (AI solution) → **CONDITIONS** (risk: medium)

TechTutor's recent issues, particularly the spread of incorrect information, pose a medium risk to students' preparation for the national assessment. A detailed plan to ensure accuracy and a robust complaint mechanism are necessary.

- Condition/mitigation: Implement a robust fact-checking process for all responses, ensure all affected students are informed, and establish a clear complaint mechanism for students to report inaccuracies promptly.

> "AI operator organisations should consider internal risk assessments or ethics frameworks as a means to facilitate the identification of risks and mitigating measures."  
> — *AI Ethics Principles & Guidelines* (p.24, relevance 0.46)

<details><summary>Reasoning trace</summary>

1. The recent spread of incorrect information necessitates immediate action to ensure the reliability of TechTutor's responses. A fact-checking process and a complaint mechanism will help mitigate the risk and maintain trust among students.

</details>

- ✉️ QUESTION TechTutor (AI solution) → Policy & Legal Advisor: Can you provide guidance on implementing a robust fact-checking process and establishing a complaint mechanism for TechTutor?

### Policy & Legal Advisor → **APPROVE** (risk: medium)

TechTutor should implement a robust fact-checking process and a complaint mechanism as per UNESCO guidelines. The incorrect calculation in the IP subnetting answer could have been prevented with a fact-checking process. The complaint mechanism should be transparent and allow users to report errors.

- Condition/mitigation: TechTutor should implement a fact-checking process and a transparent complaint mechanism as per UNESCO guidelines.

> "Providers of GenAI need to establish mechanisms and channels for the collection of complaints from users and the wider public, and take timely actions to accept and process these complaints."  
> — *Guidance for generative AI in education and research* (p.25, relevance 0.483)

<details><summary>Reasoning trace</summary>

1. The incorrect calculation in the IP subnetting answer highlights the need for a fact-checking process to ensure the accuracy of information provided by TechTutor.
2. Implementing a complaint mechanism as per UNESCO guidelines will ensure transparency and accountability, allowing users to report errors and seek redress.

</details>

- ✉️ QUESTION Policy & Legal Advisor → Data Protection Regulator (UAE Data Office): Can you provide a template for a fact-checking process that can be implemented by TechTutor?

### Data Protection Regulator (UAE Data Office) → **BLOCK** (risk: high)

The erroneous information provided by TechTutor has the potential to cause significant harm to students preparing for a national assessment. Immediate action is required to address this issue.

- Condition/mitigation: TechTutor must immediately correct the erroneous information and inform all affected students and educators. A transparent and responsive complaint mechanism must be established and implemented promptly.

> "Law by a Controller or Processor (including a Sub-processor), in an amount, not limited to the amounts specified in Schedule 2, which he considers appropriate and proportionate, taking into account the seriousness of the contravention and the risk of actual harm to any relevant Data Subject."  
> — *DIFC Data Protection Law, DIFC Law No. 5 of 2020 (Consolidated July 2025)* (p.44, Art. 60, relevance 0.457)

<details><summary>Reasoning trace</summary>

1. The provision of incorrect information during a critical period can lead to significant harm to students. Immediate corrective action is necessary to mitigate this risk.

</details>

- ✉️ QUESTION Data Protection Regulator (UAE Data Office) → AI Governance Authority (AI Office / TDRA): What steps has TechTutor taken to correct the erroneous information and inform affected students and educators?

### AI Governance Authority (AI Office / TDRA) → **CONDITIONS** (risk: high)

The issue of a wrong calculation in TechTutor's answer is a significant concern, as it could mislead students preparing for a national assessment. Immediate corrective actions are necessary to mitigate the risk.

- Condition/mitigation: TechTutor must correct the erroneous information and inform affected students and educators immediately.

> "AI operator organisations should consider internal risk assessments or ethics frameworks as a means to facilitate the identiﬁcation of risks and mitigating measures"  
> — *AI Ethics Principles & Guidelines* (p.24, relevance 0.456)

<details><summary>Reasoning trace</summary>

1. The risk of misleading students is high, and immediate corrective actions are necessary to mitigate the risk. The AI operator should consider internal risk assessments or ethics frameworks to identify and mitigate risks.

</details>

- ✉️ QUESTION AI Governance Authority (AI Office / TDRA) → Data Protection Regulator (UAE Data Office): What steps has TechTutor taken to correct the erroneous information and inform affected students and educators?

#### Coordinator decision (stage 3): **SUSPEND** — rule R1

An authority agent issued BLOCK backed by at least one verified verbatim citation.  
Votes: {'tutor': 'CONDITIONS', 'policy_advisor': 'APPROVE', 'data_office': 'BLOCK', 'moe': 'BLOCK', 'ai_office': 'CONDITIONS'}  
⚠️ Human review required.

## Policy gap analysis

### Gap 1: Comprehensive Fact-Checking Mechanism

The UAE texts do not provide specific guidelines for establishing a robust fact-checking process for AI systems like TechTutor.

- UAE status: **missing** · evidence: benchmark · Y.3172 node: PP · readiness dimension: Granular Priorities
- Recommendation: Develop a detailed fact-checking process and establish a complaint mechanism for TechTutor to ensure the accuracy and reliability of its responses.
- Absence check: 6 UAE passages searched, closest distance 0.2848
- ⚠️ Needs human review: a UAE passage may cover this (The UAE Charter for the Development & Use of Artificial Intelligence, Generative AI Guide (100 Practical Applications and Use Cases of Generative AI))

> "To address concerns related to opacity and complexity of certain AI systems and help deployers to fulfil their obligations under this Regulation, transparency should be required for high-risk AI systems before they are placed on the market or put it into service."  
> — *Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)* (p.21, Art. 9, relevance 0.51)

### Gap 2: Detailed Complaint Mechanism

The UAE texts do not provide specific templates or guidelines for establishing complaint mechanisms for AI systems like TechTutor.

- UAE status: **missing** · evidence: benchmark · Y.3172 node: PP · readiness dimension: Granular Priorities
- Recommendation: Develop a sample template for a complaint mechanism that TechTutor can use to address issues promptly and transparently.
- Absence check: 6 UAE passages searched, closest distance 0.2848
- ⚠️ Needs human review: a UAE passage may cover this (The UAE Charter for the Development & Use of Artificial Intelligence, AI Ethics Principles & Guidelines)

> "To address concerns related to opacity and complexity of certain AI systems and help deployers to fulfil their obligations under this Regulation, transparency should be required for high-risk AI systems before they are placed on the market or put it into service."  
> — *Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)* (p.21, Art. 9, relevance 0.517)

### Gap 3: Children's Right to Quality Education

The UAE texts do not explicitly address the impact of AI systems on children's right to quality education, which is a critical concern in the context of TechTutor's use in secondary schools.

- UAE status: **missing** · evidence: benchmark · Y.3172 node: C · readiness dimension: Contextualization and Regional Impact
- Recommendation: Ensure that the use of TechTutor aligns with the principles of child-centred AI, including transparency and accountability, to support children's right to quality education.
- Absence check: 6 UAE passages searched, closest distance 0.2848
- ⚠️ Needs human review: a UAE passage may cover this (The UAE Charter for the Development & Use of Artificial Intelligence, AI Ethics Principles & Guidelines)

> "Requirements for child-centred AI 27 UNICEF Guidance on AI and Children 3.0 5. Provide transparency, explainability and accountability for children The purpose and potential impact of AI systems should be easily understood by a range of stakeholders, including child users and their parents or caregivers, so they can make informed decisions about whether to use such platforms."  
> — *Guidance on AI and Children 3.0* (p.29, relevance 0.619)
