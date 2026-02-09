#!/usr/bin/env python3
"""
Cloud Link Generator Service
Minimal standalone service for generating and handling smart redirect links
Deploy this to any free cloud service (Render, Railway, Fly.io, etc.)
"""

from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///links.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Fix for Heroku postgres URL
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

db = SQLAlchemy(app)


# Database Models
class SmartLink(db.Model):
    __tablename__ = 'smart_links'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200))
    
    # OS-specific URLs
    android_url = db.Column(db.Text)
    ios_url = db.Column(db.Text)
    windows_url = db.Column(db.Text)
    macos_url = db.Column(db.Text)
    linux_url = db.Column(db.Text)
    fallback_url = db.Column(db.Text, nullable=False)
    
    # Stats
    click_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_clicked_at = db.Column(db.DateTime)
    
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to clicks
    clicks = db.relationship('LinkClick', backref='link', lazy='dynamic', cascade='all, delete-orphan')


class LinkClick(db.Model):
    __tablename__ = 'link_clicks'
    
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('smart_links.id'), nullable=False, index=True)
    
    # Click details
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    device_type = db.Column(db.String(20))  # android, ios, windows, macos, linux, other
    user_agent = db.Column(db.Text)
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    country = db.Column(db.String(2))  # Country code (optional)
    
    # Redirect info
    redirected_to = db.Column(db.Text)  # Which URL was used
    
    def __repr__(self):
        return f'<LinkClick {self.id} - {self.device_type} at {self.clicked_at}>'


# Create tables
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    """Home page with API documentation"""
    return jsonify({
        'service': 'Cloud Link Generator',
        'version': '1.0',
        'endpoints': {
            'create_link': 'POST /api/create',
            'redirect': 'GET /l/<token>',
            'stats': 'GET /api/stats/<token>',
            'health': 'GET /health'
        },
        'status': 'online'
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/create', methods=['POST'])
def create_link():
    """
    Create a new smart link
    
    Request body:
    {
        "name": "My App Download",
        "android_url": "https://play.google.com/...",
        "ios_url": "https://apps.apple.com/...",
        "windows_url": "https://example.com",
        "macos_url": "https://example.com",
        "linux_url": "https://example.com",
        "fallback_url": "https://example.com"
    }
    
    Returns:
    {
        "success": true,
        "token": "abc123xyz",
        "url": "https://yourservice.com/l/abc123xyz"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'fallback_url' not in data:
            return jsonify({'success': False, 'error': 'fallback_url is required'}), 400
        
        # Generate unique token
        token = secrets.token_urlsafe(12)
        
        # Create smart link
        link = SmartLink(
            token=token,
            name=data.get('name', 'Unnamed Link'),
            android_url=data.get('android_url'),
            ios_url=data.get('ios_url'),
            windows_url=data.get('windows_url'),
            macos_url=data.get('macos_url'),
            linux_url=data.get('linux_url'),
            fallback_url=data['fallback_url']
        )
        
        db.session.add(link)
        db.session.commit()
        
        # Generate full URL
        base_url = request.host_url.rstrip('/')
        full_url = f"{base_url}/l/{token}"
        
        return jsonify({
            'success': True,
            'token': token,
            'url': full_url,
            'created_at': link.created_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/l/<token>')
def redirect_link(token):
    """
    Smart redirect based on device OS
    
    Detects user's operating system and redirects to appropriate URL
    """
    try:
        # Find link by token
        link = SmartLink.query.filter_by(token=token, is_active=True).first()
        
        if not link:
            return "Link not found", 404
        
        # Get user agent and IP
        user_agent = request.headers.get('User-Agent', '').lower()
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # Detect OS/Device
        device_type = 'other'
        redirect_url = None
        
        if 'android' in user_agent:
            device_type = 'android'
            redirect_url = link.android_url
        elif any(x in user_agent for x in ['iphone', 'ipad', 'ipod']):
            device_type = 'ios'
            redirect_url = link.ios_url
        elif 'windows' in user_agent:
            device_type = 'windows'
            redirect_url = link.windows_url
        elif 'macintosh' in user_agent or 'mac os' in user_agent:
            device_type = 'macos'
            redirect_url = link.macos_url
        elif 'linux' in user_agent:
            device_type = 'linux'
            redirect_url = link.linux_url
        
        # Use fallback if no OS-specific URL
        if not redirect_url:
            redirect_url = link.fallback_url
        
        # Record detailed click
        click = LinkClick(
            link_id=link.id,
            device_type=device_type,
            user_agent=request.headers.get('User-Agent', ''),
            ip_address=ip_address,
            redirected_to=redirect_url
        )
        db.session.add(click)
        
        # Update link stats
        link.click_count += 1
        link.last_clicked_at = datetime.utcnow()
        db.session.commit()
        
        # Redirect
        return redirect(redirect_url, code=302)
        
    except Exception as e:
        print(f"Error in redirect: {e}")
        db.session.rollback()
        return "Error processing link", 500


@app.route('/api/stats/<token>')
def get_stats(token):
    """
    Get statistics for a smart link
    
    Returns click count and other metrics
    """
    try:
        link = SmartLink.query.filter_by(token=token).first()
        
        if not link:
            return jsonify({'success': False, 'error': 'Link not found'}), 404
        
        return jsonify({
            'success': True,
            'token': token,
            'name': link.name,
            'click_count': link.click_count,
            'created_at': link.created_at.isoformat(),
            'last_clicked_at': link.last_clicked_at.isoformat() if link.last_clicked_at else None,
            'is_active': link.is_active
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analytics/<token>')
def get_analytics(token):
    """
    Get detailed analytics for a smart link
    
    Returns:
        - Total clicks
        - Clicks by device type
        - Recent clicks with details
        - Click timeline
    """
    try:
        link = SmartLink.query.filter_by(token=token).first()
        
        if not link:
            return jsonify({'success': False, 'error': 'Link not found'}), 404
        
        # Get all clicks
        clicks = LinkClick.query.filter_by(link_id=link.id).order_by(LinkClick.clicked_at.desc()).all()
        
        # Count by device type
        device_counts = {}
        for click in clicks:
            device = click.device_type or 'other'
            device_counts[device] = device_counts.get(device, 0) + 1
        
        # Recent clicks (last 50)
        recent_clicks = []
        for click in clicks[:50]:
            recent_clicks.append({
                'id': click.id,
                'device_type': click.device_type,
                'clicked_at': click.clicked_at.isoformat(),
                'ip_address': click.ip_address,
                'redirected_to': click.redirected_to
            })
        
        # Click timeline (group by date)
        from collections import defaultdict
        timeline = defaultdict(int)
        for click in clicks:
            date_key = click.clicked_at.strftime('%Y-%m-%d')
            timeline[date_key] += 1
        
        # Convert timeline to sorted list
        timeline_data = [{'date': k, 'clicks': v} for k, v in sorted(timeline.items())]
        
        return jsonify({
            'success': True,
            'token': token,
            'name': link.name,
            'total_clicks': link.click_count,
            'device_breakdown': device_counts,
            'recent_clicks': recent_clicks,
            'timeline': timeline_data,
            'created_at': link.created_at.isoformat(),
            'last_clicked_at': link.last_clicked_at.isoformat() if link.last_clicked_at else None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
