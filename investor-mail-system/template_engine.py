"""
Investor Mail System - Template Engine
Jinja2-based template rendering with variable substitution

Developed by: emirgunyy & gktrk363
"""
from jinja2 import Template, Environment, BaseLoader


def render_template(template_str, context):
    """
    Render a template string with context variables
    
    Variables:
    - {{ad}} or {{name}} - Investor name
    - {{sirket}} or {{company}} - Company name
    - {{email}} - Email address
    - {{kategori}} or {{category}} - Category
    """
    # Normalize context keys (support both Turkish and English)
    normalized_context = {
        'ad': context.get('name', context.get('ad', '')),
        'name': context.get('name', context.get('ad', '')),
        'sirket': context.get('company', context.get('sirket', '')),
        'company': context.get('company', context.get('sirket', '')),
        'email': context.get('email', ''),
        'kategori': context.get('category', context.get('kategori', '')),
        'category': context.get('category', context.get('kategori', '')),
    }
    
    # Add any additional context
    for key, value in context.items():
        if key not in normalized_context:
            normalized_context[key] = value
    
    # Render template
    template = Template(template_str)
    rendered = template.render(**normalized_context)
    
    # Tracking Pixel Logic (Framework)
    # Note: This requires a deployed server to actually track opens.
    # Currently pointing to a placeholder.
    tracking_pixel = '<img src="http://localhost:8502/track.png" width="1" height="1" style="display:none;" />'
    
    if "</body>" in rendered:
        rendered = rendered.replace("</body>", f"{tracking_pixel}</body>")
    else:
        rendered += tracking_pixel
        
    return rendered


def get_default_templates():
    """Return default email templates"""
    
    templates = [
        {
            'name': 'Melek Yatırımcı Pitch',
            'subject': 'Oyun Projemiz Hakkında - Yatırım Fırsatı',
            'category': 'MELEK',
            'body': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }
        .cta-button { background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎮 Oyun Projemiz</h1>
    </div>
    <div class="content">
        <p>Sayın {{ad}},</p>
        
        <p>{{sirket}} firmasının oyun sektörüne olan ilgisini büyük bir heyecanla takip ediyorum.</p>
        
        <p>Unreal Engine 5 ile geliştirdiğimiz projemiz hakkında sizinle görüşmek istiyoruz. Projemiz:</p>
        
        <ul>
            <li>🎯 Benzersiz oynanış mekanikleri</li>
            <li>🌍 Geniş açık dünya</li>
            <li>🎨 AAA kalitesinde grafikler</li>
        </ul>
        
        <p>Kısa bir görüşme için müsait olduğunuz bir zaman dilimini paylaşabilir misiniz?</p>
        
        <a href="#" class="cta-button">Pitch Deck'i İncele</a>
        
        <p>Saygılarımla,<br>
        <strong>[İsminiz]</strong><br>
        [Oyun Stüdyonuz]</p>
    </div>
    <div class="footer">
        Bu mail size yatırım fırsatı sunmak amacıyla gönderilmiştir.<br>
        Almak istemiyorsanız lütfen "unsubscribe" yazarak yanıtlayın.
    </div>
</body>
</html>'''
        },
        {
            'name': 'VC Pitch',
            'subject': 'Oyun Stüdyosu Yatırım Fırsatı - UE5 Projesi',
            'category': 'VC',
            'body': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background: #1a1a2e; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .metrics { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .footer { background: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Yatırım Fırsatı</h1>
    </div>
    <div class="content">
        <p>Sayın {{ad}},</p>
        
        <p>{{sirket}} portföyündeki gaming yatırımlarınızı inceleme fırsatı buldum. Sizinle projemiz hakkında görüşmek istiyoruz.</p>
        
        <div class="metrics">
            <h3>📊 Proje Metrikleri</h3>
            <ul>
                <li><strong>Engine:</strong> Unreal Engine 5</li>
                <li><strong>Platform:</strong> PC, Console</li>
                <li><strong>Geliştirme Aşaması:</strong> [Aşama]</li>
                <li><strong>Talep Edilen Yatırım:</strong> [Miktar]</li>
            </ul>
        </div>
        
        <p>Detaylı pitch deck ve demo için görüşme talep ediyoruz.</p>
        
        <p>Saygılarımla,<br>
        <strong>[İsminiz]</strong><br>
        [Oyun Stüdyonuz]</p>
    </div>
    <div class="footer">
        Bu mail size yatırım fırsatı sunmak amacıyla gönderilmiştir.
    </div>
</body>
</html>'''
        },
        {
            'name': 'Gaming VC Pitch',
            'subject': 'UE5 Horror Game - Yatırım Görüşmesi',
            'category': 'GAMING',
            'body': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #eee; background: #1a1a2e; }
        .container { max-width: 600px; margin: 0 auto; background: #16213e; border-radius: 10px; overflow: hidden; }
        .header { background: linear-gradient(135deg, #e94560 0%, #0f3460 100%); padding: 30px; text-align: center; }
        .content { padding: 25px; }
        .footer { background: #0f3460; padding: 15px; text-align: center; font-size: 12px; color: #aaa; }
        .highlight { color: #e94560; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 Yeni Nesil Horror Deneyimi</h1>
        </div>
        <div class="content">
            <p>Merhaba {{ad}},</p>
            
            <p>{{sirket}}'ın gaming-focused yatırımlarını yakından takip ediyorum. Özellikle [referans oyun/stüdyo] yatırımınız dikkatimi çekti.</p>
            
            <p>Unreal Engine 5 ile geliştirdiğimiz horror oyunumuz:</p>
            
            <ul>
                <li>🔦 <span class="highlight">Lumen</span> ile dinamik aydınlatma</li>
                <li>🌊 <span class="highlight">Nanite</span> ile sinematik detaylar</li>
                <li>👻 Benzersiz korku mekanikleri</li>
            </ul>
            
            <p>Demo ve pitch deck paylaşmak için 15 dakikalık bir görüşme yapabilir miyiz?</p>
            
            <p>Best regards,<br>
            <strong>[İsminiz]</strong></p>
        </div>
        <div class="footer">
            Gaming industry investment opportunity
        </div>
    </div>
</body>
</html>'''
        },
        {
            'name': 'Follow-up Mail',
            'subject': 'Re: Oyun Projemiz Hakkında - Takip',
            'category': 'GENEL',
            'body': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .content { padding: 20px; }
    </style>
</head>
<body>
    <div class="content">
        <p>Sayın {{ad}},</p>
        
        <p>Geçen hafta gönderdiğim mail hakkında takip yapmak istedim.</p>
        
        <p>Oyun projemiz hakkında kısa bir görüşme için müsait olur musunuz?</p>
        
        <p>Pitch deck'i incelemeniz için tekrar ekliyorum.</p>
        
        <p>Saygılarımla,<br>
        <strong>[İsminiz]</strong></p>
    </div>
</body>
</html>'''
        },
        {
            'name': 'Teşekkür Maili',
            'subject': 'Görüşme İçin Teşekkürler',
            'category': 'GENEL',
            'body': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .content { padding: 20px; }
    </style>
</head>
<body>
    <div class="content">
        <p>Sayın {{ad}},</p>
        
        <p>Bugünkü görüşme için çok teşekkür ederiz. Projemize gösterdiğiniz ilgi bizim için çok değerli.</p>
        
        <p>Görüşmede bahsettiğimiz materyalleri ekte bulabilirsiniz:</p>
        
        <ul>
            <li>📄 Güncel Pitch Deck</li>
            <li>🎬 Gameplay Video</li>
            <li>📊 Finansal Projeksiyonlar</li>
        </ul>
        
        <p>Herhangi bir sorunuz olursa lütfen bize ulaşın.</p>
        
        <p>Saygılarımla,<br>
        <strong>[İsminiz]</strong><br>
        [Oyun Stüdyonuz]</p>
    </div>
</body>
</html>'''
        }
    ]
    
    return templates


def preview_template(template_body, sample_context=None):
    """Generate a preview of a template with sample data"""
    if sample_context is None:
        sample_context = {
            'name': 'Örnek Yatırımcı',
            'company': 'Örnek Ventures',
            'email': 'ornek@example.com',
            'category': 'MELEK'
        }
    
    return render_template(template_body, sample_context)


def generate_ai_suggestion(keywords, type="cold_email"):
    """
    Generate email content based on keywords (Rule-based Mock AI).
    In a real app, this would call OpenAI/Gemini API.
    """
    keywords = keywords.lower()
    
    if "oyun" in keywords or "game" in keywords:
        subject = "🎮 Geleceğin Hit Oyunu İçin Yatırım Fırsatı"
        intro = "Oyun sektöründe deneyimli ekibimizle geliştirdiğimiz yeni projemizden bahsetmek istiyorum."
    elif "saas" in keywords:
        subject = "🚀 B2B SaaS Alanında Yeni Bir Unicorn Adayı"
        intro = "İşletmelerin verimliliğini %300 artıran çözümümüzle pazara hızlı bir giriş yaptık."
    elif "toplantı" in keywords or "meeting" in keywords:
        subject = "☕ 15 Dakikalık Tanışma Toplantısı?"
        intro = "Geçen haftaki etkinliğimizden sonra sizinle vizyonumuzu paylaşmak isterim."
    else:
        subject = "🌟 [Proje Adı] Yatırım Fırsatı Hakkında"
        intro = "Sektörde fark yaratan projemizle ilgileneceğinizi düşündüm."

    body = f"""<!DOCTYPE html>
<html>
<body>
    <p>Sayın {{{{ad}}}},</p>
    
    <p>{intro}</p>
    
    <p><strong>Öne Çıkanlar:</strong></p>
    <ul>
        <li>{"Global pazar hedefi" if "global" in keywords else "Hızlı büyüyen pazar"}</li>
        <li>{"MVP hazır" if "mvp" in keywords else "Deneyimli kurucu ekip"}</li>
        <li>{"Yüksek ROI potansiyeli"}</li>
    </ul>
    
    <p>Detaylı pitch deck ekte sunulmuştur. Müsait olduğunuzda 15 dk görüşmek isterim.</p>
    
    <p>Saygılarımla,<br><strong>[Adınız]</strong></p>
</body>
</html>"""

    return subject, body
