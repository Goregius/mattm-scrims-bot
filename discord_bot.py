from discord.ext.commands import Bot
from discord import Game
import discord
import asyncio
import random
import google_io
import time
from bot_token import TOKEN
from channel_ids import publicScrimsID, loughScrimsID, adminID


class RL_Game:
    def __init__(self,players,channel_id,mode):
        self.players = players
        self.channel_id = channel_id
        if mode == "r":  
            self.teams = self.createRandomTeams(players)
        self.time = time.time()

    def createRandomTeams(self,players):
        Blue = []
        Orange = []
        players = self.players
        for i in range(5, 2, -1):
            x = random.randint(0, i)
            player = players[x]
            Blue.append(player)
            players.remove(player)
        for i in range(2, -1, -1):
            player = players[i]
            Orange.append(player)
            players.remove(player)
        return [Blue, Orange]
    
    def isInactive(self):
        if time.time() - self.time >7200: #if game active for longer than 2hours
            return True
        return False
    
class Lough_RL_Game(RL_Game):
    def __init__(self,players,channel_id,mode):
        super().__init__(players,channel_id,mode)
        
        
class Queue:
    def __init__(self,channel_id):
        self.gameQueue = []
        self.channel_id = channel_id
    def queue(self,player):
        if player not in self.gameQueue:
            if len(self.gameQueue) <= 5:
                self.gameQueue.append(player)
                return True
            else:
                return("Full")
        else:
            return False
        
    def leave(self,player):
        if player in self.gameQueue:
            self.gameQueue.remove(player)
            return True
        else:
            return False

    def status(self):
        msg = "Current players in the queue "
        for i in self.gameQueue:
            msg += (str(i)[0:-5]+", ")  # discord names
        return msg

    def kickPlayer(self, player):
        for i in range(len(self.gameQueue)):
            queuer = self.gameQueue[i]
            if player == queuer:
                del self.gameQueue[i]
                return True

#loughScrimsID = "491408697168494630" #test
#publicScrimsID = "491408712574173214" #test2
loughGameQueue = Queue(loughScrimsID)
publicGameQueue = Queue(publicScrimsID)

Queues = [loughGameQueue,publicGameQueue]
ActiveQueues = []
for i in range(len(Queues)):
    ActiveQueues.append(Queue(Queues[i].channel_id))

    
#Queues[0].gameQueue = ["a#5674","B#4483","c#5478","D#5487","e#7845"] #test queues
#Queues[1].gameQueue = ["a#5674","B#4483","c#5478","D#5487","e#7845"] #test queues


BOT_PREFIX = ("!")
games = []
client = Bot(command_prefix=BOT_PREFIX)


@client.command(name="hello",
                description="says hello",
                brief="says hello",
                aliases=["hi", "hey", "howdy", "bonjour", "hola"],
                pass_context=True)
async def hello(context):
    msg = 'Hello '+context.message.author.mention
    await client.say(msg)

####-----------------------------------------QUEUE COMMANDS------------------------------------------------------

    
@client.command(name="queue",
                description="adds you to the queue",
                brief="adds you to the queue",
                aliases=["q", "Q"],
                pass_context=True)
async def queue(context):
    msg=""
    for q in Queues:
        if context.message.channel.id == q.channel_id:
            qStatus =q.queue(context.message.author)
            if qStatus==True:
                msg = ("You have been added to the queue "+context.message.author.mention+".\nThere are currently "+str(len(q.gameQueue))+" players in the queue.")
            elif not qStatus:
                msg = ("Already in queue "+context.message.author.mention)
            if len(q.gameQueue)==6:
                #set q to active queue when full
                for q2 in ActiveQueues:
                    if q2.channel_id == q.channel_id:
                        q2.gameQueue = q.gameQueue
                        q.gameQueue = []
                        break
                msg += "\nGame Starting! Pick an option to create teams (!b !r !c)"
    if msg=="":
        msg = "this is a test server (queue msg)"
    await client.say(msg)



    
@client.command(name="leave",
                description="removes you from the queue",
                brief="removes you from the queue",
                aliases=["l","L"],
                pass_context=True)
async def leave(context):
    msg = ""
    for q in Queues:
        if context.message.channel.id == q.channel_id: 
            if q.leave(context.message.author):
                msg = "You have been removed from the queue "+context.message.author.mention+".\nThere are currently "+str(len(q.gameQueue))+" players in the queue"
            else:
                msg  = "You are not in the queue "+context.message.author.mention
            break
    if msg == "":
        msg = "this is a test server"
    await client.say(msg)


@client.command(name="status",
                description="gets status of queue",
                brief="gets status of queue",
                aliases=["s", "S"],
                pass_context=True)
async def status(context):
    msg = ""
    for q in Queues:
        if context.message.channel.id == q.channel_id:
            if len(q.gameQueue)==0:
                msg = "Queue currently empty"
            else:
                msg = "Current players in the queue: "
                for player in range(len(q.gameQueue)-1):
                    msg += (str(q.gameQueue[player])[:-5]+", ")  # discord names
                msg+=str(q.gameQueue[-1])[:-5]
                break
    if msg == "":
        msg = "this is a test server"
    await client.say(msg)
#---------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------ActiveGames---------------------------------------------------------------------------
@client.command(name="random",
                description="randomises teams when queue is full !r",
                brief="Decides how to organise teams",
                aliases=["r","R"],
                pass_context=True)
async def randomTeams(context):
    for q in range(len(ActiveQueues)):
        if context.message.channel.id == ActiveQueues[q].channel_id and ActiveQueues[q].gameQueue: #find correct queue
            if ActiveQueues[q].channel_id==loughScrimsID:
                newGame = Lough_RL_Game(ActiveQueues[q].gameQueue, ActiveQueues[q].channel_id, "r")
            else:
                newGame = RL_Game(ActiveQueues[q].gameQueue, ActiveQueues[q].channel_id, "r")
            
            ActiveQueues[q].gameQueue=[]
            Blue = newGame.teams[0]
            Orange = newGame.teams[1]
            games.append(newGame)
            channel = discord.Object(id=loughScrimsID)
            msg = "Team A: "+str(Blue[0])+", " + \
                str(Blue[1]) + ", " + str(Blue[2])
            msg += "\nTeam B: "+str(Orange[0])+", " + \
                str(Orange[1]) + ", " + str(Orange[2])
            await client.say(msg)
            return True
    await client.say("No active games found "+context.message.author.mention+".")

        

@client.command(name="captains",
                description="Captains create teams",
                brief="Decides how to organise teams",
                aliases=["c","C"],
                pass_context=True)
async def captains(context):
    pass


@client.command(name="report score",
                description="!report <win/loss> <your score> <opponents score>",
                brief="report score of current match",
                aliases=["report", ],
                pass_context=True)
async def report_score(context, result, score1, score2):
    gamefound = False
    if result in ["win", "loss"]:
        if result == "loss":
            x = score1
            score1 = score2
            score2 = x
        if games:  # if list not empty
            for game in range(len(games)):
                blue = games[game].teams[0]
                orange  = games[game].teams[1]
                if context.message.channel.id==games[game].channel_id:
                    if context.message.author in blue:
                        record = [str(blue[0])[0:-5], str(blue[1])[0:-5], str(blue[2])[0:-5], str(
                            score1), str(score2), str(orange[0])[0:-5], str(orange[1])[0:-5], str(orange[2])[0:-5]]
                        gameFound = True

                    elif context.message.author in orange:
                        record = [str(blue[0])[0:-5], str(blue[1])[0:-5], str(blue[2])[0:-5], str(
                            score2), str(score1), str(orange[0])[0:-5], str(orange[1])[0:-5], str(orange[2])[0:-5]]

                    else:
                        continue
                    gameFound = True
                    gameType = type(games[game])
                    del games[game]
                    break
            if gameFound:
                if gameType is Lough_RL_Game:
                    google_io.addRecord(record)
                msg = context.message.author.mention+" reported the score as: " + \
                    record[0]+", "+record[1]+", "+record[2]+" "+record[3] + \
                    " - "+record[4]+" "+record[5]+", "+record[6]+", "+record[7]
            else:
                msg = "You are not currently in any games "+context.message.author.mention
        else:
            msg = "There are currently no active games"+context.message.author.mention
    else:
        msg = "Unrecognised syntax, try again"
    await client.say(msg)

        
@client.command(name="Delete Active game",
                description="Deletes first game from queue",
                brief="Admin permission",
                aliases=["del"],
                pass_context=True)

async def deleteActiveGame(context):
    for role in context.message.author.roles:
        if role == "Admin":
            for q in range(len(Queue)):
                if Queue[q].channel_id == context.message.channel.id:
                    del Queue[q]
                    await client.say("game removed from the queue" )
#-------------------------------------------------------------------------------------------------------------------------------
@client.command(name="Kick Player",
                description="Removes player from queue ",
                brief="Admin permission",
                aliases=["Kick","kick","remove"],
                pass_context=True)

async def kickPlayer(context, player):
    for role in context.message.author.roles:
        if str(role) == "Admin":
            for q in range(len(Queues)):
                if Queues[q].channel_id == context.message.channel.id:
                    for i in range(len(Queues[q].gameQueue)):
                        queuer = Queues[q].gameQueue[i]
                        if player == queuer or player == str(queuer)[:-5]:
                            del Queues[q].gameQueue[i]
                            await client.say(str(queuer)[:-5]+" removed from the queue.")
                            return True
    print("player not found in the list.")        
    


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="Rocket League"))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')







client.run(TOKEN)
