#!/usr/bin/python
"""
AdvancedTorSQL
v2.0 by maddux
"""

#import sqlalchemy as sql

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

OKAY = "\002\00303TOR AUTH MESSAGE\003: \002"
WARN = "\002\00308TOR AUTH WARNING\003: \002"
CRIT = "\002\00304TOR AUTH CRITICAL\003: \002"
COMMANDCHAN = "#command"
db = create_engine('mysql://user:password@host:port/db_name')
Base = declarative_base()
Session = sessionmaker(bind=db)

class User(Base):
	__tablename__ = 'torusers'
	id = Column(Integer, primary_key=True)
	ident = Column(String)
	hash = Column(String)
	comment = Column(String)

	def __init__(self,ident,hash,comment):
		self.ident = ident
		self.hash = hash
		self.comment = comment

	def __repr__(self):
		return "<User('%r',%r',%r')>" % (self.ident, self.hash, self.comment)

def afind(phenny, input):
	if input.sender != COMMANDCHAN: return
	session = Session()
	qry = input.group(2)
	if qry:
		count = 0
		for instance in session.query(User).filter_by(ident=qry):
			msg = str(instance.id)+', '+str(instance.ident)+', '+str(instance.hash)+', '+str(instance.comment)
			count += 1
			phenny.say(OKAY+msg)
		for instance in session.query(User).filter_by(hash=qry):
			msg = str(instance.id)+', '+str(instance.ident)+', '+str(instance.hash)+', '+str(instance.comment)
			count += 1
			phenny.say(OKAY+msg)
		for instance in session.query(User).filter_by(comment=qry):
			msg = str(instance.id)+', '+str(instance.ident)+', '+str(instance.hash)+', '+str(instance.comment)
			count += 1
			phenny.say(OKAY+msg)
		if count == 1:
			phenny.say('1 match found.')
		else:
			phenny.say(str(count)+' matches found.')
	else:
		phenny.say('No arguments given.')
afind.commands = ['afind']

def aadd(phenny, input):
	if input.sender != COMMANDCHAN: return
	if not input.group(2):
		phenny.say('No arguments given. Usage: .aadd <ident> <hash> [comment]')
		return
	if not " " in input.group(2):
		phenny.say('Need more than one argument. Usage: .aadd <ident> <hash> [comment]')
		return
	qry = input.group(2).split()
	if len(qry[1]) != 64:
		phenny.say(CRIT+"Hash length does not match. Aborting.")
		return
	ahash = qry[1]
	aident = (qry[0][:10]) if len(qry[0]) > 10 else qry[0]
	if len(qry[0]) > 10:
		msg = "Ident more than 10 characters. Truncating to "+aident+"."
		phenny.say(WARN+msg)
	if len(qry) < 3: acomment = ""
	if len(qry) == 3: acomment = qry[2]
	if len(qry) > 3:
		acomment = ' '.join(qry[2:])
	session = Session()
	for instance in session.query(User).filter_by(ident=aident):
		msg = str(instance.id)+', '+str(instance.ident)+', '+str(instance.hash)+', '+str(instance.comment)
		if qry[1] == str(instance.hash):
			phenny.say(CRIT+"ident with corresponding hash already in database:")
			phenny.say(CRIT+msg)
			phenny.say(CRIT+"Aborting.")
			return
		phenny.say(WARN+"ident already exists in database:")
		phenny.say(WARN+msg)
	add_user = User(aident,ahash,acomment)
	session.add(add_user)
	session.commit()
	phenny.say(OKAY+"User added:")
	phenny.say(OKAY+aident+", "+ahash+", "+acomment)
aadd.commands = ['aadd']

def adel(phenny, input):
	if input.sender != COMMANDCHAN: return
	if not input.group(2):
		phenny.say('No argument given. Usage: .adel <ID>')
		return
	try:
		aid = int(input.group(2))
	except ValueError:
		phenny.say(CRIT+'ID must be an Integer. Usage: .adel <id>')
		return
	if aid < 1:
		phenny.say(CRIT+'Index Error.')
		return
	session = Session()
	for instance in session.query(User).filter_by(id=aid):
		msg = str(instance.id)+', '+str(instance.ident)+', '+str(instance.hash)+', '+str(instance.comment)
		phenny.say(OKAY+'Deleting:')
		phenny.say(OKAY+msg)
		session.delete(instance)
		session.commit()
		phenny.say(OKAY+'User deleted.')
		return
	phenny.say(CRIT+'ID not found.')
adel.commands = ['adel']

def achgident(phenny, input):
	if input.sender != COMMANDCHAN: return
	if not input.group(2):
		phenny.say('No argument given. Usage: .adel <ID>')
		return
	qry = input.group(2).split()
	try:
		aid = int(qry[0])
	except ValueError:
		phenny.say(CRIT+'ID must be an Integer. Usage: .achgident <id> <newident>')
		return
	aident = qry[1]
	if aid < 1:
		phenny.say(CRIT+'Index Error.')
		return
	session = Session()
	for instance in session.query(User).filter_by(id=aid):
		msg = str(instance.id)+', '+str(instance.ident)+', '+str(instance.hash)+', '+str(instance.comment)
		phenny.say(OKAY+'Old entry:')
		phenny.say(OKAY+msg)
		phenny.say(OKAY+'New entry:')
		msg = str(instance.id)+', '+aident+', '+str(instance.hash)+', '+str(instance.comment)
		phenny.say(OKAY+msg)
		instance.ident = aident
		session.commit()
		phenny.say(OKAY+'User updated.')
		return
	phenny.say(CRIT+'ID not found')
achgident.commands = ['achgident']

def achghash(phenny, input):
	if input.sender != COMMANDCHAN: return
	if not input.group(2):
		phenny.say('No argument given. Usage: .adel <ID>')
		return
	qry = input.group(2).split()
	try:
		aid = int(qry[0])
	except ValueError:
		phenny.say(CRIT+'ID must be an Integer. Usage: .achghash <id> <newhash>')
		return
	ahash = qry[1]
	if aid < 1:
		phenny.say(CRIT+'Index Error.')
		return
	session = Session()
	for instance in session.query(User).filter_by(id=aid):
		msg = str(instance.id)+', '+str(instance.ident)+', '+str(instance.hash)+', '+str(instance.comment)
		phenny.say(OKAY+'Old entry:')
		phenny.say(OKAY+msg)
		phenny.say(OKAY+'New entry:')
		msg = str(instance.id)+', '+str(instance.ident)+', '+ahash+', '+str(instance.comment)
		phenny.say(OKAY+msg)
		instance.hash = ahash
		session.commit()
		phenny.say(OKAY+'User updated.')
		return
	phenny.say(CRIT+'ID not found')
achghash.commands = ['achghash']

def achgcomment(phenny, input):
	if input.sender != COMMANDCHAN: return
	if not input.group(2):
		phenny.say('No argument given. Usage: .adel <ID>')
		return
	qry = input.group(2).split()
	if len(qry) > 2:
		acomment = ' '.join(qry[1:])
	else:
		acomment = qry[1]
	try:
		aid = int(qry[0])
	except ValueError:
		phenny.say(CRIT+'ID must be an Integer. Usage: .achgcomment <id> <newcomment>')
		return
	if aid < 1:
		phenny.say(CRIT+'Index Error.')
		return
	session = Session()
	for instance in session.query(User).filter_by(id=aid):
		msg = str(instance.id)+', '+str(instance.ident)+', '+str(instance.hash)+', '+str(instance.comment)
		phenny.say(OKAY+'Old entry:')
		phenny.say(OKAY+msg)
		phenny.say(OKAY+'New entry:')
		msg = str(instance.id)+', '+str(instance.ident)+', '+str(instance.hash)+', '+acomment
		phenny.say(OKAY+msg)
		instance.comment = acomment
		session.commit()
		phenny.say(OKAY+'User updated.')
		return
	phenny.say(CRIT+'ID not found')
achgcomment.commands = ['achgcomment']


