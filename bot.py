import os
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Now import telegram
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
    logger.error("BOT_TOKEN not found in environment variables!")
    raise ValueError("BOT_TOKEN environment variable is required!")

logger.info(f"Bot token loaded: {BOT_TOKEN[:10]}...")

# Store user data
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    welcome_text = f"""
🎨 *Welcome to PromoCanvas Bot, {user.first_name}!*

I'm your AI-powered campaign design assistant.

✨ *What I can do:*
• Generate professional ad creatives
• Create compelling campaign copy
• Apply your brand colors and style
• Create visuals in various dimensions

🚀 *Get started with /create*

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
2️⃣ Describe your campaign
3️⃣ Define target audience
4️⃣ Choose design style
5️⃣ Select color scheme
6️⃣ Upload logo (optional)
7️⃣ Choose dimensions
8️⃣ Review and confirm

*Need Help?*
Contact: support@promocanvas.com
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def create_campaign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start campaign creation"""
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
        "Please enter a *name* for your campaign:\n"
        "Example: 'Summer Sale 2026'",
        parse_mode=ParseMode.MARKDOWN
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get campaign name"""
    user_id = update.effective_user.id
    user_data[user_id]['name'] = update.message.text.strip()
    
    await update.message.reply_text(
        "📋 *Campaign Details*\n\n"
        "Please describe your campaign in detail:\n"
        "• What's the main message?\n"
        "• What are you promoting?\n"
        "• Any specific offers?\n\n"
        "Be as detailed as possible:",
        parse_mode=ParseMode.MARKDOWN
    )
    return DETAILS

async def get_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get campaign details"""
    user_id = update.effective_user.id
    user_data[user_id]['details'] = update.message.text.strip()
    
    await update.message.reply_text(
        "👥 *Target Audience*\n\n"
        "Who is your target audience?\n"
        "Example: 'Young professionals aged 25-35'",
        parse_mode=ParseMode.MARKDOWN
    )
    return AUDIENCE

async def get_audience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get target audience"""
    user_id = update.effective_user.id
    user_data[user_id]['audience'] = update.message.text.strip()
    
    keyboard = [
        [InlineKeyboardButton("🎯 Modern Minimalist", callback_data="style_modern")],
        [InlineKeyboardButton("🎨 Creative Artistic", callback_data="style_artistic")],
        [InlineKeyboardButton("💼 Professional Corporate", callback_data="style_corporate")],
        [InlineKeyboardButton("🌟 Bold & Vibrant", callback_data="style_vibrant")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎨 *Select Design Style*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return STYLE

async def get_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get design style"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    style = query.data.replace('style_', '')
    user_data[user_id]['style'] = style
    
    keyboard = [
        [InlineKeyboardButton("🔵 Classic Blue", callback_data="color_blue")],
        [InlineKeyboardButton("🔴 Passion Red", callback_data="color_red")],
        [InlineKeyboardButton("🟢 Fresh Green", callback_data="color_green")],
        [InlineKeyboardButton("🌙 Dark Night", callback_data="color_dark")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        f"✅ Style: *{style.title()}*\n\n"
        "🎨 *Choose Color Scheme*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return COLOR

async def get_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get color scheme"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    color = query.data.replace('color_', '')
    user_data[user_id]['color'] = color
    
    await query.message.edit_text(
        f"✅ Color: *{color.title()}*\n\n"
        "🖼️ *Upload Logo/Image*\n"
        "Send an image or type /skip",
        parse_mode=ParseMode.MARKDOWN
    )
    return IMAGE

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image upload"""
    user_id = update.effective_user.id
    
    if update.message.photo:
        photo = update.message.photo[-1]
        user_data[user_id]['image'] = photo.file_id
        await update.message.reply_text("✅ Image uploaded!")
    elif update.message.document:
        doc = update.message.document
        if doc.mime_type and doc.mime_type.startswith('image/'):
            user_data[user_id]['image'] = doc.file_id
            await update.message.reply_text("✅ Image uploaded!")
        else:
            await update.message.reply_text("❌ Please upload an image file")
            return IMAGE
    else:
        await update.message.reply_text("❌ Please upload an image or type /skip")
        return IMAGE
    
    return await show_dimensions(update, context)

async def skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip image upload"""
    user_id = update.effective_user.id
    user_data[user_id]['image'] = None
    await update.message.reply_text("⏭️ Skipped image")
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
        "📐 *Select Dimensions*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return DIMENSIONS

async def get_dimensions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get dimensions"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    dimension = query.data.replace('dim_', '')
    user_data[user_id]['dimension'] = dimension
    
    # Show confirmation
    data = user_data[user_id]
    
    summary = f"""
📋 *Campaign Summary*

📝 *Name:* {data.get('name', 'Not set')}
📋 *Details:* {data.get('details', 'Not set')[:100]}...
👥 *Audience:* {data.get('audience', 'Not set')}
🎨 *Style:* {data.get('style', 'Not set').title()}
🎨 *Color:* {data.get('color', 'Not set').title()}
📐 *Dimension:* {dimension.title()}
🖼️ *Image:* {'✅ Uploaded' if data.get('image') else '❌ Skipped'}
    """
    
    keyboard = [
        [InlineKeyboardButton("✅ Generate Design", callback_data="generate")],
        [InlineKeyboardButton("🔄 Start Over", callback_data="restart")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        f"{summary}\n\n"
        "Review and click 'Generate Design':",
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
        "🎨 *Generating your design...*\n\n"
        "⏳ Please wait...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Simulate processing
    await asyncio.sleep(2)
    
    # Generate campaign copy
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
1. Review the design
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
    """Cancel operation"""
    user_id = update.effective_user.id
    if user_id in user_data:
        del user_data[user_id]
    
    await update.message.reply_text(
        "🔄 *Cancelled*\n\n"
        "Use /create to start a new campaign.",
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
                "⚠️ *Something went wrong*\n\n"
                "Please try again or use /help for assistance.",
                parse_mode=ParseMode.MARKDOWN
            )
    except:
        pass

def main():
    """Main function to run the bot"""
    logger.info("🚀 Starting PromoCanvas Bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler
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
