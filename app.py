from flask import Flask, request, jsonify
from db import init_db, log_event, query_events

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

    event_id = log_event(
        event_type=data["eventType"],
        user_identifier=data.get("userIdentifier"),
        status=data["status"],
        details=data.get("details"),
        source_service=data.get("sourceService")
    )

    return jsonify({"status": "logged", "eventId": event_id}), 201


@app.route("/events", methods=["GET"])
def get_events():
    user_identifier = request.args.get("user")
    event_type = request.args.get("type")
    status = request.args.get("status")
    limit = int(request.args.get("limit", 100))

    results = query_events(
        user_identifier=user_identifier,
        event_type=event_type,
        status=status,
        limit=limit
    )

    return jsonify({"count": len(results), "events": results})


if __name__ == "__main__":
    app.run(debug=True)
