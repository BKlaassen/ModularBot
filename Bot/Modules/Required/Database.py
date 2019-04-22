import pymongo
from Modules.Required.Errorlog import errorlog


def load_database(database):
    global db
    global channel
    channel = database
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient[database]


def getchannel():
    return channel


def getallfromdb(collection):
    try:
        mycol = db[collection]
        mydocs = mycol.find({})
        return mydocs
    except Exception as errormsg:
        errorlog(errormsg, "Database/getallfromDB()", f"Collection: {collection}")
        raise Exception


def getonefromdb(collection, filter={}):
    try:
        mycol = db[collection]
        mydocs = mycol.find(filter)
        dictionary = {}
        for document in mydocs:
            dictionary = document
        return dictionary
    except Exception as errormsg:
        errorlog(errormsg, "Database/getallfromDB()", f"Collection: {collection}")
        raise Exception


def insertoneindb(collection, data):
    try:
        mycol = db[collection]
        mycol.insert_one(data)
    except Exception as errormsg:
        errorlog(errormsg, "Database/insertone()", "data: " + data)
        raise Exception


def deleteoneindb(collection, filter):
    try:
        mycol = db[collection]
        mycol.delete_one(filter)
    except Exception as errormsg:
        errorlog(errormsg, "Database/deleteone()", "filter: " + filter)
        raise Exception


def deletecollection(collection):
    try:
        db.drop_collection(collection)
    except Exception as errormsg:
        errorlog(errormsg, "Database/deletecollection()", "collection: " + collection)
        raise Exception


def updateoneindb(collection, fltr, data, upsert=False):
    try:
        mycol = db[collection]
        mycol.update_one(fltr, data, upsert, upsert)
    except Exception as errormsg:
        errorlog(errormsg, "Database/updateone()", "filter: " + fltr + " Data: " + data)
        raise Exception


def updatemanyindb(collection, filter, data):
    try:
        mycol = db[collection]
        mycol.update_many(filter, data)
    except Exception as errormsg:
        errorlog(errormsg, "Database/updatemany()", "filter: " + filter + " Data: " + data)
        raise Exception


def clearcollection(collection):
    try:
        mycol = db[collection]
        mycol.delete_many({})
        return True
    except Exception as errormsg:
        errorlog(errormsg, "Database/clearcollection()", collection)
        return Exception


def copycollection(oldcollection, newcollection):
    try:
        db[oldcollection].copyTo(newcollection)
        return True
    except Exception as errormsg:
        errorlog(errormsg, "Database/clearcollection()", f"old: {oldcollection}, new: {newcollection}")
        return Exception


def collectionexists(collection):
    try:
        collectionnames = db.list_collection_names()
        if collection in collectionnames:
            return True
        else:
            return False
    except Exception as errormsg:
        errorlog(errormsg, "Database/doescollectionexitt()", collection)
        return Exception
