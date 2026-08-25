def get_dimensions(dimension_key: str) -> tuple:
    """Get width and height for dimension key"""
    dimensions = {
        'instagram': (1080, 1080),
        'facebook': (1200, 630),
        'twitter': (1200, 675),
        'youtube': (1280, 720),
        'email': (600, 400),
        'print': (2480, 3508),
        'story': (1080, 1920)
    }
    return dimensions.get(dimension_key, (1080, 1080))

def format_campaign_summary(data: dict) -> str:
    """Format campaign data for display"""
    style_names = {
        'modern': 'Modern Minimalist',
        'artistic': 'Creative Artistic',
        'corporate': 'Professional Corporate',
        'vibrant': 'Bold & Vibrant',
        'photo': 'Photo-focused',
        'typography': 'Typography Focus'
    }
    
    color_names = {
        'blue': 'Classic Blue',
        'red': 'Passion Red',
        'green': 'Fresh Green',
        'warm': 'Warm Orange',
        'dark': 'Dark Night',
        'bright': 'Bright Sun'
    }
    
    dimension_names = {
        'instagram': 'Instagram (1080x1080)',
        'facebook': 'Facebook (1200x630)',
        'twitter': 'Twitter (1200x675)',
        'youtube': 'YouTube (1280x720)',
        'email': 'Email Banner (600x400)',
        'print': 'Print A4 (2480x3508)',
        'story': 'Story (1080x1920)'
    }
    
    summary = f"""
📋 *Campaign Name:* {data.get('name', 'Not set')}

📝 *Description:* 
{data.get('details', 'Not set')[:200]}...

👥 *Target Audience:* {data.get('audience', 'Not set')}

🎨 *Design Style:* {style_names.get(data.get('style'), data.get('style', 'Not set'))}

🎨 *Color Scheme:* {color_names.get(data.get('color'), data.get('color', 'Not set'))}

📐 *Dimensions:* {dimension_names.get(data.get('dimension'), data.get('dimension', 'Not set'))}

🖼️ *Logo/Image:* {'✅ Uploaded' if data.get('image') else '❌ Not uploaded (skipped)'}
    """
    
    return summary

def format_campaign_copy(campaign_data: dict) -> str:
    """Format campaign copy for display"""
    return f"""
🎯 *Campaign Copy*

*Headline:*
{campaign_data.get('headline', '')}

*Sub-headline:*
{campaign_data.get('subheadline', '')}

*Description:*
{campaign_data.get('description', '')}

*Call to Action:*
{campaign_data.get('cta', '')}
    """
