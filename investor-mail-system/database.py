"""
Investor Mail System - Database Operations
SQLite database for storing investors, templates, and sent mails

Developed by: emirgunyy & gktrk363
"""
import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH, DATA_DIR

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def get_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Investors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            company TEXT,
            category TEXT DEFAULT 'GENEL',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Templates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            category TEXT DEFAULT 'GENEL',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sent mails table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_mails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investor_id INTEGER,
            template_id INTEGER,
            subject TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'sent',
            error_message TEXT,
            FOREIGN KEY (investor_id) REFERENCES investors (id),
            FOREIGN KEY (template_id) REFERENCES templates (id)
        )
    ''')
    
    # Scheduled mails table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_mails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investor_id INTEGER,
            template_id INTEGER,
            subject TEXT,
            body TEXT,
            scheduled_time TIMESTAMP,
            status TEXT DEFAULT 'pending', -- pending, sent, failed, cancelled
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (investor_id) REFERENCES investors (id),
            FOREIGN KEY (template_id) REFERENCES templates (id)
        )
    ''')
    
    # Interactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investor_id INTEGER,
            type TEXT NOT NULL,  -- 'mail', 'linkedin', 'meeting', 'note'
            content TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (investor_id) REFERENCES investors (id)
        )
    ''')
    
    # Unsubscribes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unsubscribes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            reason TEXT,
            unsubscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Audit Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            performed_by TEXT DEFAULT 'System',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # A/B Tests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ab_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            template_a_id INTEGER,
            template_b_id INTEGER,
            status TEXT DEFAULT 'running', -- running, completed
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_a_id) REFERENCES templates (id),
            FOREIGN KEY (template_b_id) REFERENCES templates (id)
        )
    ''')

    conn.commit()
    conn.close()
    
    # Run migrations for existing databases
    run_migrations()


def run_migrations():
    """Run database migrations to update schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if new columns exist in investors table
    cursor.execute("PRAGMA table_info(investors)")
    columns = [info[1] for info in cursor.fetchall()]
    
    new_columns = {
        'phone': 'TEXT',
        'linkedin': 'TEXT',
        'status': "TEXT DEFAULT 'NEW'",  # NEW, CONTACTED, REPLIED, MEETING, REJECTED
        'tags': 'TEXT',  # comma separated
        'last_contacted_at': 'TIMESTAMP'
    }
    
    for col, type_def in new_columns.items():
        if col not in columns:
            print(f"Migrating: Adding {col} to investors table...")
            try:
                cursor.execute(f"ALTER TABLE investors ADD COLUMN {col} {type_def}")
            except sqlite3.OperationalError as e:
                print(f"Migration error for {col}: {e}")
                
    conn.commit()
    conn.close()


# ============ INVESTOR OPERATIONS ============

def add_investor(name, email, company="", category="GENEL", notes="", phone="", linkedin="", status="NEW", tags=""):
    """Add a new investor"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO investors (name, email, company, category, notes, phone, linkedin, status, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, company, category, notes, phone, linkedin, status, tags))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # Email already exists
    finally:
        conn.close()


def get_all_investors():
    """Get all active investors"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM investors WHERE is_active = 1 ORDER BY category, name')
    investors = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return investors


def get_investors_by_category(category):
    """Get investors by category"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM investors WHERE category = ? AND is_active = 1', (category,))
    investors = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return investors


def get_investor_by_id(investor_id):
    """Get a single investor by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM investors WHERE id = ?', (investor_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_investor(investor_id, name, email, company, category, notes, phone, linkedin, status, tags):
    """Update an investor"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE investors 
        SET name = ?, email = ?, company = ?, category = ?, notes = ?, 
            phone = ?, linkedin = ?, status = ?, tags = ?
        WHERE id = ?
    ''', (name, email, company, category, notes, phone, linkedin, status, tags, investor_id))
    conn.commit()
    conn.close()


def delete_investor(investor_id):
    """Soft delete an investor"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE investors SET is_active = 0 WHERE id = ?', (investor_id,))
    conn.commit()
    conn.close()


def get_categories():
    """Get all unique categories"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM investors WHERE is_active = 1')
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()
    return categories if categories else ['GENEL']


def bulk_add_investors(investors_list):
    """Add multiple investors at once"""
    conn = get_connection()
    cursor = conn.cursor()
    added = 0
    skipped = 0
    
    for inv in investors_list:
        try:
            cursor.execute('''
                INSERT INTO investors (name, email, company, category, notes, phone, linkedin, status, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                inv.get('name', ''),
                inv.get('email', ''),
                inv.get('company', ''),
                inv.get('category', 'GENEL'),
                inv.get('notes', ''),
                inv.get('phone', ''),
                inv.get('linkedin', ''),
                inv.get('status', 'NEW'),
                inv.get('tags', '')
            ))
            added += 1
        except sqlite3.IntegrityError:
            skipped += 1  # Email already exists
    
    conn.commit()
    conn.close()
    return added, skipped


# ============ TEMPLATE OPERATIONS ============

def add_template(name, subject, body, category="GENEL"):
    """Add a new template"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO templates (name, subject, body, category)
        VALUES (?, ?, ?, ?)
    ''', (name, subject, body, category))
    conn.commit()
    template_id = cursor.lastrowid
    conn.close()
    return template_id


def get_all_templates():
    """Get all templates"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM templates ORDER BY name')
    templates = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return templates


def get_template_by_id(template_id):
    """Get a single template by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_template(template_id, name, subject, body, category):
    """Update a template"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE templates 
        SET name = ?, subject = ?, body = ?, category = ?, updated_at = ?
        WHERE id = ?
    ''', (name, subject, body, category, datetime.now(), template_id))
    conn.commit()
    conn.close()


def delete_template(template_id):
    """Delete a template"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
    conn.commit()
    conn.close()


# ============ SENT MAIL OPERATIONS ============

def log_sent_mail(investor_id, template_id, subject, status="sent", error_message=None):
    """Log a sent mail"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sent_mails (investor_id, template_id, subject, status, error_message)
        VALUES (?, ?, ?, ?, ?)
    ''', (investor_id, template_id, subject, status, error_message))
    conn.commit()
    conn.close()


def get_sent_mails(limit=50):
    """Get recent sent mails with investor info"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            sm.id,
            sm.subject,
            sm.sent_at,
            sm.status,
            sm.error_message,
            i.name as investor_name,
            i.email as investor_email,
            i.company as investor_company,
            t.name as template_name
        FROM sent_mails sm
        LEFT JOIN investors i ON sm.investor_id = i.id
        LEFT JOIN templates t ON sm.template_id = t.id
        ORDER BY sm.sent_at DESC
        LIMIT ?
    ''', (limit,))
    mails = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return mails


def get_stats():
    """Get dashboard statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total investors
    cursor.execute('SELECT COUNT(*) as count FROM investors WHERE is_active = 1')
    total_investors = cursor.fetchone()['count']
    
    # Total sent mails
    cursor.execute('SELECT COUNT(*) as count FROM sent_mails WHERE status = "sent"')
    total_sent = cursor.fetchone()['count']
    
    # Total templates
    cursor.execute('SELECT COUNT(*) as count FROM templates')
    total_templates = cursor.fetchone()['count']
    
    # Failed mails
    cursor.execute('SELECT COUNT(*) as count FROM sent_mails WHERE status = "failed"')
    total_failed = cursor.fetchone()['count']
    
    # Mails sent today
    cursor.execute('''
        SELECT COUNT(*) as count FROM sent_mails 
        WHERE date(sent_at) = date('now') AND status = "sent"
    ''')
    sent_today = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_investors': total_investors,
        'total_sent': total_sent,
        'total_templates': total_templates,
        'total_failed': total_failed,
        'sent_today': sent_today
    }


# ============ INTERACTION OPERATIONS ============

def add_interaction(investor_id, type, content):
    """Add a new interaction (note, meeting, etc.)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO interactions (investor_id, type, content)
        VALUES (?, ?, ?)
    ''', (investor_id, type, content))
    conn.commit()
    conn.close()


def get_investor_interactions(investor_id):
    """Get all interactions for an investor"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM interactions 
        WHERE investor_id = ? 
        ORDER BY date DESC
    ''', (investor_id,))
    interactions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return interactions


    return interactions


# ============ SCHEDULER OPERATIONS ============

def schedule_mail(investor_id, template_id, subject, body, scheduled_time):
    """Schedule a mail for future sending"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scheduled_mails (investor_id, template_id, subject, body, scheduled_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (investor_id, template_id, subject, body, scheduled_time))
    conn.commit()
    conn.close()


def get_pending_scheduled_mails():
    """Get mails that are ready to be sent with investor details"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute('''
        SELECT 
            sm.id, sm.investor_id, sm.template_id, sm.subject, sm.body, sm.scheduled_time,
            i.email as investor_email, i.name as investor_name
        FROM scheduled_mails sm
        JOIN investors i ON sm.investor_id = i.id
        WHERE sm.status = 'pending' AND sm.scheduled_time <= ?
    ''', (now,))
    mails = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return mails


def update_scheduled_mail_status(mail_id, status):
    """Update status of a scheduled mail"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE scheduled_mails SET status = ? WHERE id = ?', (status, mail_id))
    conn.commit()
    conn.close()



# ============ ADVANCED FEATURES OPERATIONS ============

def add_unsubscribe(email, reason="Unsubscribe link"):
    """Add email to unsubscribe list"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO unsubscribes (email, reason)
            VALUES (?, ?)
        ''', (email, reason))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def is_unsubscribed(email):
    """Check if email is unsubscribed"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM unsubscribes WHERE email = ?', (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def log_audit(action, details, performed_by="System"):
    """Log an audit event"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audit_logs (action, details, performed_by)
        VALUES (?, ?, ?)
    ''', (action, details, performed_by))
    conn.commit()
    conn.close()

def get_audit_logs(limit=50):
    """Get recent audit logs"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs

# Initialize database on import
init_db()
