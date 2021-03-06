#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import json
import algorithms.process_predictions as pp

app = Flask(__name__)

model = load_model("./models/nb_stream_fasttext_10k.h5")
with open("./models/tokenizer_stream_10k.json") as f:
    json_obj = json.load(f)
    tokenizer = tokenizer_from_json(json_obj)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods = ["POST","GET"])
def predict():
    vid = request.form["vid"]

    transcript, full_text, captionCount = pp.processVideo(vid)
    predictions = pp.getPredictions(model,tokenizer,full_text)

    sponsorTimestamps,sponsorText = pp.getTimestamps(transcript, captionCount, predictions, full_text.split(" "), 1)
    minuteStamps = []
    for t in sponsorTimestamps:
        m1,s1 = divmod(round(t[0]),60)
        m2,s2 = divmod(round(t[1]),60)
        minuteStamps.append(f"({m1}:{str(s1).zfill(2)},{m2}:{str(s2).zfill(2)})")

    return render_template("predict.html", videoid = vid, transcript_text = transcript,
                           timestamp = " ".join(str(e) for e in sponsorTimestamps),
                           minutestamp = " ".join(minuteStamps),
                           sponsTexts = sponsorText)

@app.route("/api/getSponsorSegments")
def getSponsorSegments():
    vid = request.args["vid"]
    transcript, full_text, captionCount = pp.processVideo(vid)
    predictions = pp.getPredictions(model,tokenizer,full_text)
    sponsorTimestamps = pp.getTimestamps(transcript, captionCount, predictions, full_text.split(" "))
    return jsonify(sponsorSegments=sponsorTimestamps)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
