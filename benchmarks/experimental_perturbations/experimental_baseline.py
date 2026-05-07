import reviewer.prompts as p               
import json 
from pathlib import Path

from reviewer.method_progressive import review_progressive
from reviewer.method_zero_shot import review_zero_shot


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
    output_dir = Path("./baseline_comments")
    method = "progressive"                                                                                                                                     
    review_experimental(perturbations_dir, output_dir, method)