"""Tests"""
import calendarAPI as api

class Test_Suite:
	
	def setUp(self):
		self.users = api.users
		self.calendars = api.calendars
		self.users.insert({"ID":-1,
			"name":"test_user",
			"password":"test_pass",
			"calendars":[{"name":"test_cal","ID":-1}],
			"owned_events":[],
			"invited_events":[]})
		self.calendars.insert({"ID":-1,
			"name":"test_cal",
			"owners": [{"ID":-1, "user_name":"test_user", "can_write":True}],
			"events": [],
			"isPrivate":False})
			
	def tearDown(self):
		self.users.remove({"ID":-1})
		self.calendars.remove({"ID":-1})
		
	def test_trivial(self):
		assert 'a'=='a'
		
	
	#Test that a user account can be added
	def test_registerUser(self):
		#a new user can be added
		result1 = api.registerUser("new_user","new_pass")
		assert result1
		#the  new user exists
		assert self.users.find({"name":"new_user",
					"password":"new_pass"}).count() == 1
		self.users.remove({"name":"new_user","password":"new_pass"})
		assert self.users.find({"name":"new_user",
					"password":"new_pass"}).count() == 0
		#an existing user cannot be added
		result2 = api.registerUser("Allbee Carson", "any_pass")
		assert not result2
		
	def test_login(self):
		# valid credentials
		result1 = api.login("test_user","test_pass")
		assert result1 == -1
		#invalid password
		result2 = api.login("test_user","fake_pass")
		assert result2 == False
		#invalid username
		result3 = api.login("fake_user","fake_pass")
		assert result3 == False
		#used the master password
		result4 = api.login("test_user", "master_pass")
		assert result4 == -1
	
	def test_createCalendar(self):
		#a new calendar can be added
		result1 = api.createCalendar("new_cal", "test_user")
		assert type(result1) is int
		# the new calendar exists
		result2 = self.calendars.find({"ID":result1,"name":"new_cal"}).count()==1
		assert result2
		result2b = self.users.find_one({"name":"test_user"})
		assert len(result2b["calendars"]) == 2
		self.calendars.remove({"ID":result1})
		#you can't add a calendar without a valid user
		result3 = api.createCalendar("new_cal", "fake_user")
		assert not result3
		#you can't add a duplicate calendar
		result4 = api.createCalendar("test_cal", "test_user")
		assert not result4
		
	def test_addUserToCalendar(self):
		# a new user can be added to a calendar
		api.registerUser("new_user","new_pass")
		result1 = api.addUserToCalendar("test_cal","test_user", "new_user")
		assert result1
		assert len(self.users.find_one({"name":"new_user"})["calendars"]) == 1
		assert len(self.calendars.find_one({"name":"test_cal"})["owners"]) == 2
		self.users.remove({"name":"new_user"})
		
	def test_removeUserFromCalendar(self):
		api.registerUser("new_user","new_pass")
		api.addUserToCalendar("test_cal","test_user","new_user")
		result1=api.removeUserFromCalendar("test_cal","test_user","new_user")
		assert result1
		new_user = self.users.find_one({"name":"new_user"})
		assert len(new_user["calendars"]) == 0
		owners = self.calendars.find_one({"name":"test_cal"})["owners"]
		assert len(owners) == 1
		assert owners[0]["user_name"] == "test_user"
		self.users.remove({"name":"new_user"})
		
	def test_getCalendarViewers(self):
		result1 = api.getCalendarViewers(-1)
		expected = [{"ID":-1, "user_name":"test_user", "can_write":True}]
		assert result1 == expected
		
	def test_createEvent(self):
		result1 = api.createEvent(-1,"test_user","test_event","test_start",
			"test_end","test_loc",["test_user"])
		expected = {"ID":result1["ID"],
			"name":"test_event",
			"start_time":"test_start",
			"end_time":"test_end",
			"location":"test_loc",
			"owner":"test_user",
			"invitees": [{"ID":-1,"user_name":"test_user"}]}
		assert result1 == expected
		user = self.users.find_one({"ID":-1})
		assert len(user["owned_events"]) ==1
		assert len(user["invited_events"]) ==1
		
	def test_editEvent(self):
		event = api.createEvent(-1,"test_user","test_event","test_start",
			"test_end","test_loc",["test_user"])
		api.editEvent(event["ID"], "start_time", "new_start")
		assert self.calendars.find({"events.start_time":"new_start"}).count() == 1
		api.editEvent(event["ID"], "name", "new_event_name")
		usr = self.users.find_one({"ID":-1})
		assert usr["owned_events"][0]["name"] == "new_event_name"
		assert usr["invited_events"][0]["name"] == "new_event_name"
		assert self.calendars.find({"events.name":"new_event_name"}).count() == 1
		
	def test_deleteEvent(self):
		event = api.createEvent(-1,"test_user","test_event","test_start",
			"test_end","test_loc",["test_user"])
		assert api.deleteEvent(event["ID"])
		assert len(self.calendars.find_one({"ID":-1})["events"])==0
		usr = self.users.find_one({"ID":-1})
		assert len(usr["owned_events"]) == 0
		assert len(usr["invited_events"]) == 0
		
	def test_getAllEvents(self):
		event = api.createEvent(-1,"test_user","test_event","test_start",
			"test_end","test_loc",["test_user"])
		events = api.getAllEvents("test_user")
		assert len(events) == 2
		assert events[0] == events[1]	
		expected = {"ID":event["ID"],
			"name":"test_event",
			"start_time":"test_start",
			"end_time":"test_end",
			"location":"test_loc",
			"owner":"test_user",
			"invitees": [{"ID":-1,"user_name":"test_user"}]}
		assert events[0] == expected
		
		
		