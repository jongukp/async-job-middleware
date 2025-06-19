import unittest
from unittest.mock import AsyncMock, patch

from app.main import app, job_results, start_async_job
from starlette.testclient import TestClient


class AppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        job_results.clear()

    def test_proxy_success(self):
        response = self.client.post("/proxy",
                                    json={"account": "test@example.com"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["state"], "running")
        self.assertIn("id", data)

    def test_proxy_missing_account(self):
        response = self.client.post("/proxy", json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Account is required"})

    def test_callback(self):
        job_id = "test-job"
        payload = {"result": "ok"}
        response = self.client.post(f"/callback/{job_id}", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})
        self.assertEqual(job_results[job_id], payload)

    def test_status_pending(self):
        job_id = "nonexistent-job-id"
        response = self.client.get(f"/status/{job_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"state": "pending"})

    def test_status_completed(self):
        job_id = "completed-job"
        job_results[job_id] = {"result": "done"}
        response = self.client.get(f"/status/{job_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": "done"})


class StartAsyncJobTestCase(unittest.IsolatedAsyncioTestCase):

    @patch("app.main.asyncio.create_subprocess_exec")
    async def test_start_async_job_prints_output(self, mock_subproc_exec):
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"stdout", b"stderr")
        mock_subproc_exec.return_value = mock_process

        with patch("builtins.print") as mock_print:
            await start_async_job("test@example.com",
                                  "http://localhost:8000/callback/test")
            mock_print.assert_any_call("stdout")
            mock_print.assert_any_call("stderr")
