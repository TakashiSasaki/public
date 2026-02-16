import unittest
import sys
import os

# Only import windows-specific modules if on Windows to avoid ImportErrors during collection on non-Windows
if sys.platform == 'win32':
    try:
        from get_a_grip.core.event_log import EventLogCore
    except ImportError:
        EventLogCore = None
else:
    EventLogCore = None

@unittest.skipUnless(sys.platform == 'win32', "Windows environments only")
class TestEventLogCore(unittest.TestCase):
    """
    Tests for EventLogCore functionality.
    These tests interact with the actual Windows Event Log, so they are integration tests
    that require a Windows environment.
    """

    def setUp(self):
        if EventLogCore is None:
            self.skipTest("EventLogCore could not be imported (pywin32 might be missing)")

    def test_fetch_system_logs(self):
        """
        Verify that we can fetch logs from the 'System' channel.
        """
        # Fetch a small number of logs
        limit = 5
        logs = EventLogCore.fetch_logs(log_name="System", limit=limit)
        
        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0, "Should fetch at least one log if System log is not empty")
        self.assertLessEqual(len(logs), limit)
        
        # Verify structure of the first log
        first_log = logs[0]
        self.assertIn("record_number", first_log)
        self.assertIn("event_id", first_log)
        self.assertIn("event_type", first_log)
        self.assertIn("source_name", first_log)
        self.assertIn("time_generated", first_log)
        self.assertIn("message", first_log)

    def test_get_available_logs(self):
        """
        Verify that we can list available event logs.
        """
        logs = EventLogCore.get_available_logs()
        self.assertIsInstance(logs, list)
        self.assertIn("System", logs)
        self.assertIn("Application", logs)
        self.assertIn("Security", logs)

    def test_get_event_type_str(self):
        """
        Verify event type string conversion.
        """
        # We need win32con constants, but we can't import them if not on windows or pywin32 missing.
        # We can test known values if we hardcode them, or just skip strict value checking 
        # and check return type is string.
        
        # 1 = Error (usually), 4 = Info, etc. matching implementation
        # win32con.EVENTLOG_ERROR_TYPE is 1
        # win32con.EVENTLOG_INFORMATION_TYPE is 4
        
        error_str = EventLogCore.get_event_type_str(1)
        self.assertEqual(error_str, "ERROR")
        
        info_str = EventLogCore.get_event_type_str(4)
        self.assertEqual(info_str, "INFORMATION")
        
        unknown_str = EventLogCore.get_event_type_str(99999)
        self.assertTrue(unknown_str.startswith("Unknown"))

if __name__ == '__main__':
    unittest.main()
