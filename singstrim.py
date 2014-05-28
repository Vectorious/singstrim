from flask import Flask, render_template
from datetime import datetime, timedelta, timezone
import json

app = Flask(__name__)

@app.route('/')
def index():
	now, laststrim, update, live = get_last_strim()
	difference = now - laststrim
	return render_template(
		'index.html',
		years='{:f}'.format((difference.days + difference.seconds/86400) / 365),
		update=update.isoformat(' ')[:-13],	live=live,
		human_difference='{} days {} hours'.format(difference.days, difference.seconds//3600))

def sing_is_strimming():
	import requests
	return '"stream":null' not in requests.get('https://api.twitch.tv/kraken/streams/sing_sing').text

def get_last_strim():
	try:
		info = json.load(open('strim_info.json', 'r'))
	except IOError:
		info = {
			'lastupdate': 0.0,
			'laststrim': (datetime.now(timezone.utc) - timedelta(years=10)).timestamp(),
			'lastlive': False
		}
	now = datetime.now(timezone.utc)
	update = datetime.fromtimestamp(info['lastupdate'], timezone.utc)
	laststrim = datetime.fromtimestamp(info['laststrim'], timezone.utc)
	if (now - update).seconds >= 600:
		if sing_is_strimming():
			info['lastlive'] = True
		elif info['lastlive']:
			info['lastlive'] = False
			info['laststrim'] = info['lastupdate']
			laststrim = update
		info['lastupdate'] = now.timestamp()
		update = now
		json.dump(info, open('strim_info.json', 'w'))
	return now, laststrim, update, info['lastlive']

if __name__ == '__main__':
	app.run()