#!/usr/bin/env python3

import discord
from discord.ext import commands
import random
import minespy
import ttt
import re

def replacenth(string, sub, wanted, n):
	where = [m.start() for m in re.finditer(sub, string)][n-1]
	before = string[:where]
	after = string[where:]
	after = after.replace(sub, wanted, 1)
	new_string = before + after
	return new_string

# read token
with open("tokenfile","r") as tokenfile:
	token = tokenfile.read()

client = commands.Bot(command_prefix="m!")
client.remove_command("help")

helpmsg = discord.Embed(title="Help",description="m!minesweeper: create minefield\nm!ms: alias for minesweeper\nm!roll: roll dice\nm!rps: rock paper scissors\nm!tictactoe: play tic tac toe. controls are wasd; combine them to use corners")
nums = [":zero:",":one:",":two:",":three:",":four:",":five:",":six:",":seven:",":eight:"]

# print message when bot turns on and also print every guild that its in
@client.event
async def on_ready(): 
	print(f"logged in as {client.user}")
	print(f"https://discord.com/oauth2/authorize?client_id={client.user.id}&permissions=8192&scope=bot")
	for guild in client.guilds:
		print(f"In guild: {guild.name}") 
# and also print every time it joins a guild
@client.event
async def on_guild_join(guild):
	print(f"Joined guild: {guild.name}")

@client.command() 
async def minesweeper(ctx, length: int = 6, width: int = 6, mines: int = 7):
	if length * width > 196:
		await ctx.send(embed=discord.Embed(title="Error",description="Board too large. Try something smaller."))
		return
	if mines >= (length * width):
		mines = (length * width) - 1
	gridstr = minespy.generategrid(length,width,mines)
	while "0" in gridstr or "1" in gridstr or "2" in gridstr or "3" in gridstr or "4" in gridstr or "5" in gridstr or "6" in gridstr or "7" in gridstr or "7" in gridstr or "B" in gridstr: # stole this from stackoverflow
		gridstr = gridstr.replace("0","||:zero:||")
		gridstr = gridstr.replace("1","||:one:||")
		gridstr = gridstr.replace("2","||:two:||")
		gridstr = gridstr.replace("3","||:three:||")
		gridstr = gridstr.replace("4","||:four:||")
		gridstr = gridstr.replace("5","||:five:||")
		gridstr = gridstr.replace("6","||:six:||")
		gridstr = gridstr.replace("7","||:seven:||")
		gridstr = gridstr.replace("8","||:eight:||")
		gridstr = gridstr.replace("B","||:boom:||")
	gridstr = replacenth(gridstr,"||:zero:||",":zero:",random.randint(0,gridstr.count("||:zero:||")))
	embed = discord.Embed(title=f"{length}x{width} with {mines} mines",description=gridstr)
	await ctx.send(embed=embed)

@client.command()
async def rps(ctx,member):
	otherguy = ctx.message.mentions[0]
	if ctx.author.dm_channel == None:
		await ctx.author.create_dm()
	if otherguy.dm_channel == None:
		await otherguy.create_dm()
	authormsg = await ctx.author.dm_channel.send("Rock, paper, or scissors?")
	otherguymsg = await otherguy.dm_channel.send("Rock, paper, or scissors?")
	for i in u"\U0001f5ff\U0001f4f0\u2702": # rock/paper/scissors
		await authormsg.add_reaction(i)
		await otherguymsg.add_reaction(i)
	def check(reaction,user):
		return (user.id == ctx.author.id or user.id == otherguy.id) and (reaction.message == authormsg or reaction.message == otherguymsg)
	players = []
	winner = None
	while len(players) < 2:
		reaction,user = await client.wait_for('reaction_add', timeout=None, check=check)
		players.append([reaction,user])
	if str(players[0][0].emoji) == u"\U0001f5ff" and str(players[1][0].emoji) == u"\U0001f4f0": # rock < paper
		winner = players[1][1].name
	elif str(players[0][0].emoji) == u"\U0001f4f0" and str(players[1][0].emoji) == u"\U0001f5ff": # paper > rock
		winner = players[0][1].name
	elif str(players[0][0].emoji) == u"\u2702" and str(players[1][0].emoji) == u"\U0001f4f0":     # paper < scissors
		winner = players[0][1].name
	elif str(players[0][0].emoji) == u"\U0001f4f0" and str(players[1][0].emoji) == u"\u2702":     # scissors > paper
		winner = players[1][1].name
	elif str(players[0][0].emoji) == u"\u2702" and str(players[1][0].emoji) == u"\U0001f5ff":     # scissors < rock
		winner = players[1][1].name
	elif str(players[0][0].emoji) == u"\U0001f5ff" and str(players[1][0].emoji) == u"\u2702":     # rock > scissors
		winner = players[0][1].name
	else:
		description = f"{players[0][0].emoji}   v   {players[1][0].emoji}\n\nIts a tie!"
	if winner != None:
		description = f"{players[0][0].emoji}   v   {players[1][0].emoji}\n\n{winner} wins!"
	title = f"{players[0][1].name} v {players[1][1].name}"
	game_embed = discord.Embed(title=title,description=description)
	await ctx.send(embed=game_embed)
	await otherguy.dm_channel.send(embed=game_embed)
	await ctx.author.dm_channel.send(embed=game_embed)

valid_movements = ['w', 'a', 's', 'd', 'wa', 'wd', 'sa', 'sd', '.','q']

@client.command()
async def tictactoe(ctx,member):
	opponent = ctx.message.mentions[0]
	await ctx.send(f"playing tic tac toe with {opponent.display_name}")
	g = ttt.generategrid()
	gs = g
	for i in gs:
		if str(i) in "123456789":
			gs = gs.replace(i,":blue_square:")
	bmsg = await ctx.send(gs)
	moves = 1
	def check(message):
		user = message.author
		return user == opponent or user == ctx.author
	while moves <= 9:
		m = await client.wait_for('message',timeout=None,check=check)
		c = m.content.lower()
		if c in ["as","ds","aw","dw"]:
			c = c[::-1]
		og = g
		if not c in valid_movements:
			continue
		char = "X" if moves % 2 == 1 else "O"
		if c == "q":
			return
		if c == "wa":
			g = g.replace("1",char)
		elif c == "w":
			g = g.replace("2",char)
		elif c == "wd":
			g = g.replace("3",char)
		elif c == "a":
			g = g.replace("4",char)
		elif c == ".":
			g = g.replace("5",char)
		elif c == "d":
			g = g.replace("6",char)
		elif c == "sa":
			g = g.replace("7",char)
		elif c == "s":
			g = g.replace("8",char)
		elif c == "sd":
			g = g.replace("9",char)
		if og != g:
			moves += 1
		await m.delete()
		gs = g
		gs = gs.replace("X",":regional_indicator_x:")
		gs = gs.replace("O",":zero:")
		for i in gs:
			if str(i) in "123456789":
				gs = gs.replace(i,":blue_square:")
		await bmsg.edit(content=gs)
		glist = []
		for i in g.split("\n"):
			if i == "":
				continue
			gltmp = []
			for j in i:
				gltmp.append(j)
			glist.append(gltmp)
		if ttt.checkWin(glist):
			await ctx.send(f"{ttt.checkWin(glist)} has won!")
			return

@client.command()
async def roll(ctx, number_of_dice: int, number_of_sides: int):
	dice = [
		str(random.choice(range(1, number_of_sides + 1)))
		for _ in range(number_of_dice)
	]
	await ctx.send(', '.join(dice))

@client.command()
async def help(ctx):
	await ctx.send(embed=helpmsg)

# aliases

@client.command() 
async def ms(ctx, length: int = 6, width: int = 6, mines = 7):
	await minesweeper(ctx,length,width,mines)

@client.command() 
async def Ms(ctx, length: int = 6, width: int = 6, mines = 7):
	await minesweeper(ctx,length,width,mines)

@client.command() 
async def Minesweeper(ctx, length: int = 6, width: int = 6, mines = 7):
	await minesweeper(ctx,length,width,mines)

client.run(token)
