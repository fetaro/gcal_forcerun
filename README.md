# Googleカレンダーのオンライン会議を強制的に始めるツール(gcal_forcerun)

**注意：このツールは古く、メンテナンスされていません。**

**Pythonのセットアップが不要な次期バージョンを (https://github.com/fetaro/gcal-run)[https://github.com/fetaro/gcal-run] に用意していますので、こちらをお使いください**

### 概要

Googleカレンダーに登録されたオンライン会議の開始前になったら、その会議のURLを起動する。
Google MeetとZoomとMicrosoft Temasに対応。

### 動作環境

* MacOS
* Python 3.9
* Google Chromeなどのブラウザ

### 使い方

#### クレデンシャルの配置

Googleカレンダーのクレデンシャルを`secret/credentials.json`に配置する。詳細は[こちら](https://developers.google.com/calendar/quickstart/python) 参照

#### ライブラリのインストール

```
poetry install
```

#### 定期的に実行する

MacOSのcrontabを用いて、定期的に実行する。

root権限でcrontabの編集
```bash
$ sudo crontab -e
```

例えば 15,30,45,0分開始の会議をターゲットにして、その1分前と2分前に本ツールを実行するように設定 する場合は、以下のように記載する

```
13,14,28,29,43,44,58,59 * * * * python /path/to/gcal_forcerun/main.py >> /tmp/gcal_forcerun.log 2>&1
```

これにより、13分起動のタイミングで15分開始の会議を強制開始できる。
何らかの理由により13分起動の処理が失敗しても、その後の14分起動の処理でリトライできる。

#### 注意

初回実行時はOAuth2のブラウザ認証が発生するため注意（２回目以降は `work/token.pickle` にトークンが保持されるため発生しない）
