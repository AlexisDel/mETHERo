# mETHERo
A Discord bot that provides twitter crypto trends

## How it works
* ```bot.py``` manages the discord bot, it gets data from ```trends``` directory
* ```trends.py``` updates the ```trends``` directory by scanning users timeline from ```users.txt``` and create a file for each hours scanned

![](https://i.imgur.com/D3ErNj0.jpg)

## How to run

Make sure to install required libraries before running scripts
```bash
pip install -r requirements.txt
```

Run mETHERo
```bash
python3 bot.py
```

Run trends 
```bash
python3 trends.py
```
