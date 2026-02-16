
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

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
    def test_get_system_path(self, mock_environ):
        # Mock PATH environment variable
        mock_environ.get.return_value = "C:\\Path1;C:\\Path2"
        
        # We also need to ensure os.pathsep is ';' which it is on Windows.
        # If running on non-windows, this test might need os.pathsep patched too if the code uses real os.pathsep.
        # The code uses `os.pathsep`. 
        with patch('os.pathsep', ';'):
            paths = path_parser.get_system_path()
            self.assertEqual(paths, ["C:\\Path1", "C:\\Path2"])

    @patch('os.environ')
    def test_get_system_path_empty(self, mock_environ):
        mock_environ.get.return_value = ""
        with patch('os.pathsep', ';'):
            paths = path_parser.get_system_path()
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
        
        self.assertEqual(result, ["C:\\SystemPath1", "C:\\SystemPath2"])
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
        
        self.assertEqual(result, ["C:\\UserPath1", "C:\\UserPath2"])
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

if __name__ == '__main__':
    unittest.main()
