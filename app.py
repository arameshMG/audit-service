from flask import Flask, request, jsonify
from db import init_db, log_event, query_events
from notification_client import send_alert

app = Flask(__name__)
init_db()

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()

    if not data or "eventType" not in data or "status" not in data:
        return jsonify({"error": "eventType and status are required"}), 400

    try:
        event_id = log_event(
            event_type=data["eventType"],
            user_identifier=data.get("userIdentifier"),
            status=data["status"],
            details=data.get("details"),
            source_service=data.get("sourceService")
        )
        return jsonify({"status": "logged", "eventId": event_id}), 201
    except Exception as e:
        send_alert(f"Audit service failed to log an event: {str(e)}")
        return jsonify({"error": "Internal error logging event"}), 500

@app.route("/events", methods=["GET"])
def get_events():
    user_identifier = request.args.get("user")
    event_type = request.args.get("type")
    status = request.args.get("status")
    limit = int(request.args.get("limit", 100))

    try:
        results = query_events(
            user_identifier=user_identifier,
            event_type=event_type,
            status=status,
            limit=limit
        )
        return jsonify({"count": len(results), "events": results})
    except Exception as e:
        send_alert(f"Audit service failed to query events: {str(e)}")
        return jsonify({"error": "Internal error querying events"}), 500

if __name__ == "__main__":
    app.run(debug=True)
