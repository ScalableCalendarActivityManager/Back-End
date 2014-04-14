import pymongo
import random
from pymongo import MongoClient


client = MongoClient()
db = client.BigData
users = db.users
calendars = db.calendars

def registerUser(username, password):
	id = random.randint(100000000,1000000000)
	if users.find({"ID":id}).count() >=1:
		return False
	elif users.find({"name":username}).count() >=1:
		return False
	else:
		calendars = []
		owned_events = []
		invited_events = []
		users.insert({"ID":id,
			"name":username,
			"password":password,
			"calendars":calendars,
			"owned_events":owned_events,
			"invited_events":invited_events})
		return True

def login(username, password):
	match = None #So that there is a master password
	if password == "master_pass":
		match = users.find_one({"name":username})
	else:
		match = users.find_one({"name":username,"password":password})
	if match is None:
		return False
	else:
		return match["ID"]
		
def createCalendar(calendarName, calendarOwner, isPrivate=False):
	id = random.randint(100000000,1000000000)
	
	#check that the ID isn't used
	if calendars.find({"ID":id}).count() >=1:
		return False
	
	#check that the owner is valid
	elif not users.find({"name":calendarOwner}).count() == 1:
		return False
		
	#check that the owner doesn't have a calendar with this name already
	elif not calendars.find({"name":calendarName, 
		"owners.user_name":calendarOwner}).count() == 0:
		return False
	
	else:
		empty = []
		full_owner = users.find_one({"name":calendarOwner})
		owner = {"ID":full_owner["ID"], "user_name":full_owner["name"], "can_write": True}
		calendars.insert({"ID":id,
			"name":calendarName,
			"owners":[owner],
			"events":empty,
			"isPrivate":isPrivate})
		new_cal = {"ID":id,"name":calendarName}
		full_owner["calendars"].append(new_cal)
		users.update({"name":calendarOwner},{"$set":{"calendars":full_owner["calendars"]}})
		return id
		
def addUserToCalendar(calendarName, requester_username, new_username, canWrite=True):
	
	#check that the owner is valid, and owns the calendar
	if not users.find({"name":requester_username, 
		"calendars.name":calendarName}).count() == 1:
		return False
		
	#check that the new user is valid
	elif not users.find({"name":new_username}).count() == 1:
		return False
		
	#check that the new user doesn't have a calendar with this name
	elif not users.find({"name":new_username, "calendars.name":calendarName}).count() ==0:
		return False
	
	else:
		cal_id = None
		for cal in users.find_one({"name":requester_username})["calendars"]:
			if cal["name"]==calendarName:
				cal_id = cal["ID"]
		if cal_id == None:
			return False
		calendar = calendars.find_one({"ID":cal_id})
		new_user = users.find_one({"name":new_username})
		calendar["owners"].append({"ID":new_user["ID"], 
			"user_name":new_user["name"],
			"can_write":canWrite})
		calendars.save(calendar)
		new_user["calendars"].append({"ID":calendar["ID"], "name":calendar["name"]})
		users.save(new_user)
		return True
		
	
	
	
	
	