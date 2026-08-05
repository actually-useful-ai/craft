# Corpus linguistics

## Evaluator

A corpus linguist judging sampling, normalization, metadata, comparability, and reproducibility.

## Governing principle

Do not let a polished query interface imply evidence the corpus cannot support.

## Exemplar signals

- State whether each corpus is available, indexed, partially loaded, planned, or only supported by code.
- Preserve date, genre, register, source, author, annotation, and corpus provenance where available.
- Report token frequency, document frequency, dispersion, and salience distinctly.
- Normalize frequency against an appropriate denominator.
- Explain comparability across period, size, genre, orthography, transcription, and annotation.
- Treat spelling variation, lemmatization, and historical-language modeling explicitly.
- Export the query, filters, exclusions, denominator, dataset version, and matching contexts.

## Expert-noticed distinctions

- Current holdings versus projected holdings.
- Raw count versus normalized rate.
- Frequency versus dispersion.
- Code-complete support versus an operational corpus.
- Corpus absence versus historical absence.
- Modern model output versus historically valid annotation.

## Anti-patterns

- Comparing raw counts across unequal corpora.
- Filling period gaps silently.
- Treating one sentiment model as neutral across genres and centuries.
- Presenting corpus breadth without sampling limitations.
- Using frequency as etymological evidence.

## Acceptance checks

- The query and result can be reproduced.
- Every comparison states its denominator and compatibility caveats.
- Missing periods and weak coverage remain visible.
- Exported rows preserve source metadata and licensing requirements.
