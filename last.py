#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rpc
import time
import yaml
import pylast

config = yaml.load(open('config.yaml'))
wait = 60

try:
    rpc = rpc.DiscordIpcClient.for_platform(config['discord']['app_id'])
except:
    print('Connection to Discord RPC is failed. Discord is on, isn\'t?')
    exit(1)

try:
    lastfm = pylast.LastFMNetwork(api_key=config['lastfm']['key'],
                                  api_secret=config['lastfm']['secret'])
    user = lastfm.get_user(config['lastfm']['user'])
except:
    print('Connection to Last.fm is failed')
    exit(1)


def update_activity(status, icon, track, count):
    values = {
        'details': status + ':',
        'state': track,
        'assets': {
            'small_text': count + ' scrobbles!',
            'small_image': icon,
            'large_text': track,
            'large_image': 'logo'
        }
    }
    rpc.set_activity(values)


def update_rpc():
    count = str(user.get_playcount())
    track = user.get_now_playing()
    if track is not None:
        status = 'Now Playing'
        icon = 'play'
        track = str(track).replace('-', '–', 1)
        print('{}: {}'.format(status, track))
        update_activity(status, icon, track, count)
    else:
        status = 'Last Played'
        icon = 'pause'
        track = str(user.get_recent_tracks()[1][0]).replace('-', '–', 1)
        print ('{}: {}'.format(status, track))
        update_activity(status, icon, track, count)

while True:
    update_rpc()
    time.sleep(wait)
