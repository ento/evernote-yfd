#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import urllib


try:
    import config
except ImportError:
    import sys
    print 'cp config.sample config.py'
    sys.exit(1)
activate_this = os.path.join(
    os.path.dirname(__file__),
    getattr(config, 'VIRTUALENV_PATH', None) or 'env',
    'bin',
    'activate_this.py',
)
execfile(activate_this, dict(__file__=activate_this))


import oauth2 as oauth
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter
from evernote.edam.error.ttypes import EDAMSystemException


def get_note_store(token):
    for sandbox in (False, True):
        client = EvernoteClient(token=token, sandbox=sandbox)
        try:
            return client.get_note_store()
        except EDAMSystemException as e:
            if e.errorCode == 19:
                pause(e.rateLimitDuration)
        except:
            if not sandbox:
                print "Trouble accessing your evernote account with the provided developer token: '%s'" % token
                raise


def filter_notebooks(notebooks, includes=[], excludes=[]):
    notebook_names = {notebook.name: notebook for notebook in notebooks}
    if includes:
        notebooks = [notebook_names[name] for name in includes if name in notebook_names]
    if excludes:
        notebooks = [notebook for notebook in notebooks if not notebook.name in excludes]
    return notebooks


def find_note_counts(note_store, notebooks):
    note_counts = note_store.findNoteCounts(NoteFilter(), False)
    notebook_counts = note_counts.notebookCounts
    return [(notebook, notebook_counts.get(notebook.guid, 0)) for notebook in notebooks]


def track_yfd(action, *args):
    action = action.replace(' ', '-')
    message = u'd yfd {action} {args}'.format(action=action, args=' '.join(map(unicode, args)))
    tweet(message)


def tweet(message):
    oauth_req(
        'https://api.twitter.com/1.1/statuses/update.json',
        'POST',
        urllib.urlencode(dict(status=message)),
    )
    print message


def is_followed_by_yfd():
    friendship = json.loads(oauth_req('https://api.twitter.com/1.1/friendships/lookup.json?screen_name=yfd'))[0]
    return 'followed_by' in friendship['connections']


def oauth_req(url, http_method="GET", post_body=''):
    consumer = oauth.Consumer(key=config.TWITTER_CONSUMER_KEY, secret=config.TWITTER_CONSUMER_SECRET)
    token = oauth.Token(key=config.TWITTER_ACCESS_KEY, secret=config.TWITTER_ACCESS_SECRET)
    client = oauth.Client(consumer, token)
 
    resp, content = client.request(
        url,
        method=http_method,
        body=post_body,
    )
    return content


def main():
    if not is_followed_by_yfd():
        print 'warning: @yfd is not following you'
    note_store = get_note_store(config.EVERNOTE_DEVELOPER_TOKEN)
    notebooks = filter_notebooks(note_store.listNotebooks(), config.INCLUDE_NOTEBOOKS, config.EXCLUDE_NOTEBOOKS)
    notebook_counts = find_note_counts(note_store, notebooks)
    for notebook, count in notebook_counts:
        track_yfd(notebook.name, count)


if __name__ == '__main__':
    main()
