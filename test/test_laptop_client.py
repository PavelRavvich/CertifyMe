import unittest
from unittest.mock import patch, MagicMock
import json

from conf import mqtt_push_topic
from laptop_client import push_client, on_message, screenshots


class TestOnMessage(unittest.TestCase):
    def setUp(self):
        self.userdata = None
        self.msg = MagicMock()
        self.client = MagicMock()
        push_client.publish = MagicMock()
        screenshots.clear()

    def test_on_message_save_screenshot(self):
        msg = MagicMock()
        msg.payload = json.dumps({"cmd": "save-screenshot"}).encode()

        with patch('laptop_client.make_screenshot') as mock_make_screenshot:
            mock_make_screenshot.return_value = "dummy_screenshot_data"
            on_message(self.client, self.userdata, msg)

            mock_make_screenshot.assert_called_once()

            self.assertIn("dummy_screenshot_data", screenshots)

            push_client.publish.assert_called_once_with(mqtt_push_topic, json.dumps({"status": "SCREEN_SAVED"}))

    def test_on_message_clear_screenshots(self):
        msg = MagicMock()
        msg.payload = json.dumps({"cmd": "clear-screenshots"}).encode()
        screenshots.append('data')

        on_message(self.client, self.userdata, msg)

        self.assertEqual(len(screenshots), 0)
        push_client.publish.assert_called_once_with(mqtt_push_topic, json.dumps({"status": "SCREEN_CLEAR"}))

    def test_on_message_send_to_ai(self):
        msg = MagicMock()
        msg.payload = json.dumps({"cmd": "send-to-ai"}).encode()
        screenshots.append('data')

        with patch('laptop_client.ai_complete', return_value="AI result") as mock_ai_complete:
            on_message(self.client, self.userdata, msg)

            self.assertTrue(mock_ai_complete.called)
            first_call_args = mock_ai_complete.call_args[0][0]
            self.assertEqual(first_call_args, ['data'])
            self.assertEqual(len(screenshots), 0)
            push_client.publish.assert_called_once_with(
                mqtt_push_topic, json.dumps({"status": "AI_COMPLETE", "answer": "AI result"})
            )

    def test_on_message_unknown_command(self):
        msg = MagicMock()
        msg.payload = json.dumps({"cmd": "unknown_command"}).encode()

        with patch('laptop_client.logging.warning') as mock_logging_warning, \
                patch('laptop_client.push_client.publish') as mock_publish:
            on_message(self.client, self.userdata, msg)

            mock_logging_warning.assert_called_once()
            args, kwargs = mock_logging_warning.call_args
            expected_log_message = "Unknown command: unknown_command"
            self.assertIn(expected_log_message, args[0])

            mock_publish.assert_called_once_with(
                mqtt_push_topic, json.dumps({"status": "UNKNOWN_CMD"})
            )


if __name__ == '__main__':
    unittest.main()
