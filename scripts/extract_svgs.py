import re
import json
from pathlib import Path

def extract_svgs():
    app_jsx_path = Path("gallery-app/src/App.jsx")
    
    with open(app_jsx_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find Bases block
    bases_match = re.search(r'const Bases = \{(.*?)\};\n\n// Badges', content, re.DOTALL)
    if not bases_match:
        print("Could not find Bases block")
        return
    bases_block = bases_match.group(1)

    # Find Badges block
    badges_match = re.search(r'const Badges = \{(.*?)\};\n\n// --- 2\.', content, re.DOTALL)
    if not badges_match:
        print("Could not find Badges block")
        return
    badges_block = badges_match.group(1)

    def parse_components(block, comp_type, default_viewbox):
        components = {}
        # Pattern looks for: Name: (props) => (<svg viewBox="..." ...>{...}</svg>),
        # We need to extract the Name and inner contents of the <svg> tag.
        # Adjusted pattern to be more resilient to whitespace and newlines
        pattern = re.compile(r'(\w+):\s*\(props\)\s*=>\s*\(\s*<svg[^>]*>(.*?)</svg>\s*\)', re.DOTALL)
        
        for match in pattern.finditer(block):
            name = match.group(1)
            inner_svg = match.group(2).strip()
            
            # Remove JSX comments
            inner_svg = re.sub(r'\{/\*.*?\*/\}', '', inner_svg, flags=re.DOTALL)
            
            # Fix JSX specific attributes back to standard SVG if needed
            inner_svg = inner_svg.replace('className=', 'class=')
            inner_svg = inner_svg.replace('strokeWidth=', 'stroke-width=')
            inner_svg = inner_svg.replace('strokeLinecap=', 'stroke-linecap=')
            inner_svg = inner_svg.replace('strokeLinejoin=', 'stroke-linejoin=')
            inner_svg = inner_svg.replace('fillRule=', 'fill-rule=')
            inner_svg = inner_svg.replace('clipRule=', 'clip-rule=')
            inner_svg = inner_svg.replace('strokeDasharray=', 'stroke-dasharray=')
            
            components[name] = {
                "type": comp_type,
                "viewBox": default_viewbox,
                "content": inner_svg
            }
        return components

    bases = parse_components(bases_block, "base", "0 0 32 32")
    badges = parse_components(badges_block, "badge", "0 0 16 16")

    catalog = {
        "bases": bases,
        "badges": badges
    }

    output_path = Path("assets/pictograms.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")
    
    print(f"Extracted {len(bases)} bases and {len(badges)} badges to {output_path}")

if __name__ == "__main__":
    extract_svgs()
