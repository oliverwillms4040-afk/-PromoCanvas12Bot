import os
import logging
import asyncio
from datetime import datetime
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
from config import Config
from database import Database
from utils.image_generator import ImageGenerator
from utils.validators import Validator
from utils.helpers import format_campaign_summary, get_dimensions

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(
    CAMPAIGN_NAME,
    CAMPAIGN_DETAILS,
    TARGET_AUDIENCE,
    DESIGN_STYLE,
    COLOR_SCHEME,
    IMAGE_UPLOAD,
    DIMENSIONS,
    CONFIRMATION
) = range(8)

class PromoCanvasBot:
    def __init__(self):
        self.config = Config()
        self.db = Database(self.config.DATABASE_URL)
        self.image_generator = ImageGenerator(self.config)
        self.validator = Validator()
        self.user_data = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Track user in database
        self.db.add_user(
            user.id,
            user.username,
            user.first_name,
            user.last_name
        )
        
        welcome_text = f"""
🎨 *Welcome to PromoCanvas Bot, {user.first_name}!*

I'm your AI-powered campaign design assistant. I'll help you create professional promotional visuals for your marketing campaigns.

✨ *What I can do:*
• Generate professional ad creatives
• Create compelling campaign copy
• Apply your brand colors and style
• Provide multiple design variations
• Create visuals in various dimensions

🚀 *Ready to create something amazing?*

Use the buttons below to get started or type /help for more information.
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Create Campaign", callback_data="create_campaign")],
            [InlineKeyboardButton("🎨 View Styles", callback_data="view_styles")],
            [InlineKeyboardButton("📊 My Campaigns", callback_data="my_campaigns")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 *PromoCanvas Bot Help*

*Available Commands:*
/start - Welcome and main menu
/create - Start a new campaign design
/help - Show this help message
/styles - View available design styles
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
📸 Photo-focused - Image-centric
🖋️ Typography Focus - Text-driven

*Tips for Best Results:*
• Be detailed in your campaign description
• Upload high-quality images (PNG/JPG)
• Choose appropriate dimensions for your platform
• Provide clear target audience info

*Need More Help?*
Contact support: support@promocanvas.com
        """
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def styles_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /styles command"""
        styles_text = """
🎨 *Available Design Styles*

*Modern Minimalist*
Clean, simple, and elegant design with plenty of whitespace

*Creative Artistic*
Bold, expressive, and unique artistic designs

*Professional Corporate*
Formal, business-ready designs with professional appeal

*Bold & Vibrant*
Eye-catching, energetic, and dynamic designs

*Photo-focused*
Image-centric designs that emphasize visual storytelling

*Typography Focus*
Text-driven designs with creative typography

*Color Schemes Available:*
🔵 Blues - Professional and calming
🔴 Reds - Energetic and passionate
🟢 Greens - Natural and fresh
🟠 Warm Colors - Cozy and inviting
🌙 Dark Mode - Modern and dramatic
☀️ Bright Colors - Fun and vibrant

*Command:* /create to start designing!
        """
        await update.message.reply_text(styles_text, parse_mode=ParseMode.MARKDOWN)

    async def create_campaign(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start campaign creation process"""
        query = update.callback_query if update.callback_query else None
        
        if query:
            await query.answer()
            message = query.message
        else:
            message = update.message
        
        user_id = update.effective_user.id
        self.user_data[user_id] = {
            'step': 'name',
            'created_at': datetime.now()
        }
        
        await message.reply_text(
            "📝 *Let's Create Your Campaign!*\n\n"
            "First, give your campaign a *name*.\n"
            "Example: 'Summer Sale 2026' or 'Product Launch'\n\n"
            "Please enter the campaign name:",
            parse_mode=ParseMode.MARKDOWN
        )
        return CAMPAIGN_NAME

    async def handle_campaign_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle campaign name input"""
        user_id = update.effective_user.id
        name = update.message.text.strip()
        
        if not self.validator.validate_campaign_name(name):
            await update.message.reply_text(
                "❌ Campaign name must be between 3 and 100 characters.\n"
                "Please enter a valid name:"
            )
            return CAMPAIGN_NAME
        
        self.user_data[user_id]['name'] = name
        
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
        return CAMPAIGN_DETAILS

    async def handle_campaign_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle campaign details input"""
        user_id = update.effective_user.id
        details = update.message.text.strip()
        
        if not self.validator.validate_campaign_details(details):
            await update.message.reply_text(
                "❌ Please provide more details (at least 20 characters).\n"
                "Describe your campaign in more detail:"
            )
            return CAMPAIGN_DETAILS
        
        self.user_data[user_id]['details'] = details
        
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
        return TARGET_AUDIENCE

    async def handle_target_audience(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle target audience input"""
        user_id = update.effective_user.id
        audience = update.message.text.strip()
        
        if not self.validator.validate_audience(audience):
            await update.message.reply_text(
                "❌ Please provide a valid audience description (3-200 characters)."
            )
            return TARGET_AUDIENCE
        
        self.user_data[user_id]['audience'] = audience
        
        # Show style selection
        keyboard = [
            [InlineKeyboardButton("🎯 Modern Minimalist", callback_data="style_modern")],
            [InlineKeyboardButton("🎨 Creative Artistic", callback_data="style_artistic")],
            [InlineKeyboardButton("💼 Professional Corporate", callback_data="style_corporate")],
            [InlineKeyboardButton("🌟 Bold & Vibrant", callback_data="style_vibrant")],
            [InlineKeyboardButton("📸 Photo-focused", callback_data="style_photo")],
            [InlineKeyboardButton("🖋️ Typography Focus", callback_data="style_typography")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎨 *Select Design Style*\n\n"
            "Choose a design style that best fits your campaign:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        return DESIGN_STYLE

    async def handle_style_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle design style selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        style = query.data.replace('style_', '')
        self.user_data[user_id]['style'] = style
        
        # Color scheme selection
        keyboard = [
            [InlineKeyboardButton("🔵 Classic Blue", callback_data="color_blue")],
            [InlineKeyboardButton("🔴 Passion Red", callback_data="color_red")],
            [InlineKeyboardButton("🟢 Fresh Green", callback_data="color_green")],
            [InlineKeyboardButton("🟠 Warm Orange", callback_data="color_warm")],
            [InlineKeyboardButton("🌙 Dark Night", callback_data="color_dark")],
            [InlineKeyboardButton("☀️ Bright Sun", callback_data="color_bright")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        style_names = {
            'modern': 'Modern Minimalist',
            'artistic': 'Creative Artistic',
            'corporate': 'Professional Corporate',
            'vibrant': 'Bold & Vibrant',
            'photo': 'Photo-focused',
            'typography': 'Typography Focus'
        }
        
        await query.message.edit_text(
            f"✅ Style selected: *{style_names.get(style, style)}*\n\n"
            "🎨 *Choose a Color Scheme*\n\n"
            "Select the color palette for your campaign:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        return COLOR_SCHEME

    async def handle_color_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle color scheme selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        color = query.data.replace('color_', '')
        self.user_data[user_id]['color'] = color
        
        color_names = {
            'blue': 'Classic Blue',
            'red': 'Passion Red',
            'green': 'Fresh Green',
            'warm': 'Warm Orange',
            'dark': 'Dark Night',
            'bright': 'Bright Sun'
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
        return IMAGE_UPLOAD

    async def handle_image_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image upload"""
        user_id = update.effective_user.id
        
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            self.user_data[user_id]['image'] = {
                'file_id': photo.file_id,
                'file_path': file.file_path
            }
            await update.message.reply_text("✅ Image uploaded successfully!")
        elif update.message.document:
            document = update.message.document
            if document.mime_type and document.mime_type.startswith('image/'):
                if document.file_size > 20 * 1024 * 1024:
                    await update.message.reply_text("❌ Image is too large (max 20MB)")
                    return IMAGE_UPLOAD
                file = await context.bot.get_file(document.file_id)
                self.user_data[user_id]['image'] = {
                    'file_id': document.file_id,
                    'file_path': file.file_path
                }
                await update.message.reply_text("✅ Image uploaded successfully!")
            else:
                await update.message.reply_text("❌ Please upload an image file (JPG, PNG, GIF, WebP)")
                return IMAGE_UPLOAD
        else:
            await update.message.reply_text("❌ Please upload an image or type /skip")
            return IMAGE_UPLOAD
        
        return await self.show_dimensions_selection(update, context)

    async def skip_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Skip image upload"""
        user_id = update.effective_user.id
        self.user_data[user_id]['image'] = None
        await update.message.reply_text("⏭️ Skipped image upload")
        return await self.show_dimensions_selection(update, context)

    async def show_dimensions_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show dimension selection"""
        if update.callback_query:
            message = update.callback_query.message
        else:
            message = update.message
        
        keyboard = [
            [InlineKeyboardButton("📱 Instagram (1080x1080)", callback_data="dim_instagram")],
            [InlineKeyboardButton("📘 Facebook (1200x630)", callback_data="dim_facebook")],
            [InlineKeyboardButton("🐦 Twitter (1200x675)", callback_data="dim_twitter")],
            [InlineKeyboardButton("📺 YouTube (1280x720)", callback_data="dim_youtube")],
            [InlineKeyboardButton("📧 Email Banner (600x400)", callback_data="dim_email")],
            [InlineKeyboardButton("📄 Print A4 (2480x3508)", callback_data="dim_print")],
            [InlineKeyboardButton("📱 Story (1080x1920)", callback_data="dim_story")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            "📐 *Select Dimensions*\n\n"
            "Choose the dimensions for your creative:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        return DIMENSIONS

    async def handle_dimensions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle dimension selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        dimension = query.data.replace('dim_', '')
        self.user_data[user_id]['dimension'] = dimension
        
        width, height = get_dimensions(dimension)
        self.user_data[user_id]['width'] = width
        self.user_data[user_id]['height'] = height
        
        # Show confirmation
        return await self.show_confirmation(update, context)

    async def show_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show campaign confirmation"""
        query = update.callback_query
        user_id = query.from_user.id
        data = self.user_data[user_id]
        
        summary = format_campaign_summary(data)
        
        keyboard = [
            [InlineKeyboardButton("✅ Generate Design", callback_data="generate")],
            [InlineKeyboardButton("🔄 Start Over", callback_data="start_over")],
            [InlineKeyboardButton("✏️ Edit Details", callback_data="edit_details")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            f"📋 *Campaign Summary*\n\n{summary}\n\n"
            "Review your campaign details and click 'Generate Design' when ready:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        return CONFIRMATION

    async def generate_design(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate the campaign design"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = self.user_data[user_id]
        
        # Send processing message
        processing_msg = await query.message.edit_text(
            "🎨 *Generating Your Campaign Design...*\n\n"
            "Please wait while I create your professional visuals...\n"
            "⏳ This may take a few moments.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Generate campaign copy
            campaign_copy = self.generate_campaign_copy(data)
            
            # Generate image
            result = await self.image_generator.generate(
                campaign_details=data['details'],
                style=data['style'],
                color=data['color'],
                width=data['width'],
                height=data['height'],
                logo_path=data.get('image')
            )
            
            # Save to database
            campaign_id = self.db.save_campaign(
                user_id=user_id,
                name=data['name'],
                details=data['details'],
                audience=data['audience'],
                style=data['style'],
                color=data['color'],
                dimension=data['dimension'],
                image_url=result.get('image_url', ''),
                copy_text=campaign_copy
            )
            
            # Send the generated image
            caption = f"""
🎨 *Campaign Design Generated!*

📋 *Campaign:* {data['name']}
🎨 *Style:* {data['style'].title()}
🎨 *Colors:* {data['color'].title()}
📐 *Dimensions:* {data['dimension'].title()} ({data['width']}x{data['height']})

📝 *Generated Copy:*
{campaign_copy}

💡 *What's Next?*
• Download the image above
• Share with your team for feedback
• Use in your marketing channels
• Create variations with /create

*Commands:*
/create - Start a new campaign
/mycampaigns - View your campaigns
/feedback - Send feedback
            """
            
            # Delete processing message
            await processing_msg.delete()
            
            # Send image
            if result.get('success') and result.get('image_data'):
                from io import BytesIO
                import base64
                
                image_bytes = base64.b64decode(result['image_data'])
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=BytesIO(image_bytes),
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.message.reply_text(
                    f"⚠️ *Design Generation Note*\n\n"
                    f"I've generated your campaign copy but couldn't create the image at this moment.\n\n"
                    f"*Campaign Copy:*\n{campaign_copy}\n\n"
                    f"Campaign ID: {campaign_id}\n\n"
                    f"You can use this copy with any design tool to create your visual.",
                    parse_mode=ParseMode.MARKDOWN
                )
            
        except Exception as e:
            logger.error(f"Error generating design: {e}")
            await processing_msg.delete()
            await query.message.reply_text(
                "❌ *Error Generating Design*\n\n"
                "There was an error creating your campaign design. Please try again later.\n\n"
                "Use /create to start over or /help for assistance.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Clean up user data
        if user_id in self.user_data:
            del self.user_data[user_id]
        
        return ConversationHandler.END

    def generate_campaign_copy(self, data):
        """Generate campaign copy based on user input"""
        style_descriptions = {
            'modern': 'clean and minimalist',
            'artistic': 'creative and artistic',
            'corporate': 'professional and business-focused',
            'vibrant': 'bold and energetic',
            'photo': 'visually compelling',
            'typography': 'typographically creative'
        }
        
        style_desc = style_descriptions.get(data['style'], 'professional')
        
        # Generate headline
        headline = f"🚀 {data['name']} - Elevate Your {data['audience'].split()[0] if data['audience'] else 'Brand'} Experience"
        
        # Generate sub-headline
        sub_headline = f"Unlock the full potential of your campaign with our {style_desc} approach"
        
        # Generate description
        description = f"Discover how {data['name']} can transform your {data['audience']} journey. " \
                    f"Join thousands of satisfied customers who have achieved remarkable results."
        
        # Generate CTA
        cta = "Get Started Today and See the Difference!"
        
        return f"""
🎯 *Headline:* {headline}

✨ *Sub-headline:* {sub_headline}

📝 *Description:* {description}

📣 *Call to Action:* {cta}

*Key Message:* {data['details'][:150]}...
        """

    async def my_campaigns(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's campaigns"""
        user_id = update.effective_user.id
        campaigns = self.db.get_user_campaigns(user_id, limit=10)
        
        if not campaigns:
            await update.message.reply_text(
                "📊 *Your Campaigns*\n\n"
                "You haven't created any campaigns yet.\n"
                "Use /create to start your first campaign!",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        text = "📊 *Your Recent Campaigns*\n\n"
        for campaign in campaigns[:5]:
            text += f"📋 *{campaign['name']}*\n"
            text += f"   Style: {campaign['style'].title()}\n"
            text += f"   Created: {campaign['created_at'][:10]}\n"
            text += f"   Status: {campaign['status']}\n\n"
        
        text += "\nUse /create to start a new campaign!"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Create New", callback_data="create_campaign")],
            [InlineKeyboardButton("📖 Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel current operation"""
        user_id = update.effective_user.id
        if user_id in self.user_data:
            del self.user_data[user_id]
        
        await update.message.reply_text(
            "🔄 *Operation Cancelled*\n\n"
            "You can start a new campaign with /create anytime!\n"
            "Need help? Use /help",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "create_campaign":
            return await self.create_campaign(update, context)
        elif data == "view_styles":
            return await self.styles_command(update, context)
        elif data == "my_campaigns":
            return await self.my_campaigns(update, context)
        elif data == "help":
            return await self.help_command(update, context)
        elif data == "generate":
            return await self.generate_design(update, context)
        elif data == "start_over":
            user_id = query.from_user.id
            if user_id in self.user_data:
                del self.user_data[user_id]
            return await self.create_campaign(update, context)
        elif data == "edit_details":
            await query.message.reply_text(
                "✏️ *Edit Details*\n\n"
                "Use /create to start over with new details.",
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        elif data.startswith(("style_", "color_", "dim_")):
            # These are handled in their respective handlers
            pass

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    def get_application(self):
        """Create and configure the application"""
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Conversation handler for campaign creation
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('create', self.create_campaign),
                CallbackQueryHandler(self.create_campaign, pattern='create_campaign')
            ],
            states={
                CAMPAIGN_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_campaign_name)
                ],
                CAMPAIGN_DETAILS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_campaign_details)
                ],
                TARGET_AUDIENCE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_target_audience)
                ],
                DESIGN_STYLE: [
                    CallbackQueryHandler(self.handle_style_selection, pattern='style_')
                ],
                COLOR_SCHEME: [
                    CallbackQueryHandler(self.handle_color_selection, pattern='color_')
                ],
                IMAGE_UPLOAD: [
                    MessageHandler(filters.PHOTO | filters.Document.IMAGE, self.handle_image_upload),
                    CommandHandler('skip', self.skip_image)
                ],
                DIMENSIONS: [
                    CallbackQueryHandler(self.handle_dimensions, pattern='dim_')
                ],
                CONFIRMATION: [
                    CallbackQueryHandler(self.handle_callback)
                ]
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel),
                CommandHandler('help', self.help_command)
            ],
            per_message=False
        )
        
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('help', self.help_command))
        application.add_handler(CommandHandler('styles', self.styles_command))
        application.add_handler(CommandHandler('mycampaigns', self.my_campaigns))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_error_handler(self.error_handler)
        
        return application

    async def run(self):
        """Run the bot"""
        application = self.get_application()
        
        # Start the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logger.info("🚀 Bot is running...")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            await application.updater.stop()
            await application.stop()
            await application.shutdown()

if __name__ == '__main__':
    bot = PromoCanvasBot()
    asyncio.run(bot.run())
