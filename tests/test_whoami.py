import sys
import unittest
from unittest.mock import MagicMock, patch
from get_a_grip.core import whoami

class TestWhoami(unittest.TestCase):
    def setUp(self):
        # We need to reload or re-setup mocks because whoami has top-level logic
        pass

    def test_get_user_principal_name_success(self):
        # Patch sys.platform and ctypes in the whoami module
        with patch('get_a_grip.core.whoami.sys.platform', 'win32'), \
             patch('get_a_grip.core.whoami.ctypes') as mock_ctypes:
            
            # Setup wintypes/ULONG mock
            mock_ulong = MagicMock()
            mock_ctypes.wintypes.ULONG.return_value = mock_ulong
            
            # Setup GetUserNameExW mock
            mock_windll = MagicMock()
            mock_ctypes.windll = mock_windll
            mock_windll.secur32.GetUserNameExW.return_value = 1
            
            # Setup buffer mock
            mock_buffer = MagicMock()
            mock_buffer.value = "test-user@example.com"
            mock_ctypes.create_unicode_buffer.return_value = mock_buffer
            
            result = whoami.get_user_principal_name()
            
            self.assertEqual(result, "test-user@example.com")
            mock_windll.secur32.GetUserNameExW.assert_called_once()

    def test_get_user_principal_name_failure_return_zero(self):
        with patch('get_a_grip.core.whoami.sys.platform', 'win32'), \
             patch('get_a_grip.core.whoami.ctypes') as mock_ctypes:
            
            mock_ctypes.windll.secur32.GetUserNameExW.return_value = 0
            
            result = whoami.get_user_principal_name()
            self.assertIsNone(result)

    def test_get_user_principal_name_exception_swallowed(self):
        with patch('get_a_grip.core.whoami.sys.platform', 'win32'), \
             patch('get_a_grip.core.whoami.ctypes') as mock_ctypes:
            
            mock_ctypes.windll.secur32.GetUserNameExW.side_effect = Exception("API Error")
            
            # This should not raise an exception because we hit the 'except Exception: pass'
            result = whoami.get_user_principal_name()
            self.assertIsNone(result)

    def test_get_user_principal_name_on_linux(self):
        with patch('get_a_grip.core.whoami.sys.platform', 'linux'):
            result = whoami.get_user_principal_name()
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()

