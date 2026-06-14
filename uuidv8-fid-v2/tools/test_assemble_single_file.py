import os
import shutil
import subprocess
import sys
import tempfile
import unittest

def get_repo_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, "..", ".."))

class TestAssembleSingleFile(unittest.TestCase):
    def setUp(self):
        self.repo_root = get_repo_root()
        self.tool_path = os.path.join(self.repo_root, "uuidv8-fid-v2", "tools", "assemble_single_file.py")

    def run_tool(self, args, cwd=None):
        cmd = [sys.executable, self.tool_path] + args
        if cwd is None:
            cwd = self.repo_root
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

    def test_check_mode_success(self):
        res = self.run_tool(["--check"])
        self.assertEqual(res.returncode, 0, f"Check mode failed: {res.stderr}")

    def test_stdout_mode(self):
        res = self.run_tool(["--stdout"])
        self.assertEqual(res.returncode, 0, f"Stdout mode failed: {res.stderr}")
        self.assertIn("This is generated dry-run output assembled from the split UUIDv8-FID-v2 source files.", res.stdout)
        self.assertIn("format_id = (format_type << 4) | format_subtype", res.stdout)
        self.assertIn("xxxxxxxx-xxxx-8T00-8S00-xxxxxxxxxxxx", res.stdout)
        self.assertIn("0x10", res.stdout)
        self.assertIn("0x7a", res.stdout)

    def test_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy just enough files to test, omitting one required file
            uuid_dir = os.path.join(tmpdir, "uuidv8-fid-v2")
            os.makedirs(uuid_dir)
            os.makedirs(os.path.join(uuid_dir, "formats"))
            os.makedirs(os.path.join(uuid_dir, "tools"))

            # Copy tool
            shutil.copy2(self.tool_path, os.path.join(uuid_dir, "tools", "assemble_single_file.py"))

            # Run tool from temp dir (it looks for uuidv8-fid-v2/... from repo root, which will be tmpdir)
            # The tool looks for files relative to its repo root, so we should run it like:
            cmd = [sys.executable, os.path.join(uuid_dir, "tools", "assemble_single_file.py"), "--check"]
            res = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("Error: Missing required source file:", res.stderr)

    def test_output_inside_repo_fails_without_force(self):
        # Trying to write to the root of the repo
        output_path = os.path.join(self.repo_root, "uuidv8-fid-v2", "generated.md")
        res = self.run_tool(["--output", output_path])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Refusing to write output inside the repository without --force", res.stderr)

    def test_output_outside_repo_succeeds(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "generated.md")
            res = self.run_tool(["--output", output_path])
            self.assertEqual(res.returncode, 0, f"Writing output failed: {res.stderr}")
            self.assertTrue(os.path.exists(output_path))
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("This is generated dry-run output assembled from the split UUIDv8-FID-v2 source files.", content)

if __name__ == "__main__":
    unittest.main()
