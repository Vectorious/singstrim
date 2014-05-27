from flask import Flask, render_template
from datetime import datetime, timedelta, timezone
import json

app = Flask(__name__)

@app.route('/')
def index():
	now, laststrim, update, live = get_last_strim()
	update = update.isoformat(' ')[:-13]
	difference = now - laststrim
	years = '{:f}'.format((difference.days + difference.seconds/86400) / timedelta(365).days)
	human_difference = '{} days {} hours'.format(difference.days, difference.seconds//3600)
	return render_template('index.html', years=years, update=update, live=live, human_difference=human_difference)

def get_last_strim():
	try:
		info = json.load(open('strim_info.json', 'r'))
	except IOError:
		info = {
			'lastupdate': 0.0,
			'laststrim': 0.0,
			'lastlive': False
		}
	now = datetime.now(timezone.utc)
	update = datetime.fromtimestamp(info['lastupdate'], timezone.utc)
	laststrim = datetime.fromtimestamp(info['laststrim'], timezone.utc)
	live = info['lastlive']
	if (now - update).seconds >= 600:
		if sing_is_strimming():
			info['lastlive'] = live = True
		elif live:
			info['lastlive'] = live = False
			info['laststrim'] = info['lastupdate']
			laststrim = update
		info['lastupdate'] = now.timestamp()
		update = now
		json.dump(info, open('strim_info.json', 'w'))
	return now, laststrim, update, live

def sing_is_strimming():
	import requests
	return '"stream":null' not in requests.get('https://api.twitch.tv/kraken/streams/sing_sing').text

if __name__ == '__main__':
	app.run()