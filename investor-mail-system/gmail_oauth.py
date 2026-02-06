"""
Investor Mail System - Gmail OAuth Authentication
Google OAuth2 flow for Gmail API access

Developed by: emirgunyy & gktrk363
"""
import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import DATA_DIR

# OAuth scopes - only what we need
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

TOKEN_FILE = os.path.join(DATA_DIR, 'gmail_token.json')
CREDENTIALS_FILE = os.path.join(DATA_DIR, 'credentials.json')


class GmailOAuth:
    """Gmail OAuth2 authentication and email sending"""
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.user_email = None
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.creds is not None and self.creds.valid
    
    def get_user_email(self):
        """Get authenticated user's email"""
        return self.user_email
    
    def load_saved_credentials(self):
        """Load credentials from saved token file"""
        if os.path.exists(TOKEN_FILE):
            try:
                self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                
                # Refresh if expired
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                    self._save_credentials()
                
                if self.creds and self.creds.valid:
                    self._init_service()
                    self._get_user_info()
                    return True
            except Exception as e:
                print(f"Error loading credentials: {e}")
                return False
        return False
    
    def _save_credentials(self):
        """Save credentials to file"""
        with open(TOKEN_FILE, 'w') as token:
            token.write(self.creds.to_json())
    
    def _init_service(self):
        """Initialize Gmail API service"""
        self.service = build('gmail', 'v1', credentials=self.creds)
    
    def _get_user_info(self):
        """Get user email from Gmail profile"""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            self.user_email = profile.get('emailAddress')
        except Exception as e:
            print(f"Error getting user info: {e}")
    
    def authenticate(self, credentials_json=None):
        """
        Start OAuth2 authentication flow
        
        credentials_json: Optional dict with OAuth client credentials
                         If not provided, will use credentials.json file
        """
        try:
            # Create credentials file if provided as dict
            if credentials_json:
                with open(CREDENTIALS_FILE, 'w') as f:
                    json.dump(credentials_json, f)
            
            if not os.path.exists(CREDENTIALS_FILE):
                return False, "credentials.json dosyası bulunamadı! Google Cloud Console'dan indirip data klasörüne koy."
            
            # Start OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, 
                SCOPES,
                redirect_uri='http://localhost:8080/'
            )
            
            # Run local server for OAuth callback
            self.creds = flow.run_local_server(
                port=8080,
                prompt='consent',
                success_message='Gmail bağlantısı başarılı! Bu pencereyi kapatabilirsiniz.',
                open_browser=True
            )
            
            # Save credentials
            self._save_credentials()
            
            # Initialize service
            self._init_service()
            self._get_user_info()
            
            return True, f"✅ Gmail'e bağlandı: {self.user_email}"
            
        except Exception as e:
            return False, f"❌ OAuth hatası: {str(e)}"
    
    def logout(self):
        """Remove saved credentials"""
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        self.creds = None
        self.service = None
        self.user_email = None
    
    def send_email(self, to_email, subject, body_html, attachments=None):
        """
        Send an email using Gmail API
        attachments: list of (filename, file_content_bytes, mime_type) or streamlit UploadedFile objects
        """
        if not self.is_authenticated():
            return False, "Gmail'e bağlı değil!"
        
        try:
            # Create message
            message = MIMEMultipart('mixed')
            message['to'] = to_email
            message['subject'] = subject
            
            # Message body
            msg_alternative = MIMEMultipart('alternative')
            message.attach(msg_alternative)
            msg_alternative.attach(MIMEText(body_html, 'html', 'utf-8'))
            
            # Handle attachments
            if attachments:
                from email.mime.base import MIMEBase
                from email import encoders
                import mimetypes
                
                for attachment in attachments:
                    # Determine filename and content
                    if hasattr(attachment, 'name') and hasattr(attachment, 'read'):
                        # Streamlit UploadedFile
                        filename = attachment.name
                        content = attachment.getvalue()
                        ctype = attachment.type
                    else:
                        # (filename, content, type) tuple
                        filename, content, ctype = attachment
                        
                    if not ctype:
                        ctype, encoding = mimetypes.guess_type(filename)
                        if ctype is None or encoding is not None:
                            # No guess could be made, or the file is encoded (compressed), so
                            # use a generic bag-of-bits type.
                            ctype = 'application/octet-stream'
                            
                    main_type, sub_type = ctype.split('/', 1)
                    
                    part = MIMEBase(main_type, sub_type)
                    part.set_payload(content)
                    encoders.encode_base64(part)
                    
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{filename}"'
                    )
                    message.attach(part)
            
            # Encode for Gmail API
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return True, "✅ Gönderildi"
            
        except Exception as e:
            error_msg = str(e)
            if 'insufficient' in error_msg.lower():
                return False, "❌ Gmail API yetkisi yetersiz. Scopes kontrol et."
            return False, f"❌ Gönderim hatası: {error_msg}"


def create_credentials_template():
    """Return template for Google OAuth credentials"""
    return {
        "installed": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["http://localhost:8080/"]
        }
    }


def check_credentials_file():
    """Check if credentials.json exists"""
    return os.path.exists(CREDENTIALS_FILE)
