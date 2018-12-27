import os
import random
import time

from Errorlog import errorlog
from Send_message import send_message


def load_quotes(FOLDER):
    global folder
    global quotes

    folder = FOLDER
    quotes = {}
    try:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Quotes.txt', 'r') as f:
            for line in f:
                split = line.split("$")
                quotes[split[0]] = split[1].rstrip('\n')
    except:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Quotes.txt', 'w'):
            pass


def quote(s, message, game):
    global quotes
    arguments = message.split(" ")
    try:
        if arguments[1].lower() == "list":
            send_message(s,
                         f"Quotelist can be found here: http://www.bastixx.nl/twitch/{folder}/quotes.php")
        elif arguments[1].lower() == "add":
            try:
                currentdate = time.strftime("%d/%m/%Y")

                newquote = " ".join(arguments[2:])
                quotes[str(len(quotes) + 1)] = newquote + " [%s] [%s]" % (game, currentdate)
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Quotes.txt', 'a') as f:
                    f.write("%s$%s [%s] [%s]\n" % (len(quotes), newquote, game, currentdate))
                send_message(s, "Quote %d added!" % len(quotes))
            except Exception as errormsg:
                send_message(s, "There was an error adding this quote. Please try again!")
                errorlog(errormsg, "Quotes/addquote()", message)
        elif arguments[1].lower() == "remove":
            try:
                del quotes[arguments[2]]
                counter = 1
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Quotes.txt', 'w') as f:
                    for key, val in quotes.items():
                        f.write("%s$%s\n" % (counter, val))
                        counter += 1
                quotes = {}
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Quotes.txt') as f:
                    for line in f:
                        split = line.split("$")
                        quotes[split[0]] = split[1].rstrip('\n')
                send_message(s, "Quote %s removed!" % arguments[2])

            except Exception as errormsg:
                errorlog(errormsg, "Quotes/removequote()", message)
        else:
            try:
                if quotes:
                    try:
                        quoteindex = arguments[1]
                        quoteindex = int(quoteindex)
                        quote = quotes[quoteindex]
                        send_message(s, "Quote %s: %s" % (quoteindex, quote))
                    except KeyError:
                        send_message(s, "This quote does not exist.")
                    except ValueError:
                        quotes_temp = {}
                        for key, value in quotes.items():
                            if arguments[1].lower() in value.lower():
                                quotes_temp[key] = value
                        if len(quotes_temp) == 0:
                            send_message(s, "No quotes found.")
                        elif len(quotes_temp) == 1:
                            for key, value in quotes_temp.items():
                                send_message(s, "Quote %s: %s" % (key, value))
                        else:
                            keylist = []
                            for key in quotes_temp:
                                keylist.append(key)

                            randomindex = random.choice(keylist)
                            randomquote = quotes_temp[str(randomindex)]
                            send_message(s, "Quote %s: %s" % (randomindex, randomquote))
                    except Exception as errormsg:
                        errorlog(errormsg, "Quotes/quote()", message)
                        send_message(s, "Something went wrong, check your command.")
                else:
                    send_message(s, "No quotes yet!")
            except IndexError:
                send_message(s, "Error finding your searchterms. Check your command.")
            except Exception as errormsg:
                errorlog(errormsg, "Quotes/quote()", message)
                send_message(s, "Something went wrong, check your command.")
    except:
        randomindex = random.randint(1, len(quotes))
        randomquote = quotes[str(randomindex)]
        send_message(s, "Quote %s: %s" % (randomindex, randomquote))


def last_quote(s):
    try:
        quoteindex = len(quotes)
        quote = quotes[str(quoteindex)]
        send_message(s, "Quote %s: %s" % (quoteindex, quote))
    except Exception as errormsg:
        errorlog(errormsg, "Quotes/lastquote()", "")
        send_message(s, "There was an error retrieving the last quote. Error logged.")
