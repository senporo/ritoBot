import discord
from discord.ext import commands
import os
from riotwatcher import TftWatcher, LolWatcher, ValWatcher, ApiError
import requests
from keep_alive import keep_alive

#allow intents for discord to access everything
intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

#initialize
riotKey_LOL = os.environ['apiKey']
riotKey_TFT = os.environ['apiKey_TFT']
lol_watcher = LolWatcher(riotKey_LOL)
tft_watcher = TftWatcher(riotKey_TFT)

region = 'na1'
summoner = 'superfeetlicker'

cmds = {"rank(arank/trank) [summoner name]":"gets summoner rank",
        "stats(astats/tstats) [summoner name]":"gets summoner stats",
        "profile [summoner name]":"gets summoner profile overview",
        "match [summoner name]" : "gets past 10 games played(arena/rift)"
}

BOT_FLAG = '!'
TFT_FLAG = 't'
ARENA_FLAG = 'a'
RANK = "rank"
STATS = "stats"
PROFILE = "profile"
MATCH = "match"

#bot is on
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


#Return Match History (Past 10)
def get_match_history(summoner):
  lol_summoner = lol_watcher.summoner.by_name(region, summoner)
  match_list = lol_watcher.match.matchlist_by_puuid(region, lol_summoner['puuid'])
  count = 0
  history = ""
  for matches in match_list:
    if count > 9: #iterate 10 times
      break
    match_data = lol_watcher.match.by_id(region, match_list[count])
    person_index = match_data['metadata']['participants'].index(lol_summoner['puuid'])
    win = match_data['info']['participants'][person_index]['win']
    champion_name = match_data['info']['participants'][person_index]['championName']
    gamemode = match_data['info']['gameMode']
    if win == True:
      win = "Win"
    else:
      win = "Loss"
    if gamemode == 'CHERRY':
      gamemode = 'ARENA'
    game_stats = (gamemode.title() + " " + win + " " + champion_name)
    history += game_stats
    history += "\n"
    count += 1 
  return history

#Return Tft Match History (Past 10)
def get_tft_match_history(summoner):
  tft_summoner = tft_watcher.summoner.by_name(region, summoner)
  match_list = tft_watcher.match.by_puuid(region, tft_summoner['puuid'])
  count = 0
  history = ""
  for matches in match_list:
    if count > 9:
      break
    match_data = tft_watcher.match.by_id(region, match_list[count])
    person_index = match_data['metadata']['participants'].index(tft_summoner['puuid'])
    placement = match_data['info']['participants'][person_index]['placement']
    history += str(placement)
    history += "\n"
    count += 1
  return history
  
#LEAGUE
#------------------------------------------------#
# get league rank
def get_rank(summoner):
  lol_summoner = lol_watcher.summoner.by_name(region, summoner)
  ranked_stats = lol_watcher.league.by_summoner(region, lol_summoner['id'])
  if (len(ranked_stats) > 1):
        return str(ranked_stats[1]['tier']) + " " + str(ranked_stats[1]['rank']) + " " +str(ranked_stats[1]['leaguePoints']) + "lp"
  else:
      return "No Solo Q Ranked"


#get league stats
def get_stats(summoner):
  lol_summoner = lol_watcher.summoner.by_name(region, summoner)
  ranked_stats = lol_watcher.league.by_summoner(region, lol_summoner['id'])
  if (len(ranked_stats) > 1):
    return str(ranked_stats[1]['wins']) + " Wins " + str(ranked_stats[1]['losses']) + " Losses "
  else:
    return "No Solo Q Stats"

#TFT
#------------------------------------------------#
# get tft rank
def get_tft_rank(summoner):
  tft_summoner = tft_watcher.summoner.by_name(region, summoner)
  ranked_stats = tft_watcher.league.by_summoner(region, tft_summoner['id'])
  if('tier' in ranked_stats[0]):
    return ranked_stats[0]['tier'] + " " + ranked_stats[0]['rank'] + " " +     str(ranked_stats[0]['leaguePoints']) + " " + "lp"
  else:
    return ranked_stats[1]['tier'] + " " + ranked_stats[1]['rank'] + " " +     str(ranked_stats[1]['leaguePoints']) + " " + "lp"

#get tft stats
def get_tft_stats(summoner):
  tft_summoner = tft_watcher.summoner.by_name(region, summoner)
  ranked_stats = tft_watcher.league.by_summoner(region, tft_summoner['id'])
  if('tier' in ranked_stats[0]):
    win = ranked_stats[0]['wins']
    loss = ranked_stats[0]['losses']
  else:
    win = ranked_stats[1]['wins']
    loss = ranked_stats[1]['losses']
  return (str(win) + " Wins " + str(loss) + " losses")
#------------------------------------------------# 

#ARENA
#------------------------------------------------#
#get arena rank
def get_arena_rank(summoner):
  lol_summoner = lol_watcher.summoner.by_name(region, summoner)
  ranked_stats = lol_watcher.league.by_summoner(region, lol_summoner['id'])
  return str(ranked_stats[0]['wins']) + " Wins " + "And " + str(ranked_stats[0]['losses']) + " Losses" + " In Arena"
#------------------------------------------------#


@bot.command()
async def rank(ctx, summoner_name):
  await ctx.send(get_rank(summoner_name))

@client.event
async def on_message(message):
  if message.author == client.user:  #no bot recursion
    return

  # BOT COMMAND
  if message.content.startswith(BOT_FLAG):
    msg = message.content[1:]

  #Command List
    if msg.startswith("commands"):
      result = ""
      for key, value in cmds.items():
        result += "!" + key + " - " + value + "\n"
      await message.channel.send(result)

  #Match History
    elif msg.startswith(MATCH):
      summoner = msg[len(MATCH):]
      await message.channel.send(get_match_history(summoner))
    
  # TFT COMMAND
    elif msg.startswith(TFT_FLAG):
      msg = msg[1:]
      
      # RANK
      if msg.startswith(RANK):
        summoner = msg[len(RANK):]
        await message.channel.send(get_tft_rank(summoner))

      #stats
      if msg.startswith(STATS):
        summoner = msg[len(STATS):]
        await message.channel.send(get_tft_stats(summoner))

      if msg.startswith(MATCH):
        summoner = msg[len(MATCH):]
        await message.channel.send(get_tft_match_history(summoner))
        
    #Arena Command
    elif msg.startswith(ARENA_FLAG):
      msg = msg[1:]
      summoner = msg[len(RANK):]
      await message.channel.send(get_arena_rank(summoner))

    #Profile Command
    elif msg.startswith(PROFILE):
      msg = msg[1:]
      summoner = msg[len(PROFILE):]
      await message.channel.send(summoner + " is a noob")
    
    # LOL COMMAND
    else:
      # RANK
      if msg.startswith(RANK):
        summoner = msg[len(RANK):]
        await message.channel.send(get_rank(summoner)) 
      if msg.startswith(STATS):
        summoner = msg[len(STATS):]
        await message.channel.send(get_stats(summoner))



#run bot
keep_alive()
client.run(os.environ['KEY'])
bot.run(os.environ['KEY'])
