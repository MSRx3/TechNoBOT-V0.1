import os
from time import sleep
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from keep_alive import keep_alive
from dotenv import load_dotenv
from discord.utils import get
import pickle
from chatterbot import ChatBot
from os import path
import asyncio

chatbot = ChatBot('RT')
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
Botlog = 0
if path.exists('logchannel.db') == True:
  Botlog = pickle.load(open('logchannel.db', 'rb'))

bot = discord.Client()

print('connecting')

bot = commands.Bot(command_prefix = '/')

messagelist = [] 

#On ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} is connected to Discord.')
    global amounts
    global chatbot
    global settingdict
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="THIS SERVER"))

@bot.command(name='msg_count', help = 'Test command from StackOverflow')
async def message_count(ctx, channel: discord.TextChannel=None):
  channel = channel or ctx.channel
  await ctx.send(f'Getting number of messages in {channel.mention}, this may take a while')
  count = 0
  async for _ in channel.history(limit=None):
    count += 1
  await ctx.send("There were {} messages in {}".format(count, channel.mention))


#-------------------------------------------------------------------------------------------------------------
#MODERATION-----------------
async def log(event):
  channel = bot.get_channel(Botlog)
  await channel.send(str(event))
#Warnings
@bot.command(name = 'warn', help = 'Warns a member. Please mention the user')
@has_permissions(administrator = True)
async def warn(ctx, user, *, reason=None):
  if user == None:
    await ctx.send('You have not specified a user. Did you mention the user? You also need a reason.')
  else:
    await ctx.send(user + ' has been warned for ' + reason)
    warnings = []
    if path.exists(user + '.db') == True:
      warnings = pickle.load(open(user + '.db', 'rb'))
    else:
      pickle.dump(warnings, open(user + '.db', 'ab'))
    warnings.append(reason)
    pickle.dump(warnings, open(user + '.db', 'wb'))
    await log(f'Warned {user} for {reason}')

@bot.command(name = 'warnings', help = 'Views if someone has warnings')
@has_permissions(administrator = True)
async def warnings(ctx, user):
  warnings = []
  if path.exists(user + '.db') == True:
    warnings = pickle.load(open(user + '.db', 'rb'))
    print(warnings)
    for i in range (len(warnings)):
      await ctx.send(str(i+1) + '. ' + warnings[i])
  if warnings == []:
    await ctx.send('No warnings for this user.')
@warnings.error
async def warnings_error(ctx, error):
  await ctx.send('There is an error with the *warnings command for this user: %s' % error)
  
@bot.command(name = 'removewarn', help = 'Removes a warning for someone. Please use the place number of the warning.')
async def removewarn(ctx, user, warn_num):
  if path.exists(user + '.db') == True:
    warnings = []
    warnings = pickle.load(open(user + '.db', 'rb'))
    warnings.pop(int(warn_num) - 1)
    pickle.dump(warnings, open(user + '.db', 'wb'))
    await ctx.send('Sucess!')
    await log('Warning removed from ' + user)

@bot.command(name = 'clear', help = 'clears stuff')
@has_permissions(administrator = True)
async def purge(ctx, *, amount=0):
  try:
    user = ctx.author
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'{user.mention} cleared {amount} messages')
    asyncio.sleep(5)
    await ctx.channel.purge (limit=2)
  except commands.MissingPermissions:
    await ctx.send(f"{user.mention} You don't have the permission to run this command")

#Botlog
@bot.command(name = 'setbotlog', help = 'Sets a bot log using the channel id')
@has_permissions(administrator = True)
async def setbotlog(ctx, channelid):
  Botlog = channelid
  pickle.dump(Botlog, open('logchannel.db', 'ab'))

#Mute
@bot.command(name = 'mute', help = "Mute someone.")
@has_permissions(administrator = True)
async def mute(ctx, user: discord.Member):
  try:
    role = get(ctx.guild.roles, name="Muted") 
    await user.add_roles(role)
    await ctx.send(f'{user.mention} has been muted.')
  except commands.MissingPermissions:
    await ctx.send("You are missing the permissions to run this command")

#Unmute
@bot.command(name = 'unmute', help = "Unmute someone.")
@has_permissions(administrator = True)
async def unmute(ctx, user: discord.Member):
  try:
    role = get(ctx.guild.roles, name="Muted") 
    if role in user.roles:
      await user.remove_roles(role)
      await ctx.send(f'{user.mention} has been unmuted.')
    else:
      await ctx.send(f'{user.mention} is not currently muted')
  except commands.MissingPermissions:
    await ctx.send("You are missing permissions to run this command")
  
@bot.command(name = 'kick', help = 'kicks people')
@has_permissions(administrator=True)
async def kick (ctx, member : discord.Member,  *, reason=None):
  try:
   await member.kick(reason=reason)
   await ctx.send(f'{member.mention} is kicked')
   await member.send(f"You've been kicked from TechNo1Geeks sever Reason: {reason}")
  except commands.MissingPermissions:
   await ctx.send("You are missing permissions to run this command")
   
@bot.command(name = 'ban', help = 'bans people')
@has_permissions(administrator=True)
async def ban (ctx, member : discord.Member, *, reason=None):
  try:
   await member.ban (reason=reason)
   await ctx.send(f'{member.mention} has been banned')
  except commands.MissingPermissions:
   await ctx.send ("You are missing permissions to run this command")

@bot.command(name = 'tempmute', help = "Muted someone for 10min.")
@has_permissions(administrator = True)
async def tempmute(ctx, user: discord.Member):
  try:
   role = get(ctx.guild.roles, name="Muted") 
   await user.add_roles(role)
   await ctx.send(f'{user.mention} has been muted for 10min.')
   await asyncio.sleep(600)
   await user.remove_roles(role)
   await ctx.send(f'{user.mention} has been unmuted')
  except commands.MissingPermissions:
    await ctx.send("You are missing permissions to run this command")

@bot.command(name="say")
async def say(ctx,*, message):
  await ctx.channel.purge(limit=1)
  await ctx.send(message)
  print (message)

@bot.command(name = 'give')
async def give(ctx, *, role: discord.Role):
    await ctx.channel.purge(limit=1)
    user=ctx.message.author
    role = get(ctx.guild.roles, name=role.name)
    await user.add_roles(role)

@bot.command(name = 'rem')
async def rem(ctx, *, role: discord.Role):
    await ctx.channel.purge(limit=1)
    user=ctx.message.author
    role = get(ctx.guild.roles, name=role.name)
    await user.remove_roles(role)

'''@bot.command(name = "get_user")
async def get_user(ctx, *, user: discord.Member, amount=discord.get_user):
  await ctx.server.get_user(amount)
  await ctx.send(f"There are {user} users in this server")'''

'''@bot.event
async def on_message(message):
  if message.content.count ("<@633966483579469835>"):
    await message.channel.purge(limit=1)
    await message.channel.send(f"{message.member.mention} Pining the owner is not allowed in this server")'''

@bot.command(name="edit", help="test edit command")
async def edit(ctx, user1, user2, user3):
    user=ctx.author 
    await ctx.channel.purge(limit=1)
    message = await ctx.send(f"``` {user1}```")
    await asyncio.sleep(1)
    await message.edit(content=f"``` {user1} +```")
    await asyncio.sleep(1)
    await message.edit(content=f"``` {user1} + {user2}```")
    await asyncio.sleep(1)
    await message.edit(content=f"``` {user1} + {user2} = ```")
    await asyncio.sleep(1)
    await message.edit(content=f"``` {user1} + {user2} = {user3}```")
    await asyncio.sleep(1)
    await message.add_react("😀")

@bot.command(name="stfu")
async def stfu(ctx):
  await ctx.send("https://www.youtube.com/watch?v=KRB-iHGHSqk")

keep_alive()
bot.run(TOKEN)
