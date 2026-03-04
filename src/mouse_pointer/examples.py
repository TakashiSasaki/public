import subprocess
from pathlib import Path

def main() -> None:
    # Project root is 3 levels up from src/mouse_pointer/examples.py
    root_dir = Path(__file__).parent.parent.parent
    examples_dir = root_dir / "examples"
    static_dir = examples_dir / "static"
    animated_dir = examples_dir / "animated"
    
    static_dir.mkdir(parents=True, exist_ok=True)
    animated_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating Static Examples...\n")
    
    # 1. Basic Purple Arrow
    print(" -> static/basic_purple_arrow.cur")
    subprocess.run([
        "mouse-pointer", "generate", 
        "--color", "#800080", 
        "--shape", "arrow", 
        "--drop-shadow", 
        "--output", str(static_dir / "basic_purple_arrow.cur")
    ], check=True)
    
    # 2. GitHub Repo Cross
    print(" -> static/github_repo_cross.cur")
    subprocess.run([
        "mouse-pointer", "generate", 
        "--color", "#24292e", 
        "--shape", "cross", 
        "--base-name", "github", 
        "--badge1-name", "repository", 
        "--output", str(static_dir / "github_repo_cross.cur")
    ], check=True)
    
    # 3. Annotated Triangle
    print(" -> static/annotated_triangle.cur")
    subprocess.run([
        "mouse-pointer", "generate", 
        "--color", "#ff0000", 
        "--shape", "triangle", 
        "--tr-text", "REC", "--tr-bg-color", "black", "--tr-color", "red", 
        "--mr-text", "v1", "--mr-bg-color", "white", 
        "--caption-text", "録画中", "--caption-bg-color", "#ffff00", "--caption-color", "black", 
        "--output", str(static_dir / "annotated_triangle.cur")
    ], check=True)
    
    print("\nGenerating Animated Examples...\n")
    
    # 4. Waving Gradient Arrow
    print(" -> animated/waving_gradient_arrow.ani")
    subprocess.run([
        "mouse-pointer", "generate", 
        "--color", "#800080", 
        "--shape", "arrow", 
        "--drop-shadow", 
        "--anim-gradient", 
        "--anim-frames", "30", 
        "--anim-speed", "5", 
        "--output", str(animated_dir / "waving_gradient_arrow.ani")
    ], check=True)
    
    # 5. Scrolling Warning Caption
    print(" -> animated/scrolling_warning.ani")
    subprocess.run([
        "mouse-pointer", "generate", 
        "--color", "#ffaa00", 
        "--shape", "triangle", 
        "--caption-text", "WARNING! High Temperature", 
        "--caption-bg-color", "black", 
        "--caption-color", "yellow", 
        "--anim-scroll", 
        "--anim-frames", "45", 
        "--anim-speed", "6", 
        "--output", str(animated_dir / "scrolling_warning.ani")
    ], check=True)
    
    # 6. Disco Cursor
    print(" -> animated/disco_cursor.ani")
    subprocess.run([
        "mouse-pointer", "generate", 
        "--color", "#00ffff", 
        "--border-color", "#ff00ff", 
        "--shape", "cross", 
        "--caption-text", "PARTY TIME!", 
        "--anim-gradient", 
        "--anim-scroll", 
        "--anim-frames", "20", 
        "--anim-speed", "8", 
        "--output", str(animated_dir / "disco_cursor.ani")
    ], check=True)
    
    print(f"\nGeneration Complete! Examples are located in:\n{examples_dir}")

if __name__ == "__main__":
    main()
