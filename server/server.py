# coding=utf-8
#------------------------------------------------------------------------------------------------------
# TDA596 Labs - Server Skeleton
# server/server.py
# Input: Node_ID total_number_of_ID
# Student Group: 37
# Student name: Daniele Dellagiacoma
#------------------------------------------------------------------------------------------------------
# Import various libraries
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler # Socket specifically designed to handle HTTP requests
import sys # Retrieve arguments
from urlparse import parse_qs # Parse POST data
from httplib import HTTPConnection # Create a HTTP connection, as a client (for POST requests to the other vessels)
from urllib import urlencode # Encode POST content into the HTTP header
from codecs import open # Open a file
from threading import  Thread # Thread Management
from random import randint # Generate random integer
#------------------------------------------------------------------------------------------------------

# Global variables for HTML templates
board_frontpage_footer_template = ""
board_frontpage_header_template = ""
boardcontents_template = ""
entry_template = ""

#------------------------------------------------------------------------------------------------------
# Static variables definitions
PORT_NUMBER = 80
STUDENT_NAME = "Daniele Dellagiacoma"
#------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
class BlackboardServer(HTTPServer):
#------------------------------------------------------------------------------------------------------
	def __init__(self, server_address, handler, node_id, vessel_list):
		# Call the super init
		HTTPServer.__init__(self, server_address, handler)
		# Create the dictionary of values
		self.store = {}
		# Keep a variable of the next id to insert
		self.current_key = -1
		# Our own ID (IP is 10.1.0.ID)
		self.vessel_id = vessel_id
		# The list of other vessels
		self.vessels = vessel_list
		# Save if the server is the leader, the leader id, and server id randomly generated
		# initially leader:0, leaderIp:server id and vassel id for the leader election randomly generated from 0 to 1000
		self.leader = {'leader':0, 'leaderIp':vessel_id, 'randId':randint(0,1000)}

#------------------------------------------------------------------------------------------------------
	# Add a value received to the store
	def add_value_to_store(self, value):
		# Add the value to the store
		id = 0
		for entry in self.store:
			id = max(entry, id)
		self.store[id+1] = value
#------------------------------------------------------------------------------------------------------
	# Modify a value received in the store
	def modify_value_in_store(self, key, value):
		# Modify a value in the store if it exists
		if key in self.store:
			self.store[key] = value
#------------------------------------------------------------------------------------------------------
	# Delete a value received from the store
	def delete_value_in_store(self, key):
		# Delete a value in the store if it exists
		if key in self.store:
			del self.store[key]
#------------------------------------------------------------------------------------------------------
	# Contact a specific vessel with a set of variables to transmit to it
	def contact_vessel(self, vessel_ip, path, entry, delete):
		# The Boolean variable taht will be returned
		success = False
		# The variables must be encoded in the URL format, through urllib.urlencode
		post_content = urlencode({'entry': entry, 'delete': delete})
		# The HTTP header must contain the type of data transmitted, here URL encoded
		headers = {"Content-type": "application/x-www-form-urlencoded"}
		# Try to catch errors when contacting the vessel
		try:
			# Contact vessel:PORT_NUMBER since they all use the same port
			# Set a timeout to 30 seconds, after which the connection fails if nothing happened
			connection = HTTPConnection("%s:%d" % (vessel_ip, PORT_NUMBER), timeout = 30)
			# Only use POST to send data (PUT and DELETE not supported)
			action_type = "POST"
			# Send the HTTP request
			connection.request(action_type, path, post_content, headers)
			# Retrieve the response
			response = connection.getresponse()
			# Check the status, the body should be empty
			status = response.status
			# If it receive a HTTP 200 - OK
			if status == 200:
				success = True
		# Catch every possible exceptions
		except Exception as e:
			print "Error while contacting %s" % vessel_ip
			# Print the error given by Python
			print(e)

		# Return if succeeded or not
		return success
#------------------------------------------------------------------------------------------------------
	# Send a received value to all the other vessels of the system
	def propagate_value_to_vessels(self, path, entry, delete):
		# Iterate through the vessel list
		for vessel in self.vessels:
			# Should not send it to our own IP, or it would create an infinite loop of updates
			if vessel != ("10.1.0.%s" % self.vessel_id):
				# Try again until the request succeed
				while (True):
					if self.contact_vessel(vessel, path, entry, delete):
						break

#------------------------------------------------------------------------------------------------------
	# Contact a specific vessel with a set of variables to transmit to it
	def contact_vessel_for_election(self, vessel_ip, path, leaderIp, maxId):
		# The Boolean variable that will be returned
		success = False
		# The variables must be encoded in the URL format, through urllib.urlencode
		post_content = urlencode({'leaderIp': leaderIp, 'maxId': maxId})
		# The HTTP header must contain the type of data transmitted, here URL encoded
		headers = {"Content-type": "application/x-www-form-urlencoded"}
		# Try to catch errors when contacting the vessel
		try:
			# Contact vessel:PORT_NUMBER since they all use the same port
			# Set a timeout to 30 seconds, after which the connection fails if nothing happened
			connection = HTTPConnection("%s:%d" % (vessel_ip, PORT_NUMBER), timeout = 30)
			# Only use POST to send data (PUT and DELETE not supported)
			action_type = "POST"
			# Send the HTTP request
			connection.request(action_type, path, post_content, headers)
			# Retrieve the response
			response = connection.getresponse()
			# Check the status, the body should be empty
			status = response.status
			# If it receive a HTTP 200 - OK
			if status == 200:
				success = True
		# Catch every possible exceptions
		except Exception as e:
			print "Error while contacting %s" % vessel_ip
			# Print the error given by Python
			print e

#------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# This class implements the logic when a server receives a GET or POST request
# It can access to the server data through self.server.*
# i.e. the store is accessible through self.server.store
# Attributes of the server are SHARED accross all request hqndling/ threads!
class BlackboardRequestHandler(BaseHTTPRequestHandler):
#------------------------------------------------------------------------------------------------------
	# Fill the HTTP headers
	def set_HTTP_headers(self, status_code = 200):
		# Set the response status code (200 if OK, something else otherwise)
		self.send_response(status_code)
		# Set the content type to HTML
		self.send_header("Content-type", "text/html")
		# Close headers
		self.end_headers()
#------------------------------------------------------------------------------------------------------
	# POST request must be parsed through urlparse.parse_QS, since the content is URL encoded
	def parse_POST_request(self):
		post_data = ""
		# Parse the response, the length of the content is needed
		length = int(self.headers['Content-Length'])
		# Parse the content using parse_qs
		post_data = parse_qs(self.rfile.read(length), keep_blank_values = 1)
		# Return the data
		return post_data
#------------------------------------------------------------------------------------------------------	
#------------------------------------------------------------------------------------------------------
# Request handling - GET
#------------------------------------------------------------------------------------------------------
	# This function contains the logic executed when this server receives a GET request
	# This function is called AUTOMATICALLY upon reception and is executed as a thread!
	def do_GET(self):
		print("Receiving a GET on path %s" % self.path)

		# Check which path was requested and call the right logic based on it
		# At this time, the GET request can only be "/" or "/board"
		if (self.path) == "/" or self.path == "/board":
			self.do_GET_Index()
		else:
			# In any other case 
			self.wfile.write("The requested URL does not exist on the server")
#------------------------------------------------------------------------------------------------------
# GET logic - specific path: "/" or "/board"
#------------------------------------------------------------------------------------------------------
	def do_GET_Index(self):
		
		try:
			# Set the response status code to 200 (OK)
			self.set_HTTP_headers(200)
			
			# Go over the entries already stored in the server  to produce the boardcontents part
			allEntries_template = ""
			for key in self.server.store:
				allEntries_template = allEntries_template + entry_template % ("board/" + str(key), key, self.server.store[key])

			# Construct the full page by combining all the parts
			html_reponse = board_frontpage_header_template + boardcontents_template % ("10.1.0."+str(self.server.vessel_id)+":"+str(PORT_NUMBER)+" Random ID: "+str(self.server.leader['randId']), allEntries_template) + board_frontpage_footer_template % STUDENT_NAME

			# Write the HTML file on the browser
			self.wfile.write(html_reponse)

		# Catch every possible exception
		except Exception as e:
			# Print error given by Python on the server console
			print e
			# Write the error given by Python on the browser
			self.wfile.write("The following problem has been encountered: " + str(e) + "\n. Please try to refresh the page. \n")
			# Set the response status code to 400 (Bad Request)
			self.set_HTTP_headers(400)
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Request handling - POST
#------------------------------------------------------------------------------------------------------
	# This function contains the logic executed when this server receives a POST request
	# This function is called AUTOMATICALLY upon reception and is executed as a thread!
	def do_POST(self):
		print("Receiving a POST on %s" % self.path)

		try:
			# Variable used to check if the message needs to be propagated to the other servers
			retransmit = False
			# Call the method to parse the data received from the POST request
			# Save the data in a dictionary, e.g. {'entry':['new Value'], 'delete':['0']}
			parameters = self.parse_POST_request()
			# Check which path was requested and call the right logic based on it
			path_segments = (self.path).split("/")

			if len(path_segments) > 1:
				# The POST requests with path "/board..." and "/propagate..." work at the same way (i.e. add, modify or delete a value in the server store)
				# The difference is that a POST request with path "/board..." will be retransmitted to the other servers
				# whereas a POST request with path "/propagate..." won't be retransmitted to avoid infinite loops
				# if the server that received the request is the leader (i.e. leader['leader']==1), it will propagate the message to all the other servers
				if path_segments[1] == "board" and self.server.leader['leader'] == 1:
					self.do_POST_Parameters(parameters, path_segments)
					retransmit=True
				# if the server that received the request is not the leader (i.e. leader['leader']==0), it will retransmit the request to the leader (i.e. leader['leaderIp'])
				elif path_segments[1] == "board" and self.server.leader['leader'] == 0:
					# Check if it is a add request or a modify/delete request
					if 'delete' in parameters:
						thread = Thread(target=self.server.contact_vessel, args=("10.1.0.%s" % self.server.leader['leaderIp'], self.path, parameters['entry'][0], parameters['delete'][0]))
						# Kill the process if we kill the server
						thread.daemon = True
						# Start the thread
						thread.start()
					else:
						thread = Thread(target=self.server.contact_vessel, args=("10.1.0.%s" % self.server.leader['leaderIp'], self.path, parameters['entry'][0], None))
						# Kill the process if we kill the server
						thread.daemon = True
						# Start the thread
						thread.start()
				elif path_segments[1] == "propagate":
					self.do_POST_Parameters(parameters, path_segments)
				elif path_segments[1] == "election":
					self.leader_election(parameters['leaderIp'][0], parameters['maxId'][0])

			# Set the response status code to 200 (OK)
			self.set_HTTP_headers(200)

		# Catch every possible exception
		except Exception as e:
			# Print error given by Python on the server console
			print e
			# Set retransimit to False avoiding the further propagation of other errors
			retransmit = False
			# Set the response status code to 400 (Bad Request)
			self.set_HTTP_headers(400)

		# If True the message needs to be propagate to the other servers
		if retransmit:
			# do_POST send the message only when the function finishes
			# Create threads to do some heavy computation
			# Check if it is a add request or a modify/delete request
			if 'delete' in parameters:
				thread = Thread(target=self.server.propagate_value_to_vessels, args=(self.path.replace("board","propagate"), parameters['entry'][0], parameters['delete'][0]))
			else:
				# If delete is not present in parameters (i.e. when a new value is inserted)
				# delete is passed as None and it will not be used
				thread = Thread(target=self.server.propagate_value_to_vessels, args=(self.path.replace("board","propagate"), parameters['entry'][0], None))			
			# Kill the process if we kill the server
			thread.daemon = True
			# Start the thread
			thread.start()
#------------------------------------------------------------------------------------------------------
# POST Logic - specific path: "/board..." or "/propagate..."
#------------------------------------------------------------------------------------------------------
	def do_POST_Parameters(self, parameters, path_segments):

		# If the path is exactly "/board" or "/propagate"
		if len(path_segments) == 2:
			# Call the method to add the value received in the server store
			self.server.add_value_to_store(parameters['entry'][0])
		# If the path is "/board/*" or "/propagate/*" where * is the id of the entry
		elif len(path_segments) == 3:
			if (parameters['delete'][0]) == "0":
				# Call the method to modify a value received in the server store
				self.server.modify_value_in_store(int(path_segments[2]), parameters['entry'][0])
			elif parameters['delete'][0] == "1":
				# Call the method to delete the value with the corresponding id from the server store 
				self.server.delete_value_in_store(int(path_segments[2]))
#------------------------------------------------------------------------------------------------------
# POST Logic - specific path: "/election"
#------------------------------------------------------------------------------------------------------
	# Leader election in ring
	def leader_election(self, leaderIp, maxId):

		# Initially, leader ← 0, leaderIp ← vesselIp, send maxId to clockwise neighbor
		# upon receiving maxId:
		# if maxId = vessel random id, set leader ← 1.
		# vessel also checks that random id belongs to itself rather than another vessel with the same random id
		if int(maxId) == self.server.leader['randId'] and int(leaderIp) == self.server.vessel_id:
			self.server.leader['leader'] = 1
			print 'I am the leader'
		# if maxId > vessel random id, set leaderIp ← maxId and send maxId to right neighbor
		# if two or more vassels have the same random id (unlikely but could happen), the first one that received the election message wins
		elif int(maxId) >= self.server.leader['randId']:
			self.server.leader['leaderIp'] = int(leaderIp)
			thread = Thread(target=self.server.contact_vessel_for_election, args=("10.1.0.%s" % (((self.server.vessel_id)%len(self.server.vessels))+1), "/election", int(leaderIp), int(maxId)))
			# Kill the process if we kill the server
			thread.daemon = True
			# Start the thread
			thread.start()
		# if maxId < leaderIp, send leaderIp to right neighbor
		elif int(maxId) < self.server.leader['randId']:
			thread = Thread(target=self.server.contact_vessel_for_election, args=("10.1.0.%s" % (((self.server.vessel_id)%len(self.server.vessels))+1), "/election", self.server.vessel_id, self.server.leader['randId']))
			# Kill the process if we kill the server
			thread.daemon = True
			# Start the thread
			thread.start()
#------------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------------
# Execute the code
if __name__ == '__main__':

	try:
		# Open all the HTML files
		file_header = open("server/board_frontpage_header_template.html", 'rU')
		file_boardcontents = open("server/boardcontents_template.html", 'rU')
		file_entry = open("server/entry_template.html", 'rU')
		file_footer = open("server/board_frontpage_footer_template.html", 'rU')
		
		# Read the templates from the corresponding HTML files
		board_frontpage_header_template = file_header.read()
		boardcontents_template = file_boardcontents.read()
		entry_template = file_entry.read()
		board_frontpage_footer_template = file_footer.read()

		# Close all the HTML template files
		file_header.close()
		file_boardcontents.close()
		file_entry.close()
		file_footer.close()

	except Exception as e:
		print "Problem with the HTML template files: " + str(e)

	vessel_list = []
	vessel_id = 0

	# Checking the arguments
	if len(sys.argv) != 3: # 2 args, the script and the vessel name
		print("Arguments: vessel_ID number_of_vessels")
	else:
		# We need to know the vessel IP
		vessel_id = int(sys.argv[1])
		# Write the other vessels IP, based on the knowledge of their number
		for i in range(1, int(sys.argv[2]) + 1):
			# Add server itself, test in the propagation
			vessel_list.append("10.1.0.%d" % i)

	# Launch server
	server = BlackboardServer(('', PORT_NUMBER), BlackboardRequestHandler, vessel_id, vessel_list)
	print("Starting the server on port %d" % PORT_NUMBER)

	try:
		# The first node in the vessel_list initiates the leader election sending its randomly generated ID to its next node
		if "10.1.0.%d" % vessel_id == vessel_list[0]:
			thread = Thread(target=server.contact_vessel_for_election, args=("10.1.0.%s" % (((vessel_id)%len(vessel_list))+1), "/election", vessel_id, server.leader['randId']))
			# Kill the process if we kill the server
			thread.daemon = True
			# Start the thread
			thread.start()

		server.serve_forever()

	except KeyboardInterrupt:
		server.server_close()
		print("Stopping Server")
#------------------------------------------------------------------------------------------------------
