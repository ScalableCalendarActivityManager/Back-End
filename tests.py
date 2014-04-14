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
		
		
		
		
		
		