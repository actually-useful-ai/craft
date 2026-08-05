# Language classification and exploration

## Evaluator

A visitor locating one language in the whole and a linguist inspecting why that placement exists.

## Governing principle

Repair the ontology before drawing the tree.

## Exemplar signals

- Represent language, variety, historical stage, proto-language, family, subfamily, grouping, mixed language, creole, sign language, isolate, unclassified language, and disputed grouping separately.
- Retain stable identifiers, alternate names, classification source and version, status, geography, date range, and normalization history.
- Distinguish primary classification edges from cross-references and alternate analyses.
- Use coordinated overview, branch, and entity-detail scales.
- Keep a visible path to the global context while exploring a branch.
- Provide accessible textual and tabular alternatives to graphics.
- Represent non-tree structures honestly.

## Expert-noticed distinctions

- Classification membership versus direct historical descent.
- Grouping nodes versus language entities.
- Geographic proximity versus genetic relationship.
- Historical stages versus timeless taxonomy.
- Source disagreement versus low numeric confidence.
- Tree-export compatibility versus a graph that cannot be represented as Newick.

## Anti-patterns

- Choosing a graph library before defining entities and questions.
- Rendering thousands of nodes as one indented list or force graph.
- Using branch area to imply speaker count without encoding and labeling it.
- Forcing mixed, sign, disputed, or multiply classified languages into one biological-tree metaphor.
- Generated descriptions that replace available structured metadata.

## Evidence standard

Each classification edge retains source, version, relation type, status, confidence category, import timestamp, and normalization decisions.

## Acceptance checks

- A visitor can locate the selected language within seconds.
- An expert can inspect the source and alternatives for the placement.
- Entity types and disputed relations are perceivable without color alone.
- The interface remains useful at thousands of entities.
