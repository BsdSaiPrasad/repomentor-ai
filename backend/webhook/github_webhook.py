from flask import Flask, request, jsonify
import hmac
import hashlib
import os
import threading
from dotenv import load_dotenv
from backend.services.repo_analyzer import analyze_repo

load_dotenv()

app = Flask(__name__)

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "repomentor_secret")


def verify_signature(payload: bytes, signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def run_review_in_background(clone_url: str, pusher: str, repo_name: str):
    try:
        print(f"[Webhook] Starting review for {repo_name} by {pusher}")
        report = analyze_repo(clone_url)
        print(f"[Webhook] Done — {repo_name} scored {report['overall_score']} ({report['grade']})")
    except Exception as e:
        print(f"[Webhook] Review failed for {repo_name}: {e}")


@app.route("/webhook/github", methods=["POST"])
def github_webhook():
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 401

    event = request.headers.get("X-GitHub-Event", "")

    if event != "push":
        return jsonify({"status": "ignored", "event": event}), 200

    payload = request.json
    clone_url = payload["repository"]["clone_url"]
    pusher = payload["pusher"]["name"]
    repo_name = payload["repository"]["full_name"]
    branch = payload.get("ref", "").replace("refs/heads/", "")

    print(f"[Webhook] Push received — {pusher} pushed to {repo_name} ({branch})")

    thread = threading.Thread(
        target=run_review_in_background,
        args=(clone_url, pusher, repo_name)
    )
    thread.start()

    return jsonify({
        "status": "review started",
        "repo": repo_name,
        "pusher": pusher,
        "branch": branch
    }), 202


@app.route("/webhook/health", methods=["GET"])
def health():
    return jsonify({"status": "webhook server running"}), 200


if __name__ == "__main__":
    app.run(port=5001, debug=True)
