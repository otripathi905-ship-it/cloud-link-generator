# Cloud Link Generator Service

Minimal standalone service for generating smart redirect links that work 24/7.

## Features

✅ Device-aware redirects (Android, iOS, Windows, macOS, Linux)
✅ Click tracking
✅ Simple REST API
✅ SQLite (local) or PostgreSQL (production)
✅ Deploy to any cloud platform
✅ Free tier compatible

## API Endpoints

### 1. Create Link
```http
POST /api/create
Content-Type: application/json

{
  "name": "My App Download",
  "android_url": "https://play.google.com/store/apps/...",
  "ios_url": "https://apps.apple.com/app/...",
  "fallback_url": "https://example.com"
}
```

**Response:**
```json
{
  "success": true,
  "token": "abc123xyz",
  "url": "https://yourservice.com/l/abc123xyz"
}
```

### 2. Redirect
```http
GET /l/<token>
```

Automatically redirects based on device OS.

### 3. Get Stats
```http
GET /api/stats/<token>
```

**Response:**
```json
{
  "success": true,
  "token": "abc123xyz",
  "click_count": 42,
  "created_at": "2026-02-09T..."
}
```

## Deployment Options

### Option 1: Render.com (Recommended - Easiest)

1. Create account at https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo or upload files
4. Settings:
   - **Name**: link-generator
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free
5. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: (Render provides PostgreSQL for free)
6. Deploy!

**Your URL**: `https://link-generator-xyz.onrender.com`

### Option 2: Railway.app

1. Create account at https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select this folder
4. Railway auto-detects Python and deploys
5. Get your URL from dashboard

### Option 3: Fly.io

1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Run:
```bash
cd cloud_link_generator
fly launch
fly deploy
```

### Option 4: PythonAnywhere (Free Tier)

1. Create account at https://www.pythonanywhere.com
2. Upload files
3. Create web app with Flask
4. Configure WSGI file
5. Reload web app

## Local Testing

```bash
cd cloud_link_generator
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000

## Integration with Your Mailer

Add this to your local mailer's `config.py`:

```python
# Cloud Link Generator API
LINK_GENERATOR_URL = 'https://your-service.onrender.com'
```

Create a helper function in your mailer:

```python
import requests

def create_smart_link(name, android_url, ios_url, fallback_url):
    """Call cloud service to create smart link"""
    response = requests.post(
        f"{LINK_GENERATOR_URL}/api/create",
        json={
            'name': name,
            'android_url': android_url,
            'ios_url': ios_url,
            'fallback_url': fallback_url
        }
    )
    data = response.json()
    if data['success']:
        return data['url']  # https://your-service.com/l/abc123
    else:
        raise Exception(data['error'])
```

## Usage Example

```python
# In your local mailer
link = create_smart_link(
    name='App Download',
    android_url='https://play.google.com/...',
    ios_url='https://apps.apple.com/...',
    fallback_url='https://example.com'
)

# Use in email
email_html = f'<a href="{link}">Download App</a>'
```

## Benefits

✅ **Mailer runs locally** - No deployment needed
✅ **Links work 24/7** - Even when your computer is off
✅ **Free hosting** - Use free tier services
✅ **Simple API** - Just HTTP requests
✅ **Device detection** - Automatic OS-based redirects

## Security Notes

- No authentication required (public API)
- Rate limiting recommended for production
- Consider adding API key for private use
- Links are permanent (no expiration)

## Troubleshooting

### Link returns 404
- Check token is correct
- Verify link was created successfully
- Check service is running

### Wrong redirect
- Check User-Agent detection
- Verify OS-specific URLs are set
- Test fallback_url

### Service not responding
- Check deployment logs
- Verify environment variables
- Test health endpoint: `/health`

## Cost

**Free tier limits:**
- Render: 750 hours/month (enough for 24/7)
- Railway: $5 credit/month
- Fly.io: 3 VMs free
- PythonAnywhere: 1 web app free

**Recommended**: Render.com (easiest + most reliable free tier)

## Next Steps

1. Deploy to Render.com (5 minutes)
2. Get your service URL
3. Update your mailer's config
4. Create smart links via API
5. Use links in emails!
