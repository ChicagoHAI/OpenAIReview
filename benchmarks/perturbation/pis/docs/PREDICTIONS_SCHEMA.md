Verifier predictions schema (input to PIS analysis)
JSONL, one object per example:

{"uid": "paper_001::P004_S0001", "pred_label": "substantive"}
uid MUST be the composite key "<paper>::<perturbation_id>" becauseperturbation_id alone is NOT unique across papers in the gold set.
pred_label is the existing verifier's verdict. Labels are normalized(lowercase, _/space -> -) before comparison with gold.Expected values: "substantive" | "typo-shaped" | "not-an-error".
Optional: "judgments": {...} (well-formedness, evidence availability,contradiction confirmation, typo/cosmetic) — reserved for future controls,currently ignored.
Use scripts/convert_predictions.py to convert the repo verifier's raw output.Run it with --inspect first if the raw format is unknown.