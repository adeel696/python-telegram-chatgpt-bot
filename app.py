import re
from flask import Flask, request
import telegram
from openai import OpenAI
from telegrambot.credentials import tbot_token, tbot_user_name, chat_gpt_key, BotURL

 
global bot
global TOKEN
global CHATGPTKEY
CHATGPTKEY = chat_gpt_key
TOKEN = tbot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

client = OpenAI(
        api_key=CHATGPTKEY,
    )

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
   # Telegram JSON object
   update = telegram.Update.de_json(request.get_json(force=True), bot)

   chat_id = update.message.chat.id
   msg_id = update.message.message_id

   # Encode text for unicode compatibility
   text = update.message.text.encode('utf-8').decode()
   # text
   print("Received message :", text)
   
   #First Message
   if text == "/start":
       # print the welcoming message
       bot_welcome = """
       Welcome to chat GPT bot.
       """
       # send the welcoming message
       bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)

   else:
       try:
           #Get Response from chat GPT
           chatGPTReply = chat_gpt(text)
           #Send Chat GPT Response
           bot.sendMessage(chat_id=chat_id, text=chatGPTReply, reply_to_message_id=msg_id)
       except Exception:
           # if things went wrong
           bot.sendMessage(chat_id=chat_id, text="Error: Please try again", reply_to_message_id=msg_id)

   return 'ok'

#Call this url once for telegram webhook 
@app.route('/telegram_webhook', methods=['GET', 'POST'])
def set_webhook():
   s = bot.setWebhook('{URL}{HOOK}'.format(URL=BotURL, HOOK=TOKEN))
   if s:
       return "webhook setup ok"
   else:
       return "webhook setup failed"

@app.route('/')
def index():
   return ''

#Query from chatGPT using chatGPT API
def chat_gpt(message):
  messages = [ {"role": "system", "content":"" } ] 
  messages.append(
         {"role": "user", "content": message},
    )
  
  chat = client.chat.completions.create( 
    messages=messages ,
    model="gpt-3.5-turbo"
    ) 
  reply = chat.choices[0].message.content 

  return reply


if __name__ == '__main__':
   app.run(threaded=True)
