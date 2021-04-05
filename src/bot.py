import discord
from discord.ext import commands
import tweepy
import datetime
import aiocron

from utils import database
from utils import discord as Discord
from config import api_keys, discord_channels


# Constants:
HOT_TRENDS_LIMIT_PERCENTAGE = 20

# Main

DiscordAPI = commands.Bot(command_prefix='$')

# Twitter authentication
auth = tweepy.OAuthHandler(api_keys.TWITTER_CONSUMER_KEY, api_keys.TWITTER_CONSUMER_SECRET)
auth.set_access_token(api_keys.TWITTER_ACCESS_TOKEN, api_keys.TWITTER_ACCESS_TOKEN_SECRET)
TwitterAPI = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=False)


# Automatic tasks
@aiocron.crontab('0 20 * * *')
async def daily_trends():
    trends = database.get_trends(24)
    await DiscordAPI.get_channel(discord_channels.TWITTER_DAILY).send(Discord.trends_to_message(trends, "Daily"))

    trends = database.get_trends(24, "out", 100)
    await DiscordAPI.get_channel(discord_channels.TWITTER_DAILY).send(Discord.trends_to_message(trends, "Daily 💎"))


@aiocron.crontab('0 20 * * SUN')
async def weekly_trends():
    trends = database.get_trends(24 * 7)
    await DiscordAPI.get_channel(discord_channels.TWITTER_WEEKLY).send(Discord.trends_to_message(trends, "Weekly"))

    trends = database.get_trends(24 * 7, "out", 100)
    await DiscordAPI.get_channel(discord_channels.TWITTER_WEEKLY).send(Discord.trends_to_message(trends, "Weekly 💎"))


@aiocron.crontab('0 20 1 * *')
async def monthly_trends():
    trends = database.get_trends(24 * 30)
    await DiscordAPI.get_channel(discord_channels.TWITTER_MONTHLY).send(Discord.trends_to_message(trends, "Monthly"))

    trends = database.get_trends(24 * 30, "out", 100)
    await DiscordAPI.get_channel(discord_channels.TWITTER_MONTHLY).send(Discord.trends_to_message(trends, "Monthly 💎"))


@aiocron.crontab('0 * * * *')
async def trends_alert():
    hot_trends = database.get_hot_trends(1, HOT_TRENDS_LIMIT_PERCENTAGE)
    if hot_trends:
        await DiscordAPI.get_channel(discord_channels.TWITTER_ALERTS).send(
            Discord.alert_to_message(hot_trends, "🔥  HOT TRENDS ALERT  🔥"))

    no_top_100_hot_trends = database.get_hot_trends(1, HOT_TRENDS_LIMIT_PERCENTAGE, "out", 100)
    if no_top_100_hot_trends:
        await DiscordAPI.get_channel(discord_channels.TWITTER_ALERTS).send(
            Discord.alert_to_message(no_top_100_hot_trends, "💎  GEM ALERT  💎"))


# Commands
@DiscordAPI.command(brief="Shows crypto trends",
                    description="Examples :\n"
                                "$trends 24  # Last 24 hours trends \n"
                                "$trends 12 in 100  # Last 12 hours trends in top 100 MC \n"
                                "$trends 48 out 500  # Last 2 days trends out of top 500 MC")
async def trends(ctx, *args):
    # Handle bad channel issues
    if ctx.channel.id != discord_channels.TWITTER_COMMAND:
        return await ctx.message.delete()

    delta = None
    inout = None
    top = None

    # Handle input issues
    if len(args) == 1 or len(args) == 3:

        # hours
        try:
            delta = int(args[0])
            if datetime.datetime.now() - datetime.timedelta(hours=delta) < datetime.datetime(2021, 1, 1):
                return await ctx.send("L'époque de nos grands frères")
        except ValueError as e:
            return await ctx.send('\"' + str(args[0]) + '\"' + " n'est pas un entier " + "🤔")
        except OverflowError:
            return await ctx.send("Ça fait beaucoup d'heures là non ⁉️")

        if len(args) == 3:

            # in/out
            inout = args[1]
            if inout != "in" and inout != "out":
                return await ctx.send("Dans la vie y'a 2 possibilités, soit tu es in soit tu es out")

            # top
            try:
                top = int(args[2])
            except ValueError as e:
                return await ctx.send('\"' + str(args[2]) + '\"' + " n'est pas un entier " + "🤔")
            except OverflowError:
                return await ctx.send("Ça fait beaucoup de crypto là non ⁉️")

    else:
        return await ctx.send("Problème d'arguments ($help trends)")

    # Main
    trends = database.get_trends(delta, inout, top)
    await ctx.send(Discord.trends_to_message(trends, "Last " + str(delta) + "h"))


@DiscordAPI.command(brief="Adds user to Database",
                    description="Example :\n"
                                "$add Fantiks  # add @Fantiks to Database")
async def add(ctx, arg):
    if ctx.channel.id != discord_channels.COMMAND:
        return await ctx.message.delete()
    return await ctx.send(database.add_username_to_database(TwitterAPI, arg))


@DiscordAPI.command(brief="Adds user's friends to Database",
                    description="Example :\n"
                                "$add_friends Fantiks  # add @Fantiks's friends to Database")
async def add_friends(ctx, arg):
    if ctx.channel.id != discord_channels.COMMAND:
        return await ctx.message.delete()
    return await ctx.send(database.add_user_followers_to_database(TwitterAPI, arg))


@DiscordAPI.event
async def on_ready():
    await DiscordAPI.change_presence(activity=discord.Game("Hmmmm !!"))


DiscordAPI.run(api_keys.DISCORD_API_KEY)
