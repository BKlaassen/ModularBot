from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database


def load_rules():
    global rules; global warnings
    rules = {}
    warnings = {}
    try:
        col = Database.getallfromdb("Rules")
        for document in col:
            rules[document["_id"]] = {"rule": document["Rule"], "1": document["first_timeout"],
                                      "2": document["second_timeout"], "3": document["third_timeout"]}

    except Exception as errormsg:
        errorlog(errormsg, "Rules/Load_rules()", "")


def func_rules(message):
    arguments = message.split(" ")
    ruleno = arguments[1]
    ruletext = rules[ruleno]['rule']

    if arguments[2] in warnings.keys():
        warningno = str(warnings[arguments[2]].count(ruleno) + 1)
        warnings[arguments[2]].append(ruleno)
    else:
        warnings[arguments[2]] = ruleno
        warningno = '1'

    if warningno == "1":
        warningnotext = "first"
    elif warningno == "2":
        warningnotext = "second"
    elif warningno == "3":
        warningnotext = "third"
    else:
        warningnotext = "null"

    timeouttime = rules[ruleno][warningno]
    if timeouttime != '0':
        send_message("/timeout %s %s broke rule %s (%s warning)" % (
            arguments[2], timeouttime, ruleno, warningnotext))
        send_message("@%s You have been timed out for %s seconds because "
                     "you broke rule %s: %s."" This was your %s warning!" %
                     (arguments[2], timeouttime, ruleno, ruletext, warningnotext))
    else:
        send_message("/ban %s  broke rule %s" % (arguments[2], ruleno))
        send_message("@%s You have been banned from this channel because "
                     "you broke rule %s: %s. This was your %s warning!" %
                     (arguments[2], ruleno, ruletext, warningnotext))
