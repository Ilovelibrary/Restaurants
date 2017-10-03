from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

All = session.query(Restaurant).all()
for a in All:
	print a.name

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith('/hello'):
				self.send_response(200)
				self.send_header('content-type','text/html')
				self.end_headers()
				output = ''
				output += '<html><body>Hello!</body></html>'
				output += '<form method="POST" enctype="multipart/form-data" action="/action"><h2>What would like me to say</h2><input name="message" type="text"><input type="submit" value="Submit"></form>'
				self.wfile.write(output)
				print output
				return
			if self.path.endswith('/restaurants'):
				self.send_response(200)
				self.send_header('content-type','text/html')
				self.end_headers()
				output = ''
				output += '<html><body>'
				output += ('<a href="/restaurants/new">Make a New Restaurant Here</a>'+'</br><br>')
				Allrestaurants = session.query(Restaurant).all()
				for r in Allrestaurants:
					output += r.name + '</br>'
					output += ('<a href="/restaurants/%s/edit">Edit</a>' % str(r.id)+'</br>')
					output += ('<a href="/restaurants/%s/delete">Delete</a>' % str(r.id)+'</br>'+'</br>')
				output += '</body></html>'
				self.wfile.write(output)
				return
			if self.path.endswith('/restaurants/new'):
				self.send_response(200)
				self.send_header('content-type','text/html')
				self.end_headers()
				output = ''
				output += '<html><body>Make a New Restaurant</body></html>'
				output += '<form method="POST" enctype="multipart/form-data" action="/restaurants/new"><input name="restaurantname" type="text"><input type="submit" value="Submit"></form>'
				self.wfile.write(output)
				return
			if self.path.endswith('/edit'):
				restaurantID = self.path.split('/')[2]
				selectedRestaurant = session.query(Restaurant).filter_by(id = restaurantID).one()
				if selectedRestaurant!=[]:
					output = ''
					output += '<html><body>%s</body></html>' % selectedRestaurant.name
					output += '<form method="POST" enctype="multipart/form-data" action="/restaurants/%s/edit"><input name="restaurantname" type="text"><input type="submit" value="Submit"></form>' % restaurantID
					self.send_response(200)
					self.send_header('content-type','text/html')
					self.end_headers()
					self.wfile.write(output)
				return
			if self.path.endswith('/delete'):
				restaurantID = self.path.split('/')[2]
				selectedRestaurant = session.query(Restaurant).filter_by(id = restaurantID).one()
				if selectedRestaurant!=[]:
					output = ''
					output += '<html><body>%s</body></html>' % selectedRestaurant.name
					output += '<form method="POST" enctype="multipart/form-data" action="/restaurants/%s/delete">Do you want to delete %s?<input type="submit" value="Delete"></form>' % (restaurantID, selectedRestaurant.name)
					self.send_response(200)
					self.send_header('content-type','text/html')
					self.end_headers()
					self.wfile.write(output)
				return
		except IOError:
			self.send_error('404 not found')
	
	def do_POST(self):
		try:
			if self.path.endswith('/restaurants/new'):
				ctype,pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('restaurantname')
				
				newRestaurant = Restaurant(name = messagecontent[0])
				print type(newRestaurant), newRestaurant.name
				session.add(newRestaurant)
				session.commit()
				print 'committed!'
				self.send_response(301)
				self.send_header('content-type','text/html')
				self.send_header('Location','/restaurants')
				self.end_headers()
				return
			if self.path.endswith('/edit'):
				ctype,pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('restaurantname')
				restaurantID = self.path.split('/')[2]
				selectedRestaurant = session.query(Restaurant).filter_by(id = restaurantID).one()
				if selectedRestaurant!=[]:
					selectedRestaurant.name = messagecontent[0]
					session.add(selectedRestaurant)
					session.commit()
					print 'committed!'
					self.send_response(301)
					self.send_header('content-type','text/html')
					self.send_header('Location','/restaurants')
					self.end_headers()
					return
			if self.path.endswith('/delete'):
				restaurantID = self.path.split('/')[2]
				selectedRestaurant = session.query(Restaurant).filter_by(id = restaurantID).one()
				if selectedRestaurant!=[]:
					session.delete(selectedRestaurant)
					session.commit()
					print 'committed!'
					self.send_response(301)
					self.send_header('content-type','text/html')
					self.send_header('Location','/restaurants')
					self.end_headers()
					return
		except:
			pass


def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webserverHandler)
		print 'Web server running on port %s' % port
		server.serve_forever()
	except KeyboardInterrupt:
		print 'Quit'
		server.socket.close()
		

if __name__=='__main__':
	main()