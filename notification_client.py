import requests
import os

NOTIFICATION_SERVICE_URL = os.environ.get("NOTIFICATION_SERVICE_URL", "https://notification-service-k0vg.onrender.com")
NOTIFICATION_API_KEY = os.environ.get("NOTIFICATION_API_KEY")
ALERT_ISSUE_KEY = os.environ.get("ALERT_ISSUE_KEY", "IDTP-108")


def send_alert(message):
    """
    Alerts via the notification service when something goes wrong inside
    the audit service itself. Never raises - a failed alert should never
    crash the thing that's already failing.
    """
    try:
        requests.post(
            f"{NOTIFICATION_SERVICE_URL}/notify",
            json={"issueKey": ALERT_ISSUE_KEY, "message": message},
            headers={"X-Api-Key": NOTIFICATION_API_KEY},
            timeout=5
        )
    except Exception as e:
        print(f"Failed to send alert (non-fatal): {e}")
