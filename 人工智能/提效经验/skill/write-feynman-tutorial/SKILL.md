---
name: write-feynman-tutorial
description: Create or revise beginner-friendly tutorials with a Feynman learning loop, repository-wide prerequisite coverage, concrete examples, runnable practice, positive-first explanations, and teaching diagrams. Use when the user asks to create, write, organize, improve, simplify, visualize, or review a tutorial, guide, learning path, zero-to-one course, technical note series, or beginner documentation. Also use when material assumes unexplained knowledge, reads like an AI-generated glossary, leads with repeated negations such as “不是……而是……”, needs concepts missing from the wider repository added, or needs an SVG to explain hierarchy, relationships, flow, state change, ownership, or mechanism comparison.
---

# Write Feynman Tutorials

Create tutorials that let a beginner build, explain, test, and transfer a working mental model.

## Establish the learner and outcome

Infer the lowest reasonable starting point from the request and repository. Ask only when different answers would materially change the tutorial.

Define an observable outcome for each lesson. Prefer “can trace a query from table name to data file” over “understands metadata.”

Use one realistic example across the series when possible. Let it accumulate new problems as the learner advances.

## Audit prerequisites repository-wide

Before writing, inspect the target tutorial, nearby notes, indexes, links, and repository conventions.

List every concept the tutorial relies on. For each concept:

1. Find an existing beginner-level explanation in the repository.
2. Link it when it is sufficient.
3. Add or expand an explanation when it is absent or still assumes specialist knowledge.
4. Place foundational shared concepts in a prerequisite lesson or the repository's natural ownership area.
5. Define a local concept at its first meaningful use when it belongs only to that lesson.

Treat expansions, units, roles, and operational words as prerequisites too. Explain items such as acronyms, version coordinates, file-size units, “worker,” “checkpoint,” and “dry run” when later reasoning depends on them.

Build the causal model in prose, diagrams, examples, or practice. Use a glossary only for recall.

## Build the learning chain

Organize the tutorial in this order:

1. Start from a concrete situation the learner can recognize.
2. Show the problem or observation that creates the need for the concept.
3. Explain what the concept does in plain language.
4. Introduce the formal term after the mental model exists.
5. Show the mechanism step by step, using a diagram when relationships carry the explanation.
6. Ask the learner to predict a result before revealing it.
7. Provide a counterexample or changed condition.
8. Add runnable practice or a paper simulation.
9. Ask for a short explanation in the learner's own words.
10. Route each likely mistake back to the exact section that repairs it.

Keep each lesson centered on one small question. Split material when a lesson requires several independent mental models.

## Write positive-first explanations

Lead with what the subject does, how it works, and why it exists.

Use this order within a section:

```text
responsibility -> mechanism -> example -> result -> boundary or risk
```

Write:

```text
Catalog maps a logical table name to current metadata and coordinates versioned commits.
Its boundary is table discovery and commit coordination; workers read data files directly.
```

Avoid opening with contrast templates such as “Catalog is not X; it is Y” or “This is not merely A, but B.” Include limits, exclusions, and warnings when they matter. Place them after the positive model unless immediate danger requires an upfront warning. State the responsible component when describing a boundary.

Prefer direct verbs: “records,” “publishes,” “filters,” “coordinates,” “rewrites,” and “verifies.” Reduce throat-clearing phrases, motivational filler, and repeated claims that the learner should “remember” something.

## Choose the teaching medium

Choose the smallest medium that makes the mental model reconstructable:

- Use prose for one causal claim or a short linear explanation.
- Use a table for repeated fields, exact mappings, or compact option comparison.
- Use code and captured output when syntax or runtime behavior is the lesson.
- Use Mermaid for a lightweight sequence or graph that remains clearer as text source.
- Use SVG when spatial organization carries meaning: hierarchy, ownership, three or more related components, dependent flow, data movement, state transition, or side-by-side mechanism comparison.
- Use screenshots for real interface state that the learner must recognize.
- Use a generated raster image for physical appearance, atmosphere, or an illustrative scene where exact labels and geometry are secondary.

Apply a diagram gate before drafting. A teaching diagram is required when the core explanation asks the learner to hold any of these in working memory:

- three or more named components and their connections;
- two or more ownership boundaries or a change of owner;
- a dependent sequence with branching, pruning, retry, or recovery;
- a before/after state transition in which some objects persist and others change;
- two mechanisms compared across the same input, intermediate state, and result.

Use SVG for the required diagram when grouping, alignment, lanes, boundaries, or before/after placement carries meaning. Use Mermaid instead only for a simple text-native graph or sequence whose automatic layout preserves the lesson. Treat ASCII boxes and arrows as planning notes, not the final diagram, after this gate triggers.

Honor an explicit request for a concept diagram by entering the SVG workflow. Use another medium only when the requested subject depends on real interface state, executable syntax, or visual appearance, and state that reason briefly.

Make every diagram teach a causal model. Organize its content as applicable:

```text
concrete scenario -> object responsibilities -> relationships -> mechanism -> result -> boundary
```

Carry one concrete example through the diagram. Use exact domain terms, label the meaning of arrows, and keep the diagram complementary to the prose.

When choosing SVG, read [references/svg-diagrams.md](references/svg-diagrams.md) completely and follow it. Then:

1. Identify the question the learner should answer after reading the diagram.
2. Select one diagram grammar from the reference.
3. Write a self-contained SVG into the tutorial's local `assets/` directory with a descriptive kebab-case filename.
4. Add a relative Markdown image reference and a useful alt description near the explanation it supports.
5. Run `python3 <skill-dir>/scripts/validate_svg.py <svg-path>`.
6. Render the containing tutorial in a browser and inspect the full image at desktop and narrow widths.
7. Verify labels, arrows, examples, and summaries against the tutorial and authoritative technical model.

Treat XML validation as structural evidence only. Confirm clipping, overlap, contrast, arrow direction, bottom-of-canvas truncation, terminology, and factual consistency by inspection.

## Apply the Feynman loop

Use explanation as a diagnostic tool:

```text
attempt an explanation or prediction
-> expose a skipped step, vague word, or contradiction
-> return to that exact gap
-> learn the missing mechanism
-> explain a changed example
-> verify through output, a counterexample, or an operation
```

Treat plain language and analogy as supporting tools. Use an analogy only when its mapping and limits are clear. Ask the learner to reconstruct the explanation without the source rather than recognize a supplied answer.

Design checks that expose misconceptions. Prefer:

- “Given S0=[A,B] and S1=[A,B,C], which versions break if B is deleted, and why?”
- “Predict the state before running this command.”
- “Change one condition and derive the new result.”
- “Explain the mechanism to a colleague who knows only the prerequisite lesson.”

When providing answers, explain which model repairs each wrong answer and link to that section.

## Make practice complete

For hands-on lessons, provide a path from a clean environment to an observable result:

1. State required tools and how to check versions.
2. Explain compatibility-sensitive coordinates and configuration.
3. Create all sample inputs inside the lesson or link their exact source.
4. Use an isolated directory, namespace, table, or project.
5. State expected intermediate and final outputs.
6. Include one deliberate prediction point.
7. Add layered troubleshooting in execution order.
8. State which checks were actually run and which remain unverified in the current environment.

Remove hidden dependencies such as an unexplained staging table, preconfigured service, existing account, or undeclared sample data.

## Preserve repository conventions

Follow the repository's established filenames, headings, navigation, links, language, and reserved user-authored sections. Preserve unrelated local changes.

Preserve user-authored `生长思考` and `反复绊脚` sections. Append or refine entries only when the user asks, and keep their concise, personal note style.

For an existing tutorial, improve the current structure before adding another parallel explanation. Add a new prerequisite document only when the concept is shared, substantial, and absent from the repository.

Keep dated or version-sensitive statements tied to authoritative current sources. Prefer a compatibility-check procedure over a static claim that will expire.

## Review before delivery

Check the complete tutorial, not only edited paragraphs:

- Every lesson begins with a recognizable situation or direct responsibility.
- Important concepts have a repository link or a beginner-level explanation.
- Responsibilities appear before limitations.
- Contrast and negation templates are rare and justified.
- One example remains consistent across lessons and diagrams.
- Diagrams answer a named learning question and encode accurate relationships.
- SVGs pass structural validation plus rendered visual and semantic inspection.
- Predictions, changed cases, practice, and self-explanation form a real correction loop.
- Commands have prerequisites, inputs, expected results, and verification boundaries.
- Safety warnings remain explicit near destructive or irreversible operations.
- Links, navigation, headings, code fences, assets, and local formatting are valid.
- The final response reports material changes and any practice or rendering that could not be executed.
