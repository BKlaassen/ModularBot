from datetime import datetime
import pymongo


def load_errorlog(FOLDER):
    global folder
    global collection
    folder = FOLDER
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient[FOLDER]
    collection = db["Errorlog"]


def errorlog(error, functionname, message):
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    collection.insert_one({"timestamp": now, "error": str(error), "function": functionname, "message": message})
    print(f"{now} : {str(error)} : {functionname} : {message}")
