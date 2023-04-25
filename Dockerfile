# ベースイメージの指定
FROM python:3.10

# ワーキングディレクトリを指定
WORKDIR /app

# ローカルのrequirements.txtをコンテナにコピー
COPY requirements.txt requirements.txt

# パッケージのインストール
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/obashun22/whisper

# requirements.txtを削除
RUN rm requirements.txt

# コンテナ起動時にflaskサーバを立ち上げるコマンドを実行するコマンド
CMD ["gunicorn", "--bind", ":8080", "--workers", "3", "main:app"]