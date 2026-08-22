import time
import requests

def poll_job(status_url: str, headers: dict, result_key: str = "status",
             done_values=("completed", "COMPLETED"), interval=3, timeout=180):
    """Poll a job status endpoint until it's done or times out."""
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(status_url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if data.get(result_key) in done_values:
            return data
        time.sleep(interval)
    raise TimeoutError(f"Job at {status_url} did not complete in {timeout}s")