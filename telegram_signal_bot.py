import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random
from datetime import datetime, timedelta
import asyncio
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration - Environment Variables ব্যবহার করো
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8360851879:AAFsb1EQI-UG0dHVfg5C0hS8vYGKmFCX5as")
ALLOWED_USER_ID = int(os.environ.get('ALLOWED_USER_ID', 7436667328))

# User session storage
user_sessions = {}

# Strategy names
STRATEGIES = {
    1: "Conservative",
    2: "Moderate",
    3: "Aggressive",
    4: "Balanced",
    5: "High Frequency"
}

# Signal types
SIGNAL_TYPES = {
    1: "CALL Only",
    2: "PUT Only",
    3: "BOTH (CALL & PUT)"
}


def generate_random_signals(signal_type, start_time, end_time, strategy):
    """Generate random trading signals"""
    signals = []
    
    # Parse time
    start_h, start_m = map(int, start_time.split(':'))
    end_h, end_m = map(int, end_time.split(':'))
    
    # Calculate time range in minutes
    start_minutes = start_h * 60 + start_m
    end_minutes = end_h * 60 + end_m
    
    # Number of signals based on strategy
    signal_counts = {1: (3, 5), 2: (5, 8), 3: (8, 12), 4: (6, 9), 5: (10, 15)}
    min_signals, max_signals = signal_counts.get(strategy, (5, 8))
    
    num_signals = random.randint(min_signals, max_signals)
    
    # Generate random times
    used_times = set()
    for _ in range(num_signals):
        while True:
            random_minutes = random.randint(start_minutes, end_minutes - 1)
            if random_minutes not in used_times:
                used_times.add(random_minutes)
                break
        
        hour = random_minutes // 60
        minute = random_minutes % 60
        time_str = f"{hour:02d}:{minute:02d}"
        
        # Determine signal type
        if signal_type == 1:  # CALL Only
            sig_type = "CALL"
        elif signal_type == 2:  # PUT Only
            sig_type = "PUT"
        else:  # BOTH
            sig_type = random.choice(["CALL", "PUT"])
        
        signals.append((time_str, sig_type))
    
    # Sort by time
    signals.sort()
    
    return signals


def generate_statistics():
    """Generate random statistics"""
    accuracy = round(random.uniform(55.0, 85.0), 2)
    win_loss = round(random.uniform(1.2, 3.5), 2)
    profit_factor = round(random.uniform(1.5, 3.2), 2)
    
    return accuracy, win_loss, profit_factor


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = update.effective_user.id
    
    # Check if user is allowed
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("❌ Unauthorized user!")
        return
    
    # Initialize user session
    user_sessions[user_id] = {'step': 'signal_type'}
    
    # Send welcome messages
    await update.message.reply_text("🤖 Welcome to Random Signal Generator Bot!")
    await asyncio.sleep(0.5)
    
    await update.message.reply_text("This bot generates trading signals for QUOTEX platform.")
    await asyncio.sleep(0.5)
    
    await update.message.reply_text(
        "Please select your preferred signal type:\n\n"
        "1️⃣ CALL Only\n"
        "2️⃣ PUT Only\n"
        "3️⃣ BOTH (CALL & PUT)\n\n"
        "Send a number (1, 2, or 3):"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    await update.message.reply_text(
        "📚 Help Menu\n\n"
        "Available Commands:\n"
        "/start - Start generating signals\n"
        "/help - Show this help menu\n"
        "/cancel - Cancel current operation\n\n"
        "How to use:\n"
        "1. Send /start\n"
        "2. Follow the step-by-step instructions\n"
        "3. Get your signals!"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel command handler"""
    user_id = update.effective_user.id
    
    if user_id in user_sessions:
        del user_sessions[user_id]
        await update.message.reply_text("❌ Operation cancelled.\n\nSend /start to begin again.")
    else:
        await update.message.reply_text("No active operation to cancel.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user_id = update.effective_user.id
    
    # Check if user is allowed
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("❌ Unauthorized user!")
        return
    
    # Check if user has active session
    if user_id not in user_sessions:
        await update.message.reply_text("Please send /start to begin.")
        return
    
    session = user_sessions[user_id]
    user_input = update.message.text.strip()
    
    # Handle based on current step
    if session['step'] == 'signal_type':
        if user_input in ['1', '2', '3']:
            signal_type = int(user_input)
            session['signal_type'] = signal_type
            session['step'] = 'strategy'
            
            await update.message.reply_text(f"✅ Selected: {SIGNAL_TYPES[signal_type]}")
            await asyncio.sleep(0.5)
            
            await update.message.reply_text(
                "Now, select your trading strategy:\n\n"
                "1️⃣ Strategy 1 - Conservative\n"
                "2️⃣ Strategy 2 - Moderate\n"
                "3️⃣ Strategy 3 - Aggressive\n"
                "4️⃣ Strategy 4 - Balanced\n"
                "5️⃣ Strategy 5 - High Frequency\n\n"
                "Send a number (1-5):"
            )
        else:
            await update.message.reply_text("❌ Invalid input. Please send 1, 2, or 3.")
    
    elif session['step'] == 'strategy':
        if user_input in ['1', '2', '3', '4', '5']:
            strategy = int(user_input)
            session['strategy'] = strategy
            session['step'] = 'day'
            
            await update.message.reply_text(f"✅ Selected Strategy: {STRATEGIES[strategy]}")
            await asyncio.sleep(0.5)
            
            await update.message.reply_text(
                "Select analysis day (how many days ago):\n\n"
                "0️⃣ = Today\n"
                "1️⃣ = Yesterday\n"
                "2️⃣ = 2 days ago\n\n"
                "Enter a number (0-30):"
            )
        else:
            await update.message.reply_text("❌ Invalid input. Please send a number between 1-5.")
    
    elif session['step'] == 'day':
        if user_input.isdigit() and 0 <= int(user_input) <= 30:
            days_ago = int(user_input)
            session['days_ago'] = days_ago
            session['step'] = 'start_time'
            
            # Calculate date
            analysis_date = datetime.now() - timedelta(days=days_ago)
            date_str = analysis_date.strftime("%Y-%m-%d")
            day_label = "Today" if days_ago == 0 else f"{days_ago} day(s) ago"
            
            session['analysis_date'] = date_str
            
            await update.message.reply_text(f"✅ Analysis day selected: {date_str} ({day_label})")
            await asyncio.sleep(0.5)
            
            await update.message.reply_text(
                "⏰ Set Signal Time Range (UTC+6)\n\n"
                "Enter START time in 24-hour format:\n"
                "Example: 09:00\n\n"
                "Send start time:"
            )
        else:
            await update.message.reply_text("❌ Invalid input. Please send a number between 0-30.")
    
    elif session['step'] == 'start_time':
        # Validate time format
        try:
            time_parts = user_input.split(':')
            if len(time_parts) != 2:
                raise ValueError
            hour, minute = int(time_parts[0]), int(time_parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            
            session['start_time'] = user_input
            session['step'] = 'end_time'
            
            await update.message.reply_text(f"✅ Start time set: {user_input}")
            await asyncio.sleep(0.5)
            
            await update.message.reply_text(
                "Enter END time in 24-hour format:\n"
                "Example: 23:00\n\n"
                "Send end time:"
            )
        except:
            await update.message.reply_text("❌ Invalid time format. Please use HH:MM format (e.g., 18:00)")
    
    elif session['step'] == 'end_time':
        # Validate time format
        try:
            time_parts = user_input.split(':')
            if len(time_parts) != 2:
                raise ValueError
            hour, minute = int(time_parts[0]), int(time_parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            
            session['end_time'] = user_input
            
            # Check if end time is after start time
            start_h, start_m = map(int, session['start_time'].split(':'))
            end_h, end_m = map(int, user_input.split(':'))
            
            if (end_h * 60 + end_m) <= (start_h * 60 + start_m):
                await update.message.reply_text("❌ End time must be after start time. Please try again:")
                return
            
            await update.message.reply_text(f"✅ Time range set: {session['start_time']} to {user_input}")
            await asyncio.sleep(0.5)
            
            await update.message.reply_text("⏳ Generating signals... Please wait...")
            await asyncio.sleep(2)
            
            # Generate signals
            signals = generate_random_signals(
                session['signal_type'],
                session['start_time'],
                session['end_time'],
                session['strategy']
            )
            
            # Format date
            date_obj = datetime.strptime(session['analysis_date'], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d/%m/%Y")
            
            # Build signal message
            signal_lines = []
            for time_str, sig_type in signals:
                signal_lines.append(f"𝙱𝚁𝙻𝚄𝚂𝙳 𝙾𝚃𝙲, {time_str} 𝙼𝟷 {sig_type}")
            
            signal_message = (
                "𒆜•--❎ 𝗙𝗜𝗡𝗔𝗟 ⋅◈⋅ SIGNAL ❎--•𒆜\n"
                "━━━━━━━━━・━━━━━━━━━\n"
                f"📆            {formatted_date}          📆\n"
                "━━━━━━━━━・━━━━━━━━━\n"
                "𝚂𝙸𝙶𝙽𝙰𝙻          𝙵𝙾𝚁       𝚀𝚄𝙾𝚃𝙴𝚇\n"
                f"{chr(10).join(signal_lines)}\n"
                "━━━━━━━━━・━━━━━━━━━\n"
                "❗️ AVOID SIGNAL AFTER BIG CANDLE,\n"
                "❗️ DOJI, BELOW 80% & GAP\n"
                "━━━━━━━━━・━━━━━━━━━\n"
                "❤️•-------‼️ B╎K╎P ‼️-------•❤️"
            )
            
            await update.message.reply_text(signal_message)
            await asyncio.sleep(0.5)
            
            # Generate and send statistics
            accuracy, win_loss, profit_factor = generate_statistics()
            
            stats_message = (
                "━━━━━━━━━・━━━━━━━━━\n"
                f"Signal Accuracy: {accuracy}%\n"
                f"Win/Loss Ratio: {win_loss}\n"
                f"Profit Factor: {profit_factor}\n"
                "━━━━━━━━━・━━━━━━━━━\n"
                "❤️•-------‼️ B╎K╎P ‼️-------•❤️"
            )
            
            await update.message.reply_text(stats_message)
            await asyncio.sleep(0.5)
            
            await update.message.reply_text("💡 Want to generate new signals? Send /start")
            
            # Clear session
            del user_sessions[user_id]
            
        except:
            await update.message.reply_text("❌ Invalid time format. Please use HH:MM format (e.g., 23:00)")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Exception while handling an update: {context.error}")


def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Bot is running... Press Ctrl+C to stop.")
    application.run_polling()


if __name__ == '__main__':
    main()
