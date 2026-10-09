# Course Tutor

A tutor that answers students' questions about the courses of the degree, using only the material the group wrote for each course and citing where every answer comes from.

## Language

### Subject matter

**Course**:
One of the four curricular units the tutor covers: GAIF (Generative AI Foundations), PEID (Prompt Engineering and Interaction Design), AITB (AI Tools for Business Professionals) and DTGS (Digital Transformation and Generative AI Strategy).
_Avoid_: Subject, discipline, class, unit, domain, cadeira

**Course Material**:
The summary the group wrote for one Course; it is the only source of truth about that Course.
_Avoid_: Slides, documents, knowledge base, corpus

**Section**:
A numbered part of a Course Material with its own identifier (e.g. `PEID-2.3`); it is the unit that gets cited.
_Avoid_: Chunk, excerpt, passage, paragraph

**Course Description**:
A short statement of what a Course covers and what it does not cover, which the Router reads to decide where a question belongs.
_Avoid_: Syllabus, course summary, router prompt

**Out of scope**:
The label for a question that belongs to none of the Courses.
_Avoid_: Off-topic, invalid, other

### Parts of the app

**Router**:
The part that reads a question and decides which Course it belongs to, or that it is Out of scope.
_Avoid_: Orchestrator, central agent, classifier

**Course Tutor**:
The part that answers a question using only one Course's Course Material.
_Avoid_: Course agent, specialist agent, bot

**Refusal**:
The Course Tutor's fixed answer when a question routed to its Course is not covered by the Course Material, including requests to solve new exercises and questions about course logistics.
_Avoid_: Fallback, error, "I don't know"

**Agentic Tutor**:
An experimental variant of the Course Tutor in which the model itself decides which parts of the Course Material to consult, through a search tool.
_Avoid_: Course agent

**Grounded Answer**:
A Course Tutor answer in which every claim is in the Course Material and is cited to the Section it came from.
_Avoid_: Response, output

### Evaluation

**Golden Set**:
The fixed, versioned list of 36 questions with their agreed expected outcomes, against which every version of the app is measured.
_Avoid_: Test set, dataset, examples

**Overlap Case**:
A golden-set question genuinely covered by two Course Materials, so it has two Accepted Courses.
_Avoid_: Ambiguous question

**Near-miss Case**:
A golden-set question that sounds like it belongs to two Courses but is covered by only one, so it has a single Accepted Course.
_Avoid_: Trick question, overlap case

**Accepted Courses**:
The set of one or two Courses a golden-set question may correctly be routed to; two when the question is genuinely covered by both Course Materials.
_Avoid_: Correct course, true label

**Supported**:
A judge verdict on an answer: every claim in it is found in the Section it cites.
_Avoid_: Correct, true, faithful, accurate

**Responsive**:
A judge verdict on an answer: it addresses what the question actually asked.
_Avoid_: Correct, relevant, useful, complete

**End-to-end Success**:
The headline metric: a golden-set case succeeds when the Router picks one of its Accepted Courses and the Course Tutor either gives an answer that cites an expected Section and is judged Supported and Responsive, or refuses when a refusal is expected.
_Avoid_: Accuracy, score, pass rate

### Building

**Agent**:
A GitHub Copilot agent defined in `.github/agents/`, used by the group to build the app; never a part of the app.
_Avoid_: Using "agent" for the Router or the Course Tutor
