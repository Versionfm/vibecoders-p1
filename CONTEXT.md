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
A short statement of what a Course covers and what it does not cover, which the Router or the Agentic Tutor reads to decide where a question belongs.
_Avoid_: Syllabus, course summary, router prompt

**Out of scope**:
The label for a question that belongs to none of the Courses.
_Avoid_: Off-topic, invalid, other

**Out of scope Sentence**:
The fixed answer the Agentic Tutor gives, without reading any Course Material, when a question is Out of scope.
_Avoid_: Out of scope message, rejection

### Parts of the app

**Router**:
The part that reads a question and decides which Course it belongs to, or that it is Out of scope.
_Avoid_: Orchestrator, central agent, classifier

**Course Tutor**:
The part that answers a question using only one Course's Course Material.
_Avoid_: Course agent, specialist agent, bot

**Refusal**:
The fixed answer when the Course Material chosen for a question does not cover it, including requests to solve new exercises and questions about course logistics.
_Avoid_: Fallback, error, "I don't know"

**Routed Tutor**:
The Router followed by the Course Tutor: the app's first design, in which one Course Material is chosen before the answer is written.
_Avoid_: Baseline, pipeline, classic tutor

**Agentic Tutor**:
An experimental alternative to the Routed Tutor with no Router: one model decides which Course Materials to read, one whole Course Material per read, and answers from what it read.
_Avoid_: Course agent, agent, single agent

**Read**:
One request by the Agentic Tutor for the whole Course Material of one Course.
_Avoid_: Tool call, retrieval, search, lookup

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
The set of one or two Courses whose Course Material a golden-set question may correctly be answered from; two when the question is genuinely covered by both Course Materials.
_Avoid_: Correct course, true label

**Run**:
One pass of every case in a case file through the app; an evaluation has three Runs.
_Avoid_: Iteration, trial, attempt

**Trace**:
The record of one case in one Run: the Course Materials chosen or read, in order, and the answer given.
_Avoid_: Run, log, transcript

**Search Step**:
The verdict on whether a Trace used the right Course Material: only Accepted Courses were chosen or read, at least one of them, and none at all for an Out of scope case.
_Avoid_: Retrieval, routing accuracy

**Path Step**:
The verdict on whether a Trace got to its answer properly: no Course Material read twice, no request for something that is not a Course, no answer to an in-scope question without reading, within the Read limit, and no failed model call.
_Avoid_: Process, trajectory

**Answer Step**:
The verdict on the answer of a Trace: it cites an expected Section and only Sections of Course Materials it chose or read, or gives the Refusal or Out of scope Sentence when one is expected; once the judge exists, the answer must also be Supported and Responsive.
_Avoid_: Answer accuracy, correctness

**Supported**:
A judge verdict on an answer: every claim in it is found in the Section it cites.
_Avoid_: Correct, true, faithful, accurate

**Responsive**:
A judge verdict on an answer: it addresses what the question actually asked.
_Avoid_: Correct, relevant, useful, complete

**End-to-end Success**:
The headline metric: a Trace succeeds when it passes the Search Step, the Path Step and the Answer Step; reported as the share of Traces that succeed.
_Avoid_: Accuracy, score, overall pass, overall

### Building

**Agent**:
A coding-assistant agent (a Claude Code agent in `.claude/agents/`, or a GitHub Copilot agent in `.github/agents/`) used by the group to build or evaluate the app; never a part of the app.
_Avoid_: Using "agent" for the Router, the Course Tutor or the Agentic Tutor
