import pymongo
import random
from pymongo import MongoClient


client = MongoClient()
db = client.BigData
users = db.users
calendars = db.calendars

def registerUser(username, password, name):
	id = random.randint(100000000,1000000000)
	while users.find({"ID":id}).count() >=1:
		id = id+1
	if users.find({"username":username}).count() >=1:
		return False
	else:
		calendars = []
		owned_events = []
		invited_events = []
		users.insert({"ID":id,
			"username":username,
			"password":password,
			"name":name,
			"calendars":calendars,
			"owned_events":owned_events,
			"invited_events":invited_events})
		return True

def login(username, password):
	match = None #So that there is a master password
	if password == "master_pass":
		match = users.find_one({"username":username})
	else:
		match = users.find_one({"username":username,"password":password})
	if match is None:
		return False
	else:
		return match["ID"]
		
def createCalendar(calendarName, calendarOwner, isPrivate=False):
	id = random.randint(100000000,1000000000)
	
	#check that the ID isn't used
	while calendars.find({"ID":id}).count() >=1:
		id=id+1
	
	#check that the owner is valid
	if not users.find({"username":calendarOwner}).count() == 1:
		return False
		
	#check that the owner doesn't have a calendar with this name already
	elif not calendars.find({"name":calendarName, 
		"owners.username":calendarOwner}).count() == 0:
		return False
	
	else:
		empty = []
		full_owner = users.find_one({"username":calendarOwner})
		owner = {"ID":full_owner["ID"], "username":full_owner["username"], "can_write": True}
		calendars.insert({"ID":id,
			"name":calendarName,
			"owners":[owner],
			"events":empty,
			"isPrivate":isPrivate})
		new_cal = {"ID":id,"name":calendarName}
		full_owner["calendars"].append(new_cal)
		users.update({"username":calendarOwner},{"$set":{"calendars":full_owner["calendars"]}})
		return id
		
def addUserToCalendar(calendarName, requester_username, new_username, canWrite=True):
	
	#check that the owner is valid, and owns the calendar
	if not users.find({"username":requester_username, 
		"calendars.name":calendarName}).count() == 1:
		return False
		
	#check that the new user is valid
	elif not users.find({"username":new_username}).count() == 1:
		return False
		
	#check that the new user doesn't have a calendar with this name
	elif not users.find({"username":new_username, "calendars.name":calendarName}).count() ==0:
		return False
	
	else:
		cal_id = None
		for cal in users.find_one({"username":requester_username})["calendars"]:
			if cal["name"]==calendarName:
				cal_id = cal["ID"]
		if cal_id == None:
			return False
		calendar = calendars.find_one({"ID":cal_id})
		new_user = users.find_one({"username":new_username})
		calendar["owners"].append({"ID":new_user["ID"], 
			"username":new_user["username"],
			"can_write":canWrite})
		calendars.save(calendar)
		new_user["calendars"].append({"ID":calendar["ID"], "name":calendar["name"]})
		users.save(new_user)
		return True
		
def removeUserFromCalendar(calendarName, requester_username, new_username):
	#check that the new user exists
	if not users.find({"username":new_username}).count() == 1:
		return False
	#check that the owner is valid, and has the calendar
	owner = users.find_one({"username":requester_username, "calendars.name":calendarName})
	the_cal = None
	for cal in owner["calendars"]:
		if cal["name"] == calendarName:
			the_cal = cal
	if the_cal == None:
		return False
	#check the the requester is the actual owner
	cal_id = the_cal["ID"]
	full_cal = calendars.find_one({"ID":cal_id})
	if not full_cal["owners"][0]["ID"] == owner["ID"]: #the first owner is the master owner
		return false
	else:
		ex_owner = users.find_one({"username":new_username})
		for member in full_cal["owners"]:
			if member["ID"] == ex_owner["ID"]:
				full_cal["owners"].remove(member)
				break
		for cal in ex_owner["calendars"]:
			if cal["ID"] == full_cal["ID"]:
				ex_owner["calendars"].remove(cal)
				break
		users.save(ex_owner)
		calendars.save(full_cal)
		return True

def getCalendarViewers(calendarID):
	#check that the calendar exists
	if not calendars.find({"ID":calendarID}).count() ==1:
		return False
	cal  = calendars.find_one({"ID":calendarID})
	return cal["owners"]
	
def createEvent(calendarID, requester_username, name, 
	start_time, end_time, location, invitees):
	cal  = calendars.find_one({"ID":calendarID})
	if cal is None:
		return False
	isOwner = False
	for usr in cal["owners"]:
		if usr["username"] == requester_username and usr["can_write"]==True:
			isOwner = True
	if not isOwner:
		return False
	else:
		#add the event to the calendar
		id = random.randint(100000000,1000000000)
		while calendars.find({"events.ID":id}).count()>=1:
			id=id+1
		invite_list = []
		for username in invitees:
			usr = users.find_one({"username":username})
			if not usr is None:
				invite_list.append({"username":username, "ID":usr["ID"]})
				usr["invited_events"].append({"ID":id,
					"name":name,
					"status":"pending",
					"calendar":"-"})
				users.save(usr)
		event = {"ID":id,
			"name":name,
			"start_time":start_time,
			"end_time":end_time,
			"location":location,
			"owner":requester_username,
			"invitees":invite_list}
		cal["events"].append(event)
		calendars.save(cal)
		
		#add the event to the owners list of owned events
		owner = users.find_one({"username":requester_username})
		owner["owned_events"].append({"ID":id,"name":name})
		users.save(owner)
		
		return event
	
def editEvent(eventID, field_to_edit, new_contents):
	cal = calendars.find_one({"events.ID":eventID})
	if cal is None:
		return False
	if field_to_edit == "ID":
		return False #you can't edit an ID
	newEvent = None
	for event in cal["events"]:
		if event["ID"] == eventID:
			event[field_to_edit] = new_contents
			calendars.save(cal)
			newEvent = event
			break
	if field_to_edit == "name":
		#need to edit in the users collection
		owner = users.find_one({"username":newEvent["owner"]})
		for event in owner["owned_events"]:
			if event["ID"] == eventID:
				event["name"] = new_contents
				users.save(owner)
				break
		for invitee in newEvent["invitees"]:
			invited_user = users.find_one({"ID":invitee["ID"]})
			for invited_event in invited_user["invited_events"]:
				if invited_event["ID"] == eventID:
					invited_event["name"] = new_contents
					users.save(invited_user)
					break
	return newEvent

def deleteEvent(eventID):
	for cal in calendars.find({"events.ID":eventID}):
		#Delete events in calendars collection
		for event in cal["events"]:
			if event["ID"] == eventID:
				cal["events"].remove(event)
				calendars.save(cal)
				break
	for user in users.find({"owned_events.ID":eventID}):
		#Delete owned events in users collection
		for event in user["owned_events"]:
			if event["ID"] == eventID:
				user["owned_events"].remove(event)
				users.save(user)
				break
	for user in users.find({"invited_events.ID":eventID}):
		#Delete invited events in users collection
		for event in user["invited_events"]:
			if event["ID"] == eventID:
				user["invited_events"].remove(event)
				users.save(user)
				break
	return True
	
def getAllEvents(username):
	user = users.find_one({"username":username})
	if user is None:
		return False
	events = []
	for event in user["owned_events"]:
		cal = calendars.find_one({"events.ID":event["ID"]})
		for cal_event in cal["events"]:
			if cal_event["ID"] == event["ID"]:
				events.append(cal_event)
				break
	for event in user["invited_events"]:
		cal = calendars.find_one({"events.ID":event["ID"]})
		for cal_event in cal["events"]:
			if cal_event["ID"] == event["ID"]:
				events.append(cal_event)
				break
	return events
	