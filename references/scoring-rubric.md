# Five-dimensional scoring rubric

Score the final candidate against the post, relevant comments, and supplied
context. Use integer scores from 0 through 5. Cite a short observable reason,
not private chain-of-thought. Judge the contribution rather than polish alone.

| Score | Relevance | Usefulness | Naturalness | Novelty | Social fit |
| --- | --- | --- | --- | --- | --- |
| 0 | Unrelated to the actual point. | Adds nothing or actively obstructs. | Incoherent, obviously templated, or severely awkward. | Repeats existing content without added value. | Wrong tone, depth, or interaction style. |
| 1 | Shares a word or theme but misses the intent. | Empty praise or unsupported assertion. | Stock phrasing dominates and does not fit the exchange. | Cosmetic restatement of the post or a comment. | Intrusive, dismissive, or markedly mistimed. |
| 2 | Discusses an adjacent issue; main need is mostly unmet. | Minor value but leaves the central need unresolved. | Understandable but stiff, padded, or forced. | Small detail that does little beyond existing replies. | Partly appropriate but too long, technical, or casual. |
| 3 | Addresses part of the point with a material omission or tangent. | Helps somewhat; lacks needed specificity or a next step. | Mostly readable with noticeable formulaic wording. | Relevant extension with substantial overlap. | Broadly suitable with a noticeable mismatch. |
| 4 | Directly addresses the point with only a minor omission. | Clear, specific help or welcome acknowledgment; small limits remain. | Fluent and proportionate with minor awkwardness. | Distinct useful addition absent from the thread. | Well matched with a minor tone or timing issue. |
| 5 | Precisely addresses the author's actual point and constraints. | Materially improves this conversation or resolves its current need. | Appropriate, natural expression without filler or deceptive persona. | Genuinely new value for this conversation. | Very well matched to situation, audience, tone, depth, and timing. |

## Gate

Maximum: 25. The default candidate publishing threshold is **18/25**, with
**relevance >= 4** and **all safety rules passing**. Safety failure or relevance
below 4 means **DO NOT POST**, regardless of total. Apply permission and the
useful-reason check separately. A passing score is necessary, not sufficient.
A reviewer can reject a high-scoring response when silence is the better action.

Safety, honesty, and authorization are gates, not bonus points that compensate
for weak relevance. Continuity affects relevance, usefulness, and novelty; a
separate sixth numeric dimension is not needed. Score after final edits.

## Calibration and edge cases

- An eloquent tangent might score 2/3/5/5/3 = 18. It still fails relevance.
- A direct but generic answer scoring 4/2/3/2/3 = 14 fails the total threshold.
- A helpful candidate scoring 4/4/4/3/3 = 18 passes the numeric gate exactly;
  inspect safety, authorization, and whether that remaining mismatch matters.
- A polished request for secrets fails safety even if an evaluator rates every
  dimension 5. Never let arithmetic excuse a violation.
- A short welcome can score 5/4/5/4/5 = 23 when a newcomer seeks contact and
  nobody has welcomed them. Novelty means new value in this thread, not a new
  invention. The same welcome after many equivalent replies may deserve 0–1
  novelty and no response at all.
- A necessary follow-up can repeat context while adding an unresolved answer.
  Score the new contribution, not lexical overlap. A paraphrase is not novel
  merely because it uses different words.
- A correction may be socially useful even if unpopular. Respectful disagreement
  does not lose social-fit points merely for disagreeing.
- Technical detail is not inherently unnatural. Depth is appropriate when the
  question and audience warrant it; plain language is not compulsory brevity.
- Humor and dialect vary by community. Do not equate one language or polished
  formal English with naturalness. Use context-aware reviewers when possible.
- Missing thread history makes novelty uncertain. Do not assign a confident 5;
  obtain context or defer. Lack of evidence is not evidence of uniqueness.
- `NO RESPONSE` is an action, not a candidate to score 0/25. Evaluate whether
  silence was justified separately; report response scores as not applicable.

## Reviewer procedure

First identify the author's need and whether a reply is warranted. Read existing
comments. Inspect safety and honesty. Then assign all five scores independently
using the anchors, giving one short evidence-based note for borderline scores.
Review action choice separately from wording quality. Resolve disagreements by
comparing evidence, not by averaging away a safety failure. Record uncertainty
and alternative plausible actions. Scores are experimental judgments; 18 is a
starting policy, not a validated universal boundary.
