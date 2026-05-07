import reviewer.prompts as p
import reviewer.method_progressive as mp
import reviewer.method_zero_shot as mzs
import json
from pathlib import Path

from reviewer.method_progressive import review_progressive
from reviewer.method_zero_shot import review_zero_shot

# ── Zero-shot prompts (EDITED) ───────────────────────────────────────────────────────

mzs.ZERO_SHOT_PROMPT = f"""{p.REVIEWER_PREAMBLE}

{{ocr_caveat}}

---

PAPER:

{{paper_text}}

---

Check specifically for EXPERIMENTAL errors. This includes poor experimental design, instances of p-hacking, and incorrect interpretation of data/results. 
                        
{p.EXPLANATION_STYLE}

{p.LENIENCY_RULES}

{p.DO_NOT_FLAG_BASE}

Return a JSON object with this structure:
{{{{
  "overall_feedback": "one paragraph high-level assessment of the paper's quality and main issues",
  "comments": [
    {{{{
      "title": "concise title of the issue",
      "quote": "exact verbatim text from the paper (preserving LaTeX)",
      "explanation": "precise explanation of what is wrong and why",
      "type": "technical" or "logical"
    }}}}
  ]
}}}}

Return ONLY the JSON object. No other text."""

mzs.ZERO_SHOT_CHUNK_PROMPT = f"""{p.REVIEWER_PREAMBLE}

{{ocr_caveat}}

---

PASSAGE TO CHECK:

{{chunk_text}}

---

Check specifically for EXPERIMENTAL errors. This includes poor experimental design, instances of p-hacking, and incorrect interpretation of data/results. 
                        
{p.EXPLANATION_STYLE}

{p.LENIENCY_RULES}

{p.DO_NOT_FLAG_CHUNKED}

Return a JSON object with this structure:
{{{{
  "overall_feedback": "brief assessment of this section",
  "comments": [
    {{{{
      "title": "concise title of the issue",
      "quote": "exact verbatim text from the paper (preserving LaTeX)",
      "explanation": "precise explanation of what is wrong and why",
      "type": "technical" or "logical"
    }}}}
  ]
}}}}

Return ONLY the JSON object. No other text."""

# ── Progressive prompt (EDITED) ───────────────────────────────────────────────────────

mp.DEEP_CHECK_PROMPT = f"""{p.REVIEWER_PREAMBLE}                                                                                                                                      
                                                                                                                                                                                       
{{ocr_caveat}}
                                                                                                                                                                                       
CONTEXT:        
{{context}}
            
---
    
PASSAGE TO CHECK:
{{passage}}      
                                                                                                                                                                                    
---
                                                                                                                                                                                    
Check specifically for EXPERIMENTAL errors. This includes poor experimental design, instances of p-hacking, and incorrect interpretation of data/results. 
                        
{p.EXPLANATION_STYLE}
                    
{p.LENIENCY_RULES}                                                                                                                                                                   
                
{p.DO_NOT_FLAG_CHUNKED}                                                                                                                                                              
                        
{p.JSON_ARRAY_OUTPUT}"""     


def review_experimental(perturbations_dir, output_dir, method):
    output_dir.mkdir(parents=True, exist_ok=True)
                                                                                                                                                                                    
    for category_dir in perturbations_dir.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("."):                                                                                                           
            continue                                                                                                                                                                 

        paper_dir = next((p for p in (category_dir / "all").iterdir() if p.is_dir()), None)
        if paper_dir is None:
            continue

        md_files = list((paper_dir / "experimental").glob("*recorrupted.md"))                                                                                                    
        if not md_files:
            continue                                                                                                                                                             
        md_file = md_files[0]

        slug = paper_dir.name
        output_path = output_dir / method / f"{slug}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():                                                                                                                                                 
            print(f"  Skipping {slug} (already done)")
            continue                                                                                                                                                             
            
        print(f"Reviewing {slug}...")
        text = md_file.read_text()

        if method == "progressive":
            consolidated, _ = review_progressive(
                paper_slug=slug,
                document_content=text,
                model="anthropic/claude-opus-4-6",
                reasoning_effort=None,
                window_size=3,
                ocr=False,
            )
            with open(output_path, "w") as f:                                                                                                                                        
                json.dump(consolidated.to_dict(), f, indent=2)
        elif method == "zero_shot":
            result = review_zero_shot(
                paper_slug=slug,
                document_content=text,
                model="anthropic/claude-opus-4-6",
                reasoning_effort=None,
                ocr=False,
            )
            with open(output_path, "w") as f:
                json.dump(result.to_dict(), f, indent=2)

if __name__ == "__main__":
    perturbations_dir = Path("./perturbation_results")                                                                                                       
    output_dir = Path("./experimental_comments")
    method = "progressive"                                                                                                                                     
    review_experimental(perturbations_dir, output_dir, method)