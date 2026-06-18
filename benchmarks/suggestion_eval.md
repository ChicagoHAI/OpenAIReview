# Suggestion Field Evaluation

This is a small qualitative evaluation for the `suggestion` field added to review
comments. I inspected existing benchmark review outputs and checked whether the
new field would make the comment more actionable for an author revising a paper.

## Method

- Sampled three existing review comments from benchmark visualization data.
- For each comment, compared the existing `message`/`explanation` with the new
  required `suggestion` field in the prompt schema.
- Scored the expected suggestion target with a simple rubric:
  - **Specific**: names the exact revision or check to perform.
  - **Actionable**: gives the author a concrete next step.
  - **Grounded**: follows from the quoted issue rather than adding a new claim.

## Results

| Review comment | Existing behavior | Expected suggestion after this PR | Rubric result |
| --- | --- | --- | --- |
| Standard deviation of input counts in Appendix A.1 | Explains that a Poisson standard deviation is written as `m_k K` when it should be `sqrt(K m_k)`. | "Replace `sigma(n_k)=m_k K` with `sigma(n_k)=sqrt(K m_k)` and keep the next sentence's variance statement as `Var(n_k)=K m_k`." | Specific, actionable, grounded |
| Incorrect variance term in `q_k` expression | Explains that threshold variance is inconsistently treated as `Delta` instead of `Delta^2`. | "Rewrite the text and equation so threshold heterogeneity contributes variance `Delta^2`, including the combined term `sqrt(Delta^2 + beta_k)`." | Specific, actionable, grounded |
| Discrepancy regarding stability boundaries | Explains that the text says `tau_L < tau_G` while figure values imply `tau_L > tau_G`. | "Change the sentence to state `tau_L` is larger than `tau_G` for these parameters, or add a note if the plotted labels use a different convention." | Specific, actionable, grounded |

## Notes

The evaluation suggests that a separate `suggestion` field is useful because the
current explanations often contain enough reasoning to diagnose the problem but
bury the author's next action in prose. Requiring suggestions in every prompt,
preserving them in parsing/export, and rendering them in the viz UI makes the
revision step explicit.

## Follow-up

A larger evaluation should run 20-30 model-generated reviews and score suggestion
quality for specificity, correctness, and usefulness. This could become a small
benchmark that compares prompt variants for comment quality.
