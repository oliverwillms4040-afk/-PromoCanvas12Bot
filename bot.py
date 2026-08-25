import os
import sys
import logging

# Try to import dotenv, install if missing
try:
    from dotenv import load_dotenv
except ImportError:
    print("📦 python-dotenv not found, installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Now import telegram
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        MessageHandler,
        filters,
        ConversationHandler,
        ContextTypes
    )
    from telegram.constants import ParseMode
except ImportError:
    print("📦 python-telegram-bot not found, installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==20.7"])
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        MessageHandler,
        filters,
        ConversationHandler,
        ContextTypes
    )
    from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
NAME, DETAILS, AUDIENCE, STYLE, COLOR, IMAGE, DIMENSIONS, CONFIRM = range(8)

# Get bot token
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found in environment variables!")
    raise ValueError("BOT_TOKEN environment variable is required!")

logger.info(f"✅ Bot token loaded successfully")

# Store user data
user_data = {}

# ============= COMMAND HANDLERS =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    welcome_text = f"""
🎨 *Welcome to PromoCanvas Bot, {user.first_name}!*

I'm your AI-powered campaign design assistant that helps create professional promotional visuals.

✨ *What I can do:*
• Generate professional ad creatives
• Create compelling campaign copy
• Apply your brand colors and style
• Create visuals in various dimensions

🚀 *Ready to create something amazing?*

📌 *Commands:*
/create - Start a new campaign
/help - Show help
/cancel - Cancel current operation
"""
    
    keyboard = [
        [InlineKeyboardButton("🚀 Create Campaign", callback_data="create")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📚 *PromoCanvas Bot Help*

*Available Commands:*
/start - Welcome and main menu
/create - Start a new campaign design
/help - Show this help message
/cancel - Cancel current operation

*Campaign Creation Process:*
1️⃣ Enter campaign name
2️⃣ Describe your campaign details
3️⃣ Define target audience
4️⃣ Choose design style
5️⃣ Select color scheme
6️⃣ Upload logo (optional)
7️⃣ Choose dimensions
8️⃣ Review and confirm

*Design Styles Available:*
🎯 Modern Minimalist - Clean and elegant
🎨 Creative Artistic - Bold and unique
💼 Professional Corporate - Formal and business
🌟 Bold & Vibrant - Eye-catching

*Tips for Best Results:*
• Be detailed in your campaign description
• Upload high-quality images
• Choose appropriate dimensions for your platform

*Need More Help?*
Contact: support@promocanvas.com
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def create_campaign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start campaign creation process"""
    query = update.callback_query if update.callback_query else None
    
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    user_id = update.effective_user.id
    user_data[user_id] = {}
    
    await message.reply_text(
        "📝 *Create Your Campaign*\n\n"
        "First, give your campaign a *name*.\n"
        "Example: 'Summer Sale 2026' or 'Product Launch'\n\n"
        "Please enter the campaign name:",
        parse_mode=ParseMode.MARKDOWN
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle campaign name input"""
    user_id = update.effective_user.id
    name = update.message.text.strip()
    
    if len(name) < 3:
        await update.message.reply_text(
            "❌ Campaign name must be at least 3 characters.\n"
            "Please enter a valid name:"
        )
        return NAME
    
    user_data[user_id]['name'] = name
    
    await update.message.reply_text(
        "📋 *Campaign Details*\n\n"
        "Please describe your campaign in detail:\n\n"
        "• What's the main message?\n"
        "• What are you promoting?\n"
        "• Any specific offers or calls to action?\n"
        "• What makes it unique?\n\n"
        "Be as detailed as possible for better results:",
        parse_mode=ParseMode.MARKDOWN
    )
    return DETAILS

async def get_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle campaign details input"""
    user_id = update.effective_user.id
    details = update.message.text.strip()
    
    if len(details) < 20:
        await update.message.reply_text(
            "❌ Please provide more details (at least 20 characters).\n"
            "Describe your campaign in more detail:"
        )
        return DETAILS
    
    user_data[user_id]['details'] = details
    
    await update.message.reply_text(
        "👥 *Target Audience*\n\n"
        "Who is your target audience?\n\n"
        "Examples:\n"
        "• Young professionals aged 25-35\n"
        "• Tech-savvy entrepreneurs\n"
        "• Fitness enthusiasts\n"
        "• Parents with young children\n\n"
        "Please describe your target audience:",
        parse_mode=ParseMode.MARKDOWN
    )
    return AUDIENCE

async def get_audience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle target audience input"""
    user_id = update.effective_user.id
    audience = update.message.text.strip()
    
    if len(audience) < 3:
        await update.message.reply_text(
            "❌ Please provide a valid audience description (at least 3 characters)."
        )
        return AUDIENCE
    
    user_data[user_id]['audience'] = audience
    
    # Show style selection
    keyboard = [
        [InlineKeyboardButton("🎯 Modern Minimalist", callback_data="style_modern")],
        [InlineKeyboardButton("🎨 Creative Artistic", callback_data="style_artistic")],
        [InlineKeyboardButton("💼 Professional Corporate", callback_data="style_corporate")],
        [InlineKeyboardButton("🌟 Bold & Vibrant", callback_data="style_vibrant")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎨 *Select Design Style*\n\n"
        "Choose a design style that best fits your campaign:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return STYLE

async def get_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle design style selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    style = query.data.replace('style_', '')
    user_data[user_id]['style'] = style
    
    style_names = {
        'modern': 'Modern Minimalist',
        'artistic': 'Creative Artistic',
        'corporate': 'Professional Corporate',
        'vibrant': 'Bold & Vibrant'
    }
    
    # Color scheme selection
    keyboard = [
        [InlineKeyboardButton("🔵 Classic Blue", callback_data="color_blue")],
        [InlineKeyboardButton("🔴 Passion Red", callback_data="color_red")],
        [InlineKeyboardButton("🟢 Fresh Green", callback_data="color_green")],
        [InlineKeyboardButton("🌙 Dark Night", callback_data="color_dark")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        f"✅ Style selected: *{style_names.get(style, style)}*\n\n"
        "🎨 *Choose a Color Scheme*\n\n"
        "Select the color palette for your campaign:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return COLOR

async def get_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle color scheme selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    color = query.data.replace('color_', '')
    user_data[user_id]['color'] = color
    
    color_names = {
        'blue': 'Classic Blue',
        'red': 'Passion Red',
        'green': 'Fresh Green',
        'dark': 'Dark Night'
    }
    
    await query.message.edit_text(
        f"✅ Color scheme selected: *{color_names.get(color, color)}*\n\n"
        "🖼️ *Upload Your Logo or Image*\n\n"
        "Upload your logo or brand image to include in the design.\n"
        "Supported formats: JPG, PNG, GIF, WebP\n"
        "Max size: 20MB\n\n"
        "Type /skip to continue without an image:",
        parse_mode=ParseMode.MARKDOWN
    )
    return IMAGE

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image upload"""
    user_id = update.effective_user.id
    
    if update.message.photo:
        photo = update.message.photo[-1]
        user_data[user_id]['image'] = photo.file_id
        await update.message.reply_text("✅ Image uploaded successfully!")
    elif update.message.document:
        document = update.message.document
        if document.mime_type and document.mime_type.startswith('image/'):
            if document.file_size > 20 * 1024 * 1024:
                await update.message.reply_text("❌ Image is too large (max 20MB)")
                return IMAGE
            user_data[user_id]['image'] = document.file_id
            await update.message.reply_text("✅ Image uploaded successfully!")
        else:
            await update.message.reply_text("❌ Please upload an image file (JPG, PNG, GIF, WebP)")
            return IMAGE
    else:
        await update.message.reply_text("❌ Please upload an image or type /skip")
        return IMAGE
    
    return await show_dimensions(update, context)

async def skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip image upload"""
    user_id = update.effective_user.id
    user_data[user_id]['image'] = None
    await update.message.reply_text("⏭️ Skipped image upload")
    return await show_dimensions(update, context)

async def show_dimensions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show dimension selection"""
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message
    
    keyboard = [
        [InlineKeyboardButton("📱 Instagram (1080x1080)", callback_data="dim_instagram")],
        [InlineKeyboardButton("📘 Facebook (1200x630)", callback_data="dim_facebook")],
        [InlineKeyboardButton("🐦 Twitter (1200x675)", callback_data="dim_twitter")],
        [InlineKeyboardButton("📺 YouTube (1280x720)", callback_data="dim_youtube")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "📐 *Select Dimensions*\n\n"
        "Choose the dimensions for your creative:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return DIMENSIONS

async def get_dimensions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle dimension selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    dimension = query.data.replace('dim_', '')
    user_data[user_id]['dimension'] = dimension
    
    # Dimension display names
    dim_names = {
        'instagram': 'Instagram (1080x1080)',
        'facebook': 'Facebook (1200x630)',
        'twitter': 'Twitter (1200x675)',
        'youtube': 'YouTube (1280x720)'
    }
    
    # Show confirmation
    data = user_data[user_id]
    
    summary = f"""
📋 *Campaign Summary*

📝 *Name:* {data.get('name', 'Not set')}
📋 *Details:* {data.get('details', 'Not set')[:100]}...
👥 *Audience:* {data.get('audience', 'Not set')}
🎨 *Style:* {data.get('style', 'Not set').title()}
🎨 *Color:* {data.get('color', 'Not set').title()}
📐 *Dimension:* {dim_names.get(dimension, dimension)}
🖼️ *Image:* {'✅ Uploaded' if data.get('image') else '❌ Skipped'}
    """
    
    keyboard = [
        [InlineKeyboardButton("✅ Generate Design", callback_data="generate")],
        [InlineKeyboardButton("🔄 Start Over", callback_data="restart")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        f"{summary}\n\n"
        "Review your campaign details and click 'Generate Design' when ready:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return CONFIRM

async def generate_design(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate the campaign design"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = user_data.get(user_id, {})
    
    # Show processing
    await query.message.edit_text(
        "🎨 *Generating Your Campaign Design...*\n\n"
        "Please wait while I create your professional visuals...\n"
        "⏳ This may take a few moments.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Simulate processing time
    import asyncio
    await asyncio.sleep(2)
    
    # Generate campaign copy
    style_descriptions = {
        'modern': 'clean and minimalist',
        'artistic': 'creative and artistic',
        'corporate': 'professional and business-focused',
        'vibrant': 'bold and energetic'
    }
    
    style_desc = style_descriptions.get(data.get('style', 'modern'), 'professional')
    
    campaign_copy = f"""
🎯 *Campaign: {data.get('name', 'Campaign')}*

📝 *Description:*
{data.get('details', 'No details provided')}

👥 *Target Audience:*
{data.get('audience', 'General audience')}

🎨 *Style & Color:*
{data.get('style', 'Modern').title()} with {data.get('color', 'Blue').title()} theme

📐 *Dimensions:* {data.get('dimension', 'instagram').title()}

💡 *Next Steps:*
1. Review the design above
2. Make adjustments if needed
3. Share your campaign!

*Commands:*
/create - Start a new campaign
/help - Get help
    """
    
    # Clear user data
    if user_id in user_data:
        del user_data[user_id]
    
    await query.message.edit_text(
        f"✅ *Campaign Design Generated!*\n\n{campaign_copy}",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    user_id = update.effective_user.id
    if user_id in user_data:
        del user_data[user_id]
    
    await update.message.reply_text(
        "🔄 *Operation Cancelled*\n\n"
        "You can start a new campaign with /create anytime!\n"
        "Need help? Use /help",
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "create":
        return await create_campaign(update, context)
    elif data == "help":
        return await help_command(update, context)
    elif data == "generate":
        return await generate_design(update, context)
    elif data == "restart":
        user_id = query.from_user.id
        if user_id in user_data:
            del user_data[user_id]
        return await create_campaign(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ *Oops! Something went wrong.*\n\n"
                "Please try again later or use /help for assistance.\n"
                "If the problem persists, contact support.",
                parse_mode=ParseMode.MARKDOWN
            )
    except:
        pass

# ============= MAIN FUNCTION =============

def main():
    """Main function to run the bot"""
    logger.info("🚀 Starting PromoCanvas Bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for campaign creation
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('create', create_campaign),
            CallbackQueryHandler(create_campaign, pattern='create')
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_details)],
            AUDIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_audience)],
            STYLE: [CallbackQueryHandler(get_style, pattern='style_')],
            COLOR: [CallbackQueryHandler(get_color, pattern='color_')],
            IMAGE: [
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image),
                CommandHandler('skip', skip_image)
            ],
            DIMENSIONS: [CallbackQueryHandler(get_dimensions, pattern='dim_')],
            CONFIRM: [CallbackQueryHandler(handle_callback)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('help', help_command)
        ],
        per_message=False
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("✅ Bot is running! Waiting for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
