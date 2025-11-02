from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# ---- Supabase config ----
SUPABASE_URL = "https://buenbdkodjrpzsfjsddu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ1ZW5iZGtvZGpycHpzZmpzZGR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwOTM3MjQsImV4cCI6MjA3NzY2OTcyNH0.8AOdXZtF3kaNnJ8dSEpEinD4RZM7GEy-nVtTV3o81B4"   # use anon/public key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def home():
    return "✅ Flask + Supabase on Render works!"

# CREATE user
@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.json
    res = supabase.table("users").insert({
        "name": data.get("name"),
        "username": data.get("username"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "ip_address": data.get("ip_address", "0.0.0.0"),
        "profile_photo": data.get("profile_photo", "https://buenbdkodjrpzsfjsddu.supabase.co/storage/v1/object/public/profiles/bg.png")
    }).execute()
    return jsonify(res.data)

# READ all users
@app.route("/users", methods=["GET"])
def get_users():
    res = supabase.table("users").select("*").execute()
    return jsonify(res.data)

# UPDATE user
@app.route("/update_user/<email>", methods=["PUT"])
def update_user(email):
    data = request.json
    res = supabase.table("users").update({
        "name": data.get("name"),
        "username": data.get("username"),
        "phone": data.get("phone"),
        "profile_photo": data.get("profile_photo")
    }).eq("email", email).execute()
    return jsonify(res.data)

# DELETE user
@app.route("/delete_user/<email>", methods=["DELETE"])
def delete_user(email):
    res = supabase.table("users").delete().eq("email", email).execute()
    return jsonify(res.data)

if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=5000, debug=True)
