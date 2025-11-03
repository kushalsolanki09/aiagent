import os
from urllib.parse import quote_plus
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient, errors
import certifi

app = Flask(__name__)


MONGO_USER = os.environ.get("MONGO_USER", "Kushalsolanki")
MONGO_PWD_RAW = os.environ.get("MONGO_PWD", "Kushal@09")  
MONGO_PWD = quote_plus(MONGO_PWD_RAW)
MONGO_HOST = os.environ.get("MONGO_HOST", "cluster0.9p0bofy.mongodb.net")
MONGO_DB = os.environ.get("MONGO_DB", "mobagent")

MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PWD}@{MONGO_HOST}/{MONGO_DB}?retryWrites=true&w=majority"


db = None
try:
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
    client.admin.command("ping") 
    db = client[MONGO_DB]
    app.logger.info("Connected to MongoDB")
except errors.PyMongoError as e:
    app.logger.exception("MongoDB connection failed: %s", e)


@app.route("/")
def home():
    if not db:
        return render_template("index.html", chats=[], error="DB connection failed")
    try:
        cursor = db.chats.find().limit(100)
        mychats = []
        for chat in cursor:
            if "_id" in chat:
                chat["_id"] = str(chat["_id"])
            mychats.append(chat)
        return render_template("index.html", chats=mychats)
    except errors.PyMongoError as e:
        app.logger.exception("Mongo query failed")
        return render_template("index.html", chats=[], error=str(e))

@app.route("/api", methods=["GET", "POST"])
def qa():
    if request.method == "POST":
        payload = request.get_json(force=True, silent=True) or {}
        question = payload.get("question", "")
        app.logger.debug("Received question: %s", question)
        
        return jsonify({"result": f"answer of {question}"})
    return jsonify({"result": "thank you! Send a POST request with a question."})

if __name__ == "__main__":
    app.run(debug=True)
