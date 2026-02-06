"""
Investor Mail System - Mail Sender
Gmail SMTP integration with rate limiting

Developed by: emirgunyy & gktrk363
"""
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SERVER, SMTP_PORT, RATE_LIMIT_SECONDS


class MailSender:
    def __init__(self, email, app_password):
        """Initialize mail sender with Gmail credentials"""
        self.email = email
        self.app_password = app_password
        self.smtp = None
        self.is_connected = False
        self.last_send_time = 0
    
    def connect(self):
        """Connect to Gmail SMTP server"""
        try:
            self.smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            self.smtp.starttls()
            self.smtp.login(self.email, self.app_password)
            self.is_connected = True
            return True, "Gmail'e başarıyla bağlanıldı!"
        except smtplib.SMTPAuthenticationError:
            return False, "❌ Kimlik doğrulama hatası! Gmail adresi veya uygulama şifresi yanlış."
        except Exception as e:
            return False, f"❌ Bağlantı hatası: {str(e)}"
    
    def disconnect(self):
        """Disconnect from SMTP server"""
        if self.smtp:
            try:
                self.smtp.quit()
            except:
                pass
        self.is_connected = False
    
    def test_connection(self):
        """Test if connection is still active"""
        if not self.is_connected or not self.smtp:
            return False
        try:
            self.smtp.noop()
            return True
        except:
            self.is_connected = False
            return False
    
    def _rate_limit(self):
        """Apply rate limiting between emails"""
        elapsed = time.time() - self.last_send_time
        if elapsed < RATE_LIMIT_SECONDS:
            time.sleep(RATE_LIMIT_SECONDS - elapsed)
        self.last_send_time = time.time()
    
    def send_email(self, to_email, to_name, subject, body_html, attachments=None):
        """
        Send a single email
        attachments: list of (filename, file_content_bytes, mime_type) or streamlit UploadedFile objects
        """
        if not self.is_connected:
            return False, "SMTP bağlantısı yok!"
        
        # Rate limit
        self._rate_limit()
        
        try:
            # Create message
            msg = MIMEMultipart('mixed')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Message body
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
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
                            ctype = 'application/octet-stream'
                            
                    main_type, sub_type = ctype.split('/', 1)
                    
                    part = MIMEBase(main_type, sub_type)
                    part.set_payload(content)
                    encoders.encode_base64(part)
                    
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{filename}"'
                    )
                    msg.attach(part)
            
            # Send
            self.smtp.sendmail(self.email, to_email, msg.as_string())
            
            return True, "✅ Gönderildi"
        
        except smtplib.SMTPRecipientsRefused:
            return False, "❌ Geçersiz mail adresi"
        except smtplib.SMTPServerDisconnected:
             self.is_connected = False
             return False, "❌ SMTP bağlantısı koptu"
        except Exception as e:
            return False, f"❌ Hata: {str(e)}"
    
    def send_bulk(self, recipients, subject, body_template, template_engine, progress_callback=None, attachments=None):
        """
        Send bulk emails with personalization
        
        recipients: list of dicts with 'email', 'name', 'company' etc.
        body_template: Jinja2 template string
        template_engine: function to render template
        progress_callback: function to call with progress updates
        attachments: list of files to attach to all emails
        """
        results = []
        total = len(recipients)
        
        for idx, recipient in enumerate(recipients):
            recipient_email = recipient.get('email', '')
            
            # Check unsubscribe status
            from database import is_unsubscribed
            if is_unsubscribed(recipient_email):
                results.append({
                    'recipient': recipient,
                    'success': False,
                    'message': "⚠️ Kullanıcı abonelikten çıkmış (Unsubscribed)"
                })
                continue
            
            # Render personalized body
            try:
                body_html = template_engine(body_template, recipient)
                rendered_subject = template_engine(subject, recipient)
            except Exception as e:
                results.append({
                    'recipient': recipient,
                    'success': False,
                    'message': f"❌ Şablon hatası: {str(e)}"
                })
                continue
            
            # Send email
            success, message = self.send_email(
                to_email=recipient.get('email', ''),
                to_name=recipient.get('name', ''),
                subject=rendered_subject,
                body_html=body_html,
                attachments=attachments
            )
            
            results.append({
                'recipient': recipient,
                'success': success,
                'message': message
            })
            
            # Progress callback
            if progress_callback:
                progress_callback(idx + 1, total, recipient, success, message)
        
        return results


def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
