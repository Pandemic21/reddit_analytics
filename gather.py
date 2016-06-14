import pprint
import json
import requests
import time
import sqlite3

def get_reddits(params):
	while True:
		resp = requests.get(REDDITS_URL, params=params)
		if resp.status_code == 429:
			time.sleep(1)
		else:
			return resp.json()

def get_traffic_stats(subreddit):
	url = 'https://www.reddit.com' + subreddit + 'about/traffic.json'

	while True:
		resp = requests.get(url, params=params)
		if resp.status_code == 429:
			time.sleep(1)
		else:
			return resp.json() 

def get_json_traffic_stats(data):
	data = str(data).replace("u'", "'")
	data = str(data).replace("'", '"')
	return json.loads(data)


### MAIN ###########################################################
conn = sqlite3.connect('/home/pandemic/Documents/scripts/reddit_analytics/gather.db')

c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS reddits (\
	url text, \
	subscribers integer, \
	over18 text, \
	public_description text, \
	public_traffic text, \
	quarantine text, \
	subreddit_type text, \
	created_utc integer, \
	traffic_stats text)")
conn.commit()

REDDITS_URL = 'https://www.reddit.com/reddits.json'
headers = {'user-agent': 'Reddit analysis by /u/Pandemic21'}
current = 0
limit = 100
total = 1000
params = {"limit": limit}

f = open("reddits.log", "a")
saved_after = open("saved_after.log", "a")

#get_traffic_stats(reddits['data']['children'][0]['data']['url'])

reddits = get_reddits(params)

k = 0
while k < limit:
	f.write(reddits['data']['children'][k]['data']['url'] + '\n')

	# if the subreddit has public traffic stats, get them
	if reddits['data']['children'][k]['data']['public_traffic'] == True:
		time.sleep(1)
		c.execute("INSERT INTO reddits VALUES (?,?,?,?,?,?,?,?,?)", ( \
			reddits['data']['children'][k]['data']['url'], \
			int(reddits['data']['children'][k]['data']['subscribers']), \
			reddits['data']['children'][k]['data']['over18'], \
			reddits['data']['children'][k]['data']['public_description'], \
			reddits['data']['children'][k]['data']['public_traffic'], \
			reddits['data']['children'][k]['data']['quarantine'], \
			reddits['data']['children'][k]['data']['subreddit_type'], \
			int(reddits['data']['children'][k]['data']['created_utc']), \
			str(get_traffic_stats(reddits['data']['children'][k]['data']['url'])), \
			))
	# if the subreddit does not have public traffic stats, insert ""
	else:
		c.execute("INSERT INTO reddits VALUES (?,?,?,?,?,?,?,?,?)", ( \
			reddits['data']['children'][k]['data']['url'], \
			int(reddits['data']['children'][k]['data']['subscribers']), \
			reddits['data']['children'][k]['data']['over18'], \
			reddits['data']['children'][k]['data']['public_description'], \
			reddits['data']['children'][k]['data']['public_traffic'], \
			reddits['data']['children'][k]['data']['quarantine'], \
			reddits['data']['children'][k]['data']['subreddit_type'], \
			int(reddits['data']['children'][k]['data']['created_utc']), \
			""
			))
	conn.commit()
	k = k + 1


current = current + limit
print str(int(float(current)/total*100)) + "%\t" + str(current) + " reddits found"
time.sleep(10)

while current < total:
	params = {"limit": limit, "after": reddits['data']['after']}
	reddits = get_reddits(params)
	k = 0
	while k < limit:
		f.write(reddits['data']['children'][k]['data']['url'] + '\n')
		k = k + 1
	current = current + limit
	print str(int(float(current)/total*100)) + "%\t" + str(current) + " reddits found"
	saved_after.write(reddits['data']['after'] + "\n")
	time.sleep(10)

print "Ended on " + reddits['data']['after']
f.write("Ended on " + reddits['data']['after'])






