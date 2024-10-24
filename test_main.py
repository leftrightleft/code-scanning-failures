import unittest
from unittest.mock import patch, MagicMock
import main

class TestMain(unittest.TestCase):

    @patch('main.make_request')
    def test_get_rate_limit_reset_time(self, mock_make_request):
        # Mock the response for the HEAD request
        mock_response = MagicMock()
        mock_response.headers = {
            "X-Ratelimit-Remaining": "10",
            "X-Ratelimit-Reset": "1633024800"
        }
        mock_make_request.return_value = mock_response

        remaining, reset = main.get_rate_limit_reset_time("test/repo")
        self.assertEqual(remaining, 10)
        self.assertEqual(reset, 1633024800)

        # Test for missing headers
        mock_response.headers = {}
        with self.assertRaises(RuntimeError):
            main.get_rate_limit_reset_time("test/repo")

    @patch('main.make_request')
    def test_get_repos(self, mock_make_request):
        # Mock the response for the GET request
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"full_name": "test/repo1"},
            {"full_name": "test/repo2"}
        ]
        mock_response.links = {}
        mock_make_request.return_value = mock_response

        repos = main.get_repos("test_org")
        self.assertEqual(repos, ["test/repo1", "test/repo2"])

        # Test for non-200 status code
        mock_response.status_code = 500
        with self.assertRaises(RuntimeError):
            main.get_repos("test_org")

    @patch('main.make_request')
    def test_get_analyses(self, mock_make_request):
        # Mock the response for the GET request
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"analysis_key": "key1", "error": "error1"},
            {"analysis_key": "key2", "error": ""}
        ]
        mock_response.links = {}
        mock_make_request.return_value = mock_response

        analyses = main.get_analyses("test/repo")
        self.assertEqual(len(analyses), 2)
        self.assertEqual(analyses[0]["analysis_key"], "key1")
        self.assertEqual(analyses[1]["analysis_key"], "key2")

        # Test for 404 status code
        mock_response.status_code = 404
        analyses = main.get_analyses("test/repo")
        self.assertEqual(analyses, [])

        # Test for 403 status code with specific error message
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "message": "Advanced Security must be enabled for this repository to use code scanning."
        }
        analyses = main.get_analyses("test/repo")
        self.assertEqual(analyses, [])

        # Test for non-200 status code
        mock_response.status_code = 500
        with self.assertRaises(RuntimeError):
            main.get_analyses("test/repo")

if __name__ == '__main__':
    unittest.main()