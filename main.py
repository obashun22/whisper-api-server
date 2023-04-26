import whisper
from flask import Flask, request
from flask_cors import CORS

model = whisper.load_model("large")


def create_textfile(filename, sr, timelag):
    results = model.transcribe(
        filename, verbose=False, language="ja", segment_length_ratio=float(sr)
    )
    output_file = "transcribe.srt"
    with open(output_file, mode="w") as f:
        for index, _dict in enumerate(results["segments"]):
            start_time = _dict["start"]
            end_time = _dict["end"]
            start_time += timelag
            end_time += timelag
            s_h, s_m = divmod(start_time, 3600)
            s_m, s_s = divmod(s_m, 60)
            e_h, e_m = divmod(end_time, 3600)
            e_m, e_s = divmod(e_m, 60)
            f.write(
                f'{index+1}\n{s_h:02}:{s_m:02}:{s_s:02},000 --> {e_h:02}:{e_m:02}:{e_s:02},000\n{_dict["text"]}\n\n'
            )
    return output_file


app = Flask(__name__)
CORS(app)


@app.route("/")
def root():
    return "Hello Whisper!!"


@app.route("/whisper/transcribe", methods=["POST"])
def whisper_transcribe():
    input_file = request.files["file"]
    segment_length = 1
    timelag = 0
    output = create_textfile(filename=input_file, sr=segment_length, timelag=timelag)
    with open(output, "r") as file:
        contents = file.read()
        return contents


# app.run(port=4000, debug=True)
