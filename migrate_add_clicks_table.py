#!/usr/bin/env python3
"""
Migration: Add link_clicks table for detailed analytics
Run this on the cloud service to add click tracking
"""

from app import app, db
from sqlalchemy import text

def migrate():
    """Add link_clicks table"""
    with app.app_context():
        try:
            # Check if table already exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'link_clicks' not in tables:
                print("Creating link_clicks table...")
                
                # Create table
                db.session.execute(text('''
                    CREATE TABLE link_clicks (
                        id SERIAL PRIMARY KEY,
                        link_id INTEGER NOT NULL REFERENCES smart_links(id) ON DELETE CASCADE,
                        clicked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        device_type VARCHAR(20),
                        user_agent TEXT,
                        ip_address VARCHAR(45),
                        country VARCHAR(2),
                        redirected_to TEXT
                    )
                '''))
                
                # Create indexes
                db.session.execute(text('''
                    CREATE INDEX idx_link_clicks_link_id ON link_clicks(link_id)
                '''))
                
                db.session.execute(text('''
                    CREATE INDEX idx_link_clicks_clicked_at ON link_clicks(clicked_at)
                '''))
                
                db.session.commit()
                print("✅ Created link_clicks table with indexes")
            else:
                print("⏭️  link_clicks table already exists")
            
            print("\n✅ Migration completed successfully!")
            print("\nAnalytics features enabled:")
            print("  - Detailed click tracking")
            print("  - Device type detection")
            print("  - IP address logging")
            print("  - Click timeline")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRATION: Add Link Clicks Table")
    print("=" * 60)
    migrate()
