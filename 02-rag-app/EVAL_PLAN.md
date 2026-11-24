# Evaluation plan

## Goal
<One sentence: what decision will this evaluation support?>

## Question set
- Development set: <40> questions (tune on these).
- Held-out test set: <20> questions (read once, at the end).
- Composition target (per set, roughly):
  | Type | Share |
  |---|---|
  | exact-term (codes, IDs) | <15%> |
  | paraphrase (little word overlap) | <25%> |
  | direct | <25%> |
  | multi-chunk (needs two or more chunks) | <10%> |
  | unanswerable (not in the documents) | <15%> |
  | restricted at a lower access level | <10%> |
- Each question records: text, type, level asked at, gold evidence labels
  (any-of or all-of), and a short gold answer or "should refuse".

## Labelling rules
- A chunk is relevant if <rule, e.g. it contains the information needed to
  answer, not merely the same topic>.
- Questions are written <by whom, and when relative to reading the documents>.

## Metrics and pass marks (set before running)
| Metric | Definition | Pass mark |
|---|---|---|
| hit@3 | correct chunk in top 3 | >= <0.90> |
| MRR | mean reciprocal rank | >= <0.80> |
| Correct-refusal rate | refused / unanswerable | >= <0.90> |
| False-refusal rate | wrongly refused / answerable | <= <0.10> |
| Access leaks | restricted chunks shown to lower levels | exactly 0 |
| Citation validity | cited IDs that were retrieved | 100% |
| Faithfulness | <method decided in Hour 4> | >= <0.90> |

## Process
1. Tune on the development set only.
2. Freeze all settings (chunking, retriever, threshold, prompt).
3. Run the held-out set once and record the results, whatever they are.
4. Report intervals, not only point values.

## Known limits
<Corpus size, fictional documents, who wrote the questions, judge reliability.>