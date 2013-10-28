# evernote-yfd

Track Evernote note counts per notebook using your.flowingdata.com.

1. Get a Twitter account.
1. Follow @yfd and wait for it to follow you back.
1. Prepare a virtualenv

```
$ virtualenv env
$ pip install -r requirements.txt
```

1. Fill in the required config values.

```
$ cp config.py.sample config.py
```

1. Test your setup.

```
$ ./track_note_counts.py
```

1. Modify the launchd plist file according to your environment and requirements.

```
$ cp evernote-yfd.track-note-counts.plist.sample evernote-yfd.track-note-counts.plist
```

1. Load the launchd plist. (I use lunchy)

```
$ gem install lunchy
$ lunchy install evernote-yfd.track-note-counts.plist
$ lunchy start -w evernote-yfd.track-note-counts
```
