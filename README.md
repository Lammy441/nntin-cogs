# nntin-cogs
Some cogs I made/refined and use. If you have questions, message me on [Discord](https://discord.gg/Dkg79tc).
Project is WIP as I am experimenting with Red v3 beta.

## cogs
remindme: based on [26-cogs](https://github.com/Twentysix26/26-Cogs/) with slight modification on the syntax for easier usage.  
tweets: based on [discord-twitter-bot](https://github.com/NNTin/discord-twitter-bot)  
pc: privatechannel [preview](https://i.imgur.com/MZf14Eq.gifv)

## install

If you haven't already installed Red v3. Note: Python 3.5.0 or later is required. Check it via `python3 --version`.
```
python3 -m venv bot-env
source bot-env/bin/activate
python3 -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py
python3 -m pip install -U --process-dependency-links red-discordbot
redbot-setup redv3
redbot redv3
```

Discord bot commands:
```
[p]load downloader
[p]repo add nntincogs https://github.com/NNTin/nntin-cogs
[p]cog install nntincogs tweets
[p]cog install nntincogs remindme
[p]cog install nntincogs pc
```

alternatively:  
terminal:
```
cd <path>
git clone https://github.com/NNTin/nntin-cogs
```
discord bot command:
```
[p]addpath <path>
[p]load tweets
[p]load remindme
[p]load pc
```