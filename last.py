#!/usr/bin/env python3


import sys
import rpc
import time
import yaml
import pylast


config = yaml.load(open('config.yaml'))
wait = 60


def log(message, n=0):
    timestamp = time.strftime('%H:%M:%S')
    types = {0: 'INFO',
             1: 'DONE',
             2: 'FAIL'}
    prompt = '[{}] [{}] {}'.format(timestamp, types[n], message)
    print(prompt)


print('\n! Last.fm to Discord Status')
print('! Github: https://github.com/flameshikari/lastfm-to-discord-status\n')


def init_api():
    try:
        global user, now_playing, rpc
        lastfm = pylast.LastFMNetwork(api_key=config['lastfm']['key'],
                                      api_secret=config['lastfm']['secret'])
        user = lastfm.get_user(config['lastfm']['user'])
        now_playing = user.get_now_playing()
        log('Connected to Last.fm API', 1)
    except Exception as a:
        log('Connection to Last.fm API is failed\n{}'.format(a), 2)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
    try:
        rpc = rpc.DiscordIpcClient.for_platform(config['discord']['app_id'])
        log('Connected to Discord RPC', 1)
    except Exception as b:
        log('Connection to Discord RPC is failed:\n{}'.format(b), 2)
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)


init_api()


def update_activity(artist, title, genre, icon, count):
    values = {
        'details': artist,
        'state': title,
        'assets': {
            'small_text': '{} scrobbles!'.format(count),
            'small_image': 'logo',
            'large_text': 'Yeah, {}!'.format(genre.lower()),
            'large_image': icon
        }
    }
    rpc.set_activity(values)


now_playing_init = True


while True:
    try:
        count = str(user.get_playcount())
        track = user.get_now_playing()
        if track is not None:
            artist = track.get_artist().get_name()
            title = track.get_title()
            genre = track.get_artist().get_top_tags()[0][0].get_name().title()
            status = 'Now Playing'
            icon = 'play'
            update_activity(artist, title, genre, icon, count)
        else:
            track = user.get_recent_tracks()[0][0]
            artist = track.get_artist().get_name()
            title = track.get_title()
            genre = track.get_artist().get_top_tags()[0][0].get_name().title()
            status = 'Last Played'
            icon = 'pause'
            update_activity(artist, title, genre, icon, count)
        if track != now_playing:
            now_playing = track
            log('{}: {}'.format(status, str(now_playing)))
        else:
            if now_playing_init is True:
                log('{}: {}'.format(status, str(now_playing)))
                now_playing_init = False
    except Exception as c:
            log('Error:\n{}. Restarting...'.format(c), 2)
            init_api()
            pass
    except KeyboardInterrupt:
        sys.exit(0)
    try:
        time.sleep(wait)
    except KeyboardInterrupt:
        sys.exit(0)
