# Teaching SVG Reference

Read this file completely whenever the tutorial needs an SVG. Design the explanation before drawing shapes.

## Contents

1. Select a diagram grammar
2. Build the teaching model
3. Construct a robust SVG
4. Keep the image readable and accessible
5. Choose SVG versus another medium
6. Validate structure, rendering, and meaning
7. Reusable Iceberg examples

## Select a diagram grammar

Start from the learner's question. Use one primary grammar per image.

Create a formal diagram when the lesson's mechanism depends on three or more connected objects, ownership transfer, a nontrivial dependent sequence, persistent versus changed state, or aligned mechanism comparison. Do not deliver an ASCII tree or arrow chain as the final visual in those cases. Use it only to draft the SVG structure.

| Learner question | Grammar | Spatial rule |
| --- | --- | --- |
| What contains, points to, or depends on what? | Hierarchy | Arrange levels top-to-bottom; show the authoritative entry first |
| Which objects collaborate, and what crosses each connection? | Relationship | Group by responsibility; label every meaningful connection |
| What happens next, and what travels between steps? | Flow | Use one reading direction; put verbs or payloads on arrows |
| What changes after an operation? | State transition | Show before, operation, after; keep unchanged objects visible |
| Why do two mechanisms have different costs? | Comparison | Use aligned lanes, the same example, and the same evaluation points |
| Which system owns each responsibility? | Ownership or layer | Draw explicit boundaries and place each action inside its owner |

Split the image when two grammars compete for attention. A hierarchy can include a small result lane, but it should not also become a full state-transition comparison.

## Build the teaching model

Write one sentence before drawing: “After reading this image, the learner can explain ___.” Remove content that does not support that sentence.

Build the image from these parts as applicable:

```text
concrete scenario -> responsibility -> relationship -> mechanism -> result -> boundary
```

Use these rules:

- Carry one named example from input to result. Prefer `user_events`, `E7`, or another value already used by the lesson over generic A/B boxes.
- Name objects with formal domain terms after the surrounding tutorial has established their plain-language role.
- Put actions on connections: `returns current metadata location`, `reads`, `publishes`, `rewrites`, or `filters`.
- Distinguish control, reference, and data movement when the distinction changes the model. Use labels, line styles, or a compact legend.
- Show important unchanged objects in before/after diagrams so the learner sees the actual delta.
- End with an observable result or compact reconstruction sentence.
- Put limitations beside the component or mechanism they constrain, after its positive role is clear.

Use visual grouping to express ownership. Background bands, labeled boundaries, alignment, and whitespace should tell the learner which objects belong together before color is considered.

## Construct a robust SVG

Create a self-contained UTF-8 SVG with no remote images, stylesheets, scripts, or fonts.

Start with this structure and replace every placeholder:

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     width="1200" height="800" viewBox="0 0 1200 800"
     role="img" aria-labelledby="title desc">
  <title id="title">Specific diagram title</title>
  <desc id="desc">What objects, relationships, and result the diagram shows.</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10"
            refX="9" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 Z" fill="#344054"/>
    </marker>
    <style>
      .title { font: 700 32px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #101828; }
      .body { font: 400 18px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #344054; }
    </style>
  </defs>
  <rect width="1200" height="800" fill="#F8FAFC"/>
  <!-- Teaching content -->
</svg>
```

Set numeric `width`, `height`, and a matching `viewBox`. Leave margin on every edge. Increase the canvas height when content grows; do not compress text to rescue an undersized canvas.

Use `<defs>` for shared markers, filters, and styles. Give every referenced definition a unique ID. Reference arrows with `marker-end="url(#arrow)"` and keep arrowheads outside target boxes.

Use text elements rather than text converted to paths. Use locally available system-font stacks. Wrap long labels into explicit `<text>` lines or `<tspan>` elements because SVG does not wrap text automatically. Escape XML characters such as `&`, `<`, and `>`.

Keep the Markdown reference relative to the tutorial file:

```markdown
![A query follows Catalog, Metadata JSON, Snapshot, and Manifest metadata to reach data files](assets/iceberg-metadata-hierarchy.svg)
```

Write alt text that states the model, not “diagram” or the filename. Keep the nearby prose useful when the image cannot be displayed.

## Keep the image readable and accessible

- Use a single reading direction unless a clearly separated comparison requires parallel lanes.
- Use at least 16 px body text for a large teaching canvas; use larger text for section and object titles.
- Keep line spacing, internal padding, and gaps consistent. Use an 8 px spacing rhythm when it fits the repository style.
- Keep card corners at 8 px or less unless the repository has another convention.
- Reserve saturated color for identity, state, or emphasis. Use neutral surfaces and more than color alone to convey meaning.
- Maintain readable foreground/background contrast. Pair red/green state colors with words or symbols.
- Keep every label within its container at desktop and narrow rendered widths.
- Preserve readable type at narrow widths. Split a dense diagram, create a narrow-layout variant, or place it in a horizontally scrollable figure with a sensible minimum width and an original-size link. Do not shrink a large canvas until its labels become unreadable merely to remove horizontal overflow.
- Route arrows through whitespace. Keep arrow lines away from labels and state what each non-obvious arrow means.
- Keep diagrams flat and information-dense. Avoid decorative cards, nested cards, gradients, or ornamental shapes.
- Use whitespace and boundaries before shadows. Use a subtle shadow only when it clarifies foreground grouping.
- Set `role="img"`, provide non-empty `<title>` and `<desc>` elements with unique IDs, and reference both IDs from `aria-labelledby`.

## Choose SVG versus another medium

Use SVG when exact placement, labeled relationships, stable rendering, and repository-reviewable source improve learning.

Prefer another medium when it carries the lesson more directly:

| Medium | Prefer it when |
| --- | --- |
| Prose | One idea fits in a short causal explanation |
| Table | Readers compare repeated fields, options, or exact mappings |
| Code plus output | Syntax, execution order, or observable runtime behavior is central |
| Mermaid | The graph or sequence is simple and text-native maintenance matters most |
| Screenshot | Learners must recognize a real UI, command output, or current product state |
| Raster image | Physical appearance, atmosphere, illustration, or texture matters more than exact labels |

Do not add an SVG merely to make a page feel visual. Add it when the learner would otherwise need to hold several relationships in working memory.

## Validate structure, rendering, and meaning

Run the bundled structural validator:

```bash
python3 <skill-dir>/scripts/validate_svg.py path/to/diagram.svg
```

Then serve or open the containing tutorial and inspect the full diagram at desktop and narrow widths. Check:

1. Every text line fits its box and remains readable.
2. Nodes, labels, and arrows do not overlap.
3. Arrow direction and labels match the described mechanism.
4. The last row and summary are inside the canvas.
5. Color and contrast preserve grouping without becoming the only signal.
6. Terms, example values, and object ownership match the tutorial.
7. Every range, count, and summary covers the concrete objects it claims to describe.
8. The learner can reconstruct the intended model from the image and alt text.

At narrow widths, verify readability rather than only checking for overflow. A fully visible image still fails when the learner must zoom to read its labels.

Treat the structural validator as a fast gate. It cannot prove visual quality or technical truth.

## Reusable Iceberg examples

Use the Iceberg examples to learn the grammar, not as a template to copy blindly.

### Metadata hierarchy

Question: How does a logical table name lead to the files read by a query?

```text
Catalog
  -> Metadata JSON
  -> current Snapshot
  -> Manifest List
  -> selected Manifest
  -> Data File + Delete File
```

Make each arrow an action or reference. Show the query planner beside the hierarchy so partition and column-statistics pruning appear at the level where they happen. Carry one query and actual metadata/file names through the chain.

### Copy-on-Write versus Merge-on-Read

Question: When row E7 changes, which files change now and which work moves to reads?

Use two aligned lanes with the same starting file and the same updated row. In each lane show:

```text
before files -> update action -> after files -> write cost -> read cost
```

Copy-on-Write should visibly replace the affected data file. Merge-on-Read should retain the data file and add deletion/new-row information. Keep the comparison about file mechanics rather than generic “faster/slower” labels.
