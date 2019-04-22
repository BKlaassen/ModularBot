import random

from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database


def load_questions():
    global questions
    questions = {}
    try:
        if Database.collectionexists("Questions"):
            for document in Database.getallfromdb("Questions"):
                questions[document["_id"]] = document["question"]
    except Exception as errormsg:
        errorlog(errormsg, "Questions/Load_questions()", "")


def question(message, ismod):
    global questions
    arguments = message.split(" ")

    if arguments[1] == "add" and ismod:
        created = False
        try:
            newquestion = " ".join(arguments[2:])
            # Loop over all keys and check if this slot is taken
            for i in range(1, len(questions)):
                if i not in questions.keys():
                    questions[i] = newquestion
                    Database.insertoneindb("Questions", {"_id": i, "question": newquestion})
                    created = True
            if not created:
                questions[str(len(questions) + 1)] = newquestion
                Database.insertoneindb("Questions", {"_id": len(questions), "question": newquestion})
            send_message("question %d added!" % len(questions))
        except Exception as errormsg:
            send_message("There was an error adding this question. Please try again!")
            errorlog(errormsg, "Questions/add()", message)
        cooldowntime = 5

    elif arguments[1] == "remove" and ismod:
        try:
            if questions.get(arguments[2], False):
                del questions[arguments[2]]
                Database.deleteoneindb("Questions", {"_id": arguments[2]})
            send_message("Question %s removed!" % arguments[2])

        except KeyError:
            send_message(f'Question number {arguments[2]} does not exist.')

        except Exception as errormsg:
            errorlog(errormsg, "Questions/remove()", message)
            send_message("There was an error removing this question. Please check your command and try again.")
        cooldowntime = 5

    elif arguments[1] == "edit" and ismod:
        try:
            if questions.get(arguments[2], False):
                newquestion = " ".join(arguments[3:])
                questions[arguments[2]] = newquestion
                Database.updateoneindb("Questions", {"_id": arguments[2]}, {"question": newquestion})
                send_message(f"Question {arguments[2]} updated: {newquestion}")
        except Exception as errormsg:
            errorlog(errormsg, "Questions/edit()", message)
            send_message("There was an error editing this question. Please check your command and try again.")
        cooldowntime = 5
    else:
        try:
            int(arguments[1]) / 1
            send_message(f"{arguments[1]}: {questions[arguments[1]]}")
        except ValueError:
            if questions:
                randomindex = random.randint(1, len(questions))
                randomquestion = questions[str(randomindex)]
                send_message("%s: %s" % (randomindex, randomquestion))
            else:
                send_message("No questions yet!")
        except Exception as errormsg:
            errorlog(errormsg, "Question/question()", message)
            send_message("Something went wrong, check your command.")
        cooldowntime = 20

    return cooldowntime
