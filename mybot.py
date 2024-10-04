import os
import telebot
from huggingface_hub import InferenceClient

# Load environment variables
# Initialize Hugging Face Inference Client
HF_API_KEY = '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'
 # Alternatively, you can directly input your key here
client = InferenceClient(api_key=HF_API_KEY)

# Initialize the Telebot bot
TELEGRAM_TOKEN = '6386305705:AAHVS-jp6s2EE8N23Oj4aFcm02E05T87Vhc'
# Alternatively, you can directly input your Telegram token
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Conversation history dictionary to store user messages and AI responses
conversation_history = {}

# Function to interact with Hugging Face API
def chat_with_ai(user_message, conversation_id):
    if conversation_id in conversation_history:
        # If conversation exists, append new message to the history
        conversation_history[conversation_id].append({"role": "user", "content": user_message})
    else:
        # If conversation doesn't exist, create a new one
        conversation_history[conversation_id] = [{"role": "system", "content": "Answer neatly with full of emotions and if it is related to programming make it understandable."}]
        conversation_history[conversation_id].append({"role": "user", "content": user_message})

    output = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=conversation_history[conversation_id],
        stream=True,
        temperature=0.5,
        max_tokens=1024,
        top_p=0.7
    )
    response = ""
    for chunk in output:
        response += chunk.choices[0].delta.content

    # Store AI response in conversation history
    conversation_history[conversation_id].append({"role": "assistant", "content": response})

    return response

# Handler for /chat command
@bot.message_handler(commands=['chat'])
def handle_chat(message):
    user_message = message.text[len('/chat '):]  # Extract the text after /chat
    if not user_message:
        bot.reply_to(message, "Please provide a message after the /chat command.")
        return

    conversation_id = message.chat.id
    bot.reply_to(message, "Let me think...")  # Acknowledge message

    # Get AI-generated response from Hugging Face
    ai_response = chat_with_ai(user_message, conversation_id)
    bot.reply_to(message, ai_response)

# Handler for messages that are replies to the bot's previous messages
@bot.message_handler(content_types=['text'])
def handle_reply(message):
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
        conversation_id = message.chat.id
        user_message = message.text
        ai_response = chat_with_ai(user_message, conversation_id)
        bot.reply_to(message, ai_response)

# Start the bot
if __name__ == '__main__':
    # Increase the timeout here
    bot.polling(none_stop=True, interval=0, timeout=30)  # Default is 15 seconds