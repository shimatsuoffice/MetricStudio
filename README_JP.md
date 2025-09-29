#  `README_JP.md`（日本語版・社内用）

```markdown
# クリエイター レビュー ツール

このプロジェクトは **Meta アプリ審査用の最小 FastAPI デモアプリ** です。  
クリエイターが **Facebookログイン** を通じて、自分のプロフィールやインサイトを閲覧できる流れを確認できます。

##  機能
- Facebook/Instagramでのログイン
- プロフィール情報の取得
- 投稿インサイト（いいね数、コメント数、エンゲージメント）の取得

##  ローカルでの実行方法

### 1. リポジトリをクローン
```bash
git clone https://github.com/your-username/Creator_Review_Tool.git
cd Creator_Review_Tool
2. 仮想環境の作成
bash
コードをコピーする
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
3. 依存関係をインストール
bash
コードをコピーする
pip install -r requirements.txt
4. 環境変数
.env.example をコピーして .env を作成します:

ini
コードをコピーする
APP_ID=あなたのAppID
APP_SECRET=あなたのAppSecret
REDIRECT_URI=https://review.kaitekilife2.com/callback
5. アプリを起動
bash
コードをコピーする
uvicorn app:app --host 0.0.0.0 --port 8000
アクセス: http://localhost:8000

デプロイ済みテスト環境
Renderにデプロイ済みです：

 https://review.kaitekilife2.com

審査員向けテスト手順
上記URLにアクセス

Facebookでログイン をクリック

権限を承認

プロフィールとインサイトが表示されます

問い合わせ先
審査中の連絡先:
support@kaitekilife2.com
