"""
Background scheduler for handling scheduled emails.
Runs in a separate thread and checks for pending mails every minute.

Developed by: emirgunyy & gktrk363
"""
import time
import threading
from datetime import datetime
from database import get_pending_scheduled_mails, update_scheduled_mail_status, log_sent_mail
from gmail_oauth import GmailOAuth, check_credentials_file
from mail_sender import MailSender
# Note: config import might be needed for app password, but we'll focus on OAuth for now or need to pass credentials

class EmailScheduler:
    _instance = None
    _lock = threading.Lock()
    _running = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmailScheduler, cls).__new__(cls)
                    cls._instance.start()
        return cls._instance
    
    def start(self):
        if not self._running:
            self._running = True
            thread = threading.Thread(target=self._run_loop, daemon=True)
            thread.start()
            print("Scheduler started...")
    
    def _run_loop(self):
        while self._running:
            try:
                self._check_and_send()
            except Exception as e:
                print(f"Scheduler error: {e}")
            time.sleep(60)  # Check every minute
            
    def _check_and_send(self):
        pending_mails = get_pending_scheduled_mails()
        if not pending_mails:
            return
            
        print(f"Found {len(pending_mails)} pending mails")
        
        # Try to initialize OAuth client
        oauth_client = None
        if check_credentials_file():
            oauth = GmailOAuth()
            if oauth.load_saved_credentials():
                oauth_client = oauth
        
        for mail in pending_mails:
            try:
                success = False
                error_msg = None
                
                # Try sending with OAuth
                if oauth_client:
                    success, message = oauth_client.send_email(
                        mail['investor_email'],
                        mail['subject'],
                        mail['body']
                    )
                else:
                    success = False
                    message = "OAuth credentials not available for background sending"
                
                # Update status
                new_status = 'sent' if success else 'failed'
                update_scheduled_mail_status(mail['id'], new_status)
                
                # Log to sent mails history
                log_sent_mail(
                    mail['investor_id'],
                    mail['template_id'],
                    mail['subject'],
                    new_status,
                    None if success else message
                )
                
                print(f"Scheduled mail {mail['id']} processed: {new_status} - {message}")
                
            except Exception as e:
                print(f"Error processing mail {mail['id']}: {e}")
                update_scheduled_mail_status(mail['id'], 'failed')

# Start scheduler on import if not already running
# We rely on app.py to import and instantiate this class

