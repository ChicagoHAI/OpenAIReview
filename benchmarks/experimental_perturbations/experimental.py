import reviewer.prompts as p               
import json 
from pathlib import Path

from reviewer.parsers import parse_document                                                                                                                                          
from reviewer.method_progressive import review_progressive 

p.DEEP_CHECK_PROMPT = f"""{p.REVIEWER_PREAMBLE}                                                                                                                                      
                                                                                                                                                                                       
{{ocr_caveat}}
                                                                                                                                                                                       
CONTEXT:        
{{context}}
            
---
    
PASSAGE TO CHECK:
{{passage}}      
                                                                                                                                                                                    
---
                                                                                                                                                                                    
Check for:
1. Mathematical correctness (e.g. wrong formulas, sign errors, missing factors, incorrect derivations, subscript or index errors)
2. Notation inconsistencies (e.g. symbols used differently than defined, undefined notation)
3. Definition/Theorem inconsistencies (e.g. statements that contradict formal definitions/theorems)
4. Numerical inconsistencies (e.g. stated values contradict what can be derived from definitions, tables, or other sections)
5. Insufficient justification (e.g. skipped non-trivial step in derivation)
6. Overclaiming (e.g. statements that claim more than the evidence supports)
7. Ambiguity (e.g. lack of detail/specification that could lead reader to incorrect conclusions)

Pay PARTICULAR attention to EXPERIMENTAL errors (e.g. poor experimental design, p-hacking, incorrect interpretation of data)
                        
{p.EXPLANATION_STYLE}
                    
{p.LENIENCY_RULES}                                                                                                                                                                   
                
{p.DO_NOT_FLAG_CHUNKED}                                                                                                                                                              
                        
{p.JSON_ARRAY_OUTPUT}"""     


def review_experimental(perturbations_dir, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
                                                                                                                                                                                    
    for category_dir in perturbations_dir.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("."):                                                                                                           
            continue                                                                                                                                                                 

        for paper_dir in (category_dir / "all").iterdir():                                                                                                                           
            if not paper_dir.is_dir():
                continue

            md_files = list((paper_dir / "experimental").glob("*recorrupted.md"))                                                                                                    
            if not md_files:
                continue                                                                                                                                                             
            md_file = md_files[0]

            slug = paper_dir.name
            output_path = output_dir / f"{slug}.json"
            if output_path.exists():                                                                                                                                                 
                print(f"  Skipping {slug} (already done)")
                continue                                                                                                                                                             
                
            print(f"Reviewing {slug}...")
            text = md_file.read_text()
            consolidated, _ = review_progressive(                                                                                                                                    
                paper_slug=slug,
                document_content=text,                                                                                                                                               
                model="anthropic/claude-opus-4-6",
            )
            with open(output_path, "w") as f:                                                                                                                                        
                json.dump(consolidated.to_dict(), f, indent=2)

if __name__ == "__main__":
    perturbations_dir = Path("./perturbation_results")                                                                                                       
    output_dir = Path("./experimental_comments")                                                                                                                                     
    review_experimental(perturbations_dir, output_dir)