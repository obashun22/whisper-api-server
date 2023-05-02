from http import HTTPStatus
import whisper
import os
from flask import Flask, request, send_from_directory
from flask_cors import CORS
import threading

model = whisper.load_model("large")

UPLOAD_DIR = "/uploads"
SRT_DIR = "/srt"


def create_textfile(filename, sr, timelag):
    results = model.transcribe(
        filename,
        verbose=False,
        language="ja",
        segment_length_ratio=float(sr),
        fp16=False,
    )
    output_file = "transcribe.srt"
    output_file = os.path.join(SRT_DIR, output_file)
    if not os.path.exists(SRT_DIR):  # ディレクトリがなければ作成
        os.makedirs(SRT_DIR)
    else:
        if os.path.exists(output_file):  # srtファイルがあれば削除
            os.remove(output_file)
    with open(output_file, mode="w") as f:
        for index, _dict in enumerate(results["segments"]):
            start_time = _dict["start"]
            end_time = _dict["end"]
            start_time += timelag
            end_time += timelag
            s_h, s_m = divmod(start_time, 3600)
            s_m, s_sms = divmod(s_m, 60)
            e_h, e_m = divmod(end_time, 3600)
            e_m, e_sms = divmod(e_m, 60)
            s_h, e_h = int(s_h), int(e_h)  # 時
            s_m, e_m = int(s_m), int(e_m)  # 分
            s_s, e_s = int(s_sms), int(e_sms)  # 秒
            s_ms, e_ms = int((s_sms - s_s) * 1000), int((e_sms - e_s) * 1000)  # ミリ秒
            f.write(
                f'{index+1}\n{s_h:02}:{s_m:02}:{s_s:02},{s_ms:03} --> {e_h:02}:{e_m:02}:{e_s:02},{e_ms:03}\n{_dict["text"]}\n\n'
            )
    return output_file


app = Flask(__name__, static_folder="build", static_url_path="/")
CORS(app)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/whisper/transcribe", methods=["POST"])
def whisper_transcribe():
    input_file = request.files["file"]
    file_path = os.path.join(UPLOAD_DIR, input_file.filename)  # 保存先のパス
    input_file.save(file_path)  # 入力音声を保存

    segment_length = 1  # 字幕を切り出す長さ
    timelag = 0  # タイムコードのオフセット
    subthread = threading.Thread(
        target=create_textfile,
        kargs={"filename": file_path, "sr": segment_length, "timelag": timelag},
    )
    subthread.start()
    return HTTPStatus.OK


@app.route("/whisper/download", methods=["GET"])
def whisper_download():
    output_file = "transcribe.srt"
    output_file = os.path.join(SRT_DIR, output_file)
    if os.path.exists(output_file):
        with open(output_file, "r") as file:
            contents = file.read()
            return contents
    else:
        return HTTPStatus.NOT_FOUND
