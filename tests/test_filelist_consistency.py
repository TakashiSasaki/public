from get_a_grip.tools.filelist import rglob, scandir, walk
from get_a_grip.tools.filelist.utils import compare_filelists

def test_consistency_scandir_rglob_walk(tmp_path):
    """
    Verify that rglob, scandir, and walk implementations produce identical results from a real filesystem scan.
    """
    # Setup robust test environment
    root = tmp_path / "consistency_root"
    root.mkdir()
    
    (root / "file1.txt").write_text("Hello World")
    
    subdir = root / "subdir"
    subdir.mkdir()
    (subdir / "file2.bin").write_bytes(b"\x00\x01\x02")
    
    # Nested deeply
    deep = subdir / "deep" / "structure"
    deep.mkdir(parents=True)
    (deep / "deep_file.log").write_text("Log")
    
    target_path = str(root.resolve())
    
    # Execute all scanning methods
    print(f"Scanning {target_path} with rglob...")
    res_rglob = rglob.scan(target_path)
    
    print(f"Scanning {target_path} with scandir...")
    res_scandir = scandir.scan(target_path)
    
    print(f"Scanning {target_path} with walk...")
    res_walk = walk.scan(target_path)
    
    # Compare
    # scandir vs rglob
    compare_filelists(res_scandir, res_rglob, "scandir", "rglob")
    
    # scandir vs walk
    compare_filelists(res_scandir, res_walk, "scandir", "walk")
    
    # walk vs rglob (transitive, but good to check explicit edge cases if any)
    compare_filelists(res_walk, res_rglob, "walk", "rglob")
