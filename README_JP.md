# MetricStudio

このプロジェクトは、**Meta App Review（審査）用の最小構成デモアプリ**です。  
Facebookログインを利用して、クリエイター自身のプロフィールやインサイトを表示できます。

## 機能
- Facebook/Instagram ログイン
- 基本プロフィール情報の取得
- メディアのインサイト（リーチ・インプレッションなど）の取得

## ローカル実行手順

### 1. リポジトリの取得
```bash
git clone https://github.com/your-username/MetricStudio.git
cd MetricStudio
2. 仮想環境の作成
bash
コードをコピーする
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
3. 依存パッケージのインストール
bash
コードをコピーする
pip install -r requirements.txt
4. 環境変数ファイルの設定
.env.example をコピーして .env を作成してください。

ini
コードをコピーする
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
REDIRECT_URI=https://metricstudio.kaitekilife2.com/auth/callback
5. アプリの起動
bash
コードをコピーする
uvicorn app_submit:app --host 0.0.0.0 --port 8000
ブラウザでアクセス: http://localhost:8000

デプロイ環境
Render 上にデプロイされています：

👉 https://metricstudio.kaitekilife2.com

審査員の方へのテスト手順
上記URLへアクセスしてください。

Facebookでログイン をクリック。

権限を承認してください。

プロフィールとインサイトが表示されます。

## Deployment (Render)

### 環境変数設定
- META_APP_ID
- META_APP_SECRET
- APP_SECRET
- REDIRECT_URI
- ALLOWED_ORIGINS

### Start Command
```bash
uvicorn app_submit:app --host 0.0.0.0 --port $PORT


連絡先
審査に関する質問は以下にご連絡ください：
📧 info2@kaitekilife2.com
