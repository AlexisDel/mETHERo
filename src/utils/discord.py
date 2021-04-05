num2emoji = {'0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
             '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'}


def number_to_emoji(number):
    """
    Returns an emojize version of number
    """
    s = str(number)
    word = ""
    for l in s:
        word += num2emoji.get(l)
    return word


def trends_to_message(trends, frequency_prefix):
    if len(trends) > 30:
        top = 30
    else:
        top = len(trends)

    text = "```📈 " + frequency_prefix + " trends on Twitter! 🔥" + \
           "\n\n" + "Top " + number_to_emoji(top) + " :" + "\n\n"

    for i in range(top):
        name, percent = trends[i]
        text += "$" + name + (6 - len(name)) * " " + int(percent * 36 / 20) * "🟢" + "\n"
    text += "```"

    return text


def alert_to_message(trends, prefix):
    text = "```" + prefix + "\n\n" \
                            " 🕒 Last hour : \n\n"
    for crypto, percent in trends:
        text += "  🚀 $" + crypto + " : " + "{:.0f}".format(percent) + "% of tweets " + "\n"
    text += "```"

    return text