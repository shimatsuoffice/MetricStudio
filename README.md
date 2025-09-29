README.md（英語版・審査員用）
# Creator Review Tool

This project is a **minimal FastAPI demo app** prepared for Meta App Review.  
It demonstrates how a creator can log in via **Facebook Login** and view their own profile and insights.

##  Features
- Login with Facebook/Instagram
- Fetch basic profile information
- Fetch media insights (likes, comments, engagement)

##  How to run locally

### 1. Clone repository
```bash
git clone https://github.com/your-username/Creator_Review_Tool.git
cd Creator_Review_Tool

2. Create virtual environment
python -m venv venv
source venv/bin/activate   # on macOS/Linux
venv\Scripts\activate      # on Windows

3. Install dependencies
pip install -r requirements.txt

4. Environment variables

Create a .env file based on .env.example:

APP_ID=your_app_id
APP_SECRET=your_app_secret
REDIRECT_URI=https://review.kaitekilife2.com/callback

5. Run app
uvicorn app:app --host 0.0.0.0 --port 8000


Access: http://localhost:8000

Deployed test environment

The app is deployed on Render:

 https://review.kaitekilife2.com

Testing instructions for reviewers

Go to the deployed URL above.

Click Login with Facebook.

Approve requested permissions.

You will see your profile and insights.

Contact

For any questions during the review, please contact:
support@kaitekilife2.com

