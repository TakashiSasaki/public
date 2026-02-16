
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Ensure we can import from src
sys.path.append(os.path.join(os.getcwd(), 'src'))

# specific import after path modification if needed, 
# or we can patch 'sys.platform' before importing if the module has immediate checks.
# However, since the module raises OSError at the top level if not win32, 
# we need to ensure we are testing on win32 or mocking it effectively *before* import if we were on non-windows.
# But here we are on Windows, so safe to import.
# To be safe for cross-platform test running, we might need `sys.modules` patching,
# but for now we assume running on Windows or just test the logic that is accessible.

# Since the user requested "environment check", the module execution will fail if not win32.
# We will mock sys.platform to 'win32' for the duration of tests if we needed to reload.
# But since we are on Windows, we can just import.

try:
    from get_a_grip.core import path_parser
except OSError:
    # If we are running tests on non-Windows (CI?), we need to verify the OSError is raised,
    # but for testing the functions, we'd need to bypass that check.
    # Since the check is at module level, it runs on import.
    path_parser = None

class TestPathParser(unittest.TestCase):

    def setUp(self):
        # Determine if we successfully imported the module
        if path_parser is None:
            self.skipTest("path_parser module could not be imported (likely not on Windows)")

    @patch('os.environ')
    def test_get_path_from_environment(self, mock_environ):
        # Mock PATH environment variable
        mock_environ.get.return_value = "C:\\Path1;C:\\Path2"
        
        # We also need to ensure os.pathsep is ';' which it is on Windows.
        # If running on non-windows, this test might need os.pathsep patched too if the code uses real os.pathsep.
        # The code uses `os.pathsep`. 
        with patch('os.pathsep', ';'):
            paths = path_parser.get_path_from_environment()
            self.assertEqual(paths, [Path("C:\\Path1"), Path("C:\\Path2")])

    @patch('os.environ')
    def test_get_path_from_environment_empty(self, mock_environ):
        mock_environ.get.return_value = ""
        with patch('os.pathsep', ';'):
            paths = path_parser.get_path_from_environment()
            self.assertEqual(paths, [])

    @patch('get_a_grip.core.path_parser.winreg')
    def test_get_system_path_from_registry(self, mock_winreg):
        # Setup mock for OpenKey
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.HKEY_LOCAL_MACHINE = MagicMock()
        
        # Setup mock for QueryValueEx
        expected_path = "C:\\SystemPath1;C:\\SystemPath2"
        mock_winreg.QueryValueEx.return_value = (expected_path, 1) # 1 is type REG_SZ usually

        result = path_parser.get_system_path_from_registry()
        
        self.assertEqual(result, [Path("C:\\SystemPath1"), Path("C:\\SystemPath2")])
        mock_winreg.OpenKey.assert_called_with(
            mock_winreg.HKEY_LOCAL_MACHINE, 
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        )
        mock_winreg.QueryValueEx.assert_called_with(mock_key, "Path")

    @patch('get_a_grip.core.path_parser.winreg')
    def test_get_system_path_from_registry_not_found(self, mock_winreg):
        # Simulate FileNotFoundError
        mock_winreg.OpenKey.side_effect = FileNotFoundError
        
        result = path_parser.get_system_path_from_registry()
        self.assertEqual(result, [])

    @patch('get_a_grip.core.path_parser.winreg')
    def test_get_user_path_from_registry(self, mock_winreg):
        # Setup mock for OpenKey
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.HKEY_CURRENT_USER = MagicMock()
        
        # Setup mock for QueryValueEx
        expected_path = "C:\\UserPath1;C:\\UserPath2"
        mock_winreg.QueryValueEx.return_value = (expected_path, 1)

        result = path_parser.get_user_path_from_registry()
        
        self.assertEqual(result, [Path("C:\\UserPath1"), Path("C:\\UserPath2")])
        mock_winreg.OpenKey.assert_called_with(
            mock_winreg.HKEY_CURRENT_USER, 
            r"Environment"
        )
        mock_winreg.QueryValueEx.assert_called_with(mock_key, "Path")

    @patch('get_a_grip.core.path_parser.winreg')
    def test_get_user_path_from_registry_not_found(self, mock_winreg):
        mock_winreg.OpenKey.side_effect = FileNotFoundError
        result = path_parser.get_user_path_from_registry()
        self.assertEqual(result, [])

    @patch('get_a_grip.core.path_parser.get_path_from_environment')
    @patch('os.environ')
    def test_find_command_in_path(self, mock_environ, mock_get_path_from_environment):
        import tempfile
        import shutil

        # Create a temporary directory structure for testing
        # We use strict naming to avoid side effects
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

        dir1 = Path(self.test_dir) / "Dir1"
        dir2 = Path(self.test_dir) / "Dir2"
        dir1.mkdir()
        dir2.mkdir()

        # Create dummy files
        (dir1 / "app.exe").touch()
        (dir2 / "app.bat").touch()
        (dir1 / "script.py").touch()

        # Mock system path to point to these temporary directories
        mock_get_path_from_environment.return_value = [dir1, dir2]
        
        # Setup PATHEXT
        mock_environ.get.return_value = ".EXE;.BAT"

        # Test 1: Find 'app' (should find app.exe and app.bat)
        results = path_parser.find_command_in_path("app")
        
        self.assertEqual(len(results), 2)
        # Sort by name to ensure consistent order for assertion
        # Note: verify actual existence not just string check, though touch() ensures they exist.
        results_sorted = sorted(results, key=lambda p: str(p).lower())
        
        # dir2/app.bat comes after dir1/app.exe alphabetically, but implementation depends on search order
        # search order: Dir1 then Dir2.
        # Dir1 has app.exe. Dir2 has app.bat. 
        # So results[0] should be app.exe, results[1] should be app.bat.
        
        self.assertTrue(results[0].name.lower() == "app.exe")
        self.assertTrue(results[1].name.lower() == "app.bat")
        
        # Verify they are the correct full paths
        self.assertEqual(results[0].resolve(), (dir1 / "app.exe").resolve())
        self.assertEqual(results[1].resolve(), (dir2 / "app.bat").resolve())

        # Test 2: Find 'script.py' (exact extension)
        results = path_parser.find_command_in_path("script.py")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].resolve(), (dir1 / "script.py").resolve())

        # Test 3: Not found
        results = path_parser.find_command_in_path("missing")
        self.assertEqual(results, [])

        # Test 4: Case-insensitive search (e.g. searching 'APP' should find 'app.exe')
        # Windows filesystem is case-insensitive.
        # Since tempfile directory structure is real filesystem, checking case-insensitivity works.
        results = path_parser.find_command_in_path("APP")
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].name.lower() == "app.exe")
        self.assertTrue(results[1].name.lower() == "app.bat")

    # Alternative test strategy: Mock Path object creation or behavior more directly

if __name__ == '__main__':
    unittest.main()
