import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define states for conversation
NAME, PHONE, EMAIL, SPECIALIST, CONFIRMATION = range(5)

# Dictionary to store user data temporarily
user_data = {}

# Start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the Hospital Appointment Bot! Please enter your name.")
    return NAME

# Function to save user data and ask for the next piece of information
def collect_info(update: Update, context: CallbackContext):
    text = update.message.text
    user_data[context.user_data['state']] = text
    if context.user_data['state'] == NAME:
        update.message.reply_text("Great! Now, please enter your phone number.")
        return PHONE
    elif context.user_data['state'] == PHONE:
        update.message.reply_text("Thanks! Please enter your email address.")
        return EMAIL
    elif context.user_data['state'] == EMAIL:
        update.message.reply_text("Please select a specialist:")
        # You can provide a list of specialists here
        keyboard = [['Cardiologist', 'Dermatologist'], ['Neurologist', 'Other']]
        reply_markup = {'keyboard': keyboard, 'one_time_keyboard': True, 'resize_keyboard': True}
        context.user_data['specialist_keyboard'] = reply_markup
        update.message.reply_text("Please select a specialist:", reply_markup=reply_markup)
        return SPECIALIST

# Function to handle specialist selection
def select_specialist(update: Update, context: CallbackContext):
    user_data[context.user_data['state']] = update.message.text
    update.message.reply_text("You selected " + user_data[SPECIALIST] + ". Is this correct? (yes/no)")
    return CONFIRMATION

# Function to confirm and end the conversation
def confirm(update: Update, context: CallbackContext):
    if update.message.text.lower() == 'yes':
        # Save the appointment details in a database
        # You can also generate a queue number and save it here
        update.message.reply_text("Your appointment is confirmed. Your queue number is #123.")
    else:
        update.message.reply_text("Appointment not confirmed. Please start over if you want to book an appointment.")
    
    # End the conversation
    return ConversationHandler.END

def main():
    # Create the Updater and pass your bot's token
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, collect_info)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, collect_info)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, collect_info)],
            SPECIALIST: [MessageHandler(Filters.text & ~Filters.command, select_specialist)],
            CONFIRMATION: [MessageHandler(Filters.text & ~Filters.command, confirm)],
        },
        fallbacks=[],
        allow_reentry=True
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
