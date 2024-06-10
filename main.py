import discord
import deepl
#from googletrans import Translator, LANGUAGES
import os
import re

def remove_custom_emojis(text):
    # Pattern to match custom Discord emojis: <:name:id>
    custom_emoji_pattern = re.compile(r'<[^:]*:[^:]+:\d+>')
    # Pattern to match Unicode emojis

    # Remove custom Discord emojis
    text = custom_emoji_pattern.sub('', text)
    # Remove Unicode emojis
    return text

def translate(clean_text):
    translated_sentences = []
    #for lang in language_table:
    for lang in language_table_deepl:  
        #print(translated_text)
        #tmp = translator.translate(clean_text, dest=lang).text
        tmp = translator.translate_text(clean_text, target_lang=lang).text

        if (tmp != clean_text) and (tmp not in translated_sentences):

            translated_sentences.append(tmp)
            
    
    translated_text = "\n".join(translated_sentences)
    return translated_text

def preprocessing(content):
    clean_text = remove_custom_emojis(content)
    return clean_text

auth_key = "4f689c4c-1231-4c4b-956c-0c41f55626a0:fx"  # Replace with your key
translator = deepl.Translator(auth_key)

# Initialize translator
#translator = Translator(service_urls=['translate.googleapis.com'])
#translator = Translator()

role_language_table = {"Chinese": "zh-cn", "English": "en", "Japanese": "ja"}
language_table = ["zh-cn", "en", "ja"]
language_table_deepl = ["ZH", "EN-US", "JA"]
# Create discord client

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
TOKEN = os.getenv('DISCORD_TOKEN')

stored_replies = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

@client.event
async def on_message(message):
    # Avoid the bot replying to itself
    if message.author == client.user or message.author.bot:
        return
    if message.stickers:
        return
    
    clean_text = preprocessing(message.clean_content)
    #clean_text = remove_custom_emojis(message.clean_content)
    print(message.clean_content)
    print(clean_text)

    if not clean_text:
        return
    
    # Determine the target language from the user's roles
    # This assumes that role names are named exactly like language names in English (case-sensitive)
    #target_lang = []
    # for role in message.author.roles:
    #     if role.name in role_language_table.keys():
    #         target_lang.append(role_language_table[role.name])
            

    # # Default language if no valid role is found
    # if not target_lang:
    #     target_lang = ['en']  # default to English or any other default
    
    # Translate the message
    #translated_text = ""
    translated_text = translate(clean_text)
    
    # Send the translated message
    if not translated_text:
        return
    
    #await message.channel.send(translated_text)
    reply = await message.reply(translated_text, mention_author=False)

    stored_replies[message.id] = reply.id
    #print(stored_replies[message.id])

@client.event
async def on_message_delete(message):
    # Check if the deleted message had a reply from the bot
    #print("detected")
    if message.id in stored_replies.keys():
        # Retrieve the reply message ID and delete it
        reply_id = stored_replies[message.id]
        reply_message = await message.channel.fetch_message(reply_id)
        print(f"Delete: {reply_id}, {reply_message}")
        await reply_message.delete() 
        stored_replies.pop(message.id)

@client.event
async def on_message_edit(before, after):
    print("change detected!")
    print(before.id, after.id)

    # Check if there's a stored reply for the edited message
    if before.id in stored_replies.keys():
        
        reply_id = stored_replies[before.id]
        reply_message = await before.channel.fetch_message(reply_id)
        # Modify the reply based on the new content of the original message

        clean_text = preprocessing(after.clean_content)
        new_reply_content = translate(clean_text)

        stored_replies.pop(before.id)

        if clean_text and new_reply_content:  
            # Edit the reply message
            await reply_message.edit(content=new_reply_content)
            stored_replies[after.id] = reply_id
        else:
            await reply_message.delete() 

# Replace 'your_token_here' with your bot's token
client.run(TOKEN)
