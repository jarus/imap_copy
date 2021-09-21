IMAP Copy
=========

A simple utility to copy folders between IMAP mail servers.

It only requires standard Python 3.5 or later.

Examples
--------

Assume you have, for example, a Gmail account and want to copy its folders to ``otherserver``.
You can use the IMAP protocol on both servers, **provided IMAP access is enabled on Gmail**.
Generally, you can copy folders and their contents between any two IMAP-enabled email servers.

Testing the connection and credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before actually copying messages, test the IMAP connection and credentials to both the source
server and your ``otherserver``; if the connection succeeds, IMAP folder names found on both servers
will be listed:

::

    python3 imapcopy.py \
      --test \
      "imap.googlemail.com:993"     "username@gmail.com:password" \
      "imap.otherserver.com.au:993" "username:password"

Copying messages from folders
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      
To copy all the messages from, say, the ``INBOX`` folder of Gmail to the ``Inbox`` folder
of your ``otherserver``:

::

    python3 imapcopy.py \
      --verbose \
      "imap.googlemail.com:993"     "username@gmail.com:password" \
      "imap.otherserver.com.au:993" "username:password" \
      "INBOX" "Inbox"

You can provide many folders to copy; alternating between source and destination.
For example, to copy from ``INBOX`` to ``Inbox`` and from ``[Gmail]/Sent Mail``
to ``Sent``:

::

    python3 imapcopy.py \
      --verbose \
      "imap.googlemail.com:993"     "username@gmail.com:password" \
      "imap.otherserver.com.au:993" "username:password" \
      "INBOX"              "Inbox" \
      "[Gmail]/Sent Mail"  "Sent"

Copying a range of messages from a folder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since Gmail throttles uploading and downloading email messages over IMAP, you 
may find the ``--skip`` and ``--limit`` options handy. For instance, If Gmail
disconnects you after copying 123 email messages out of your total 1000
messages in the example shown above, you may use the following command to
resume copying skipping the first 123 messages:

::

    python3 imapcopy.py \
      –-skip 123 \
      "imap.googlemail.com:993"     "username@gmail.com:password" \
      "imap.otherserver.com.au:993" "username:password" \
      "INBOX" "Inbox"

Similarly, the ``--limit`` option allows you to copy only at most ``N`` messages
excluding the skipped messages. For example, the following command will copy
messages number 124 through 223 from Gmail:

::

    python3 imapcopy.py \
       --skip 123 --limit 100 \
      "imap.googlemail.com:993"     "username@gmail.com:password" \
      "imap.otherserver.com.au:993" "username:password" \
      "INBOX" "Inbox"

Copying all folders and sub-folders from a server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``--recurse`` option copies the contents of a folder and its sub-folders.
Also, if you use an empty string ``""`` as the source ``folder``, all the folders in
the source server  will be copied to the destination.

:: 

    python3 imapcopy.py \
      --recurse \
      "imap.googlemail.com:993"     "username@gmail.com:password" \
      "imap.otherserver.com.au:993" "username:password" \
      ""   "Imported"

Usage
-----

::
   
    usage: imapcopy.py [-h] [-t] [-c] [-r] [-q] [-v] [-s N] [-l N] source source-auth destination destination-auth [folders ...]

    positional arguments:
    source                source host, e.g. imap.googlemail.com:993
    source-auth           source host credentials, e.g. username@host.de:password
    destination           destination host, e.g. imap.otherhoster.com:993
    destination-auth      destination host credentials, e.g. username@host.de:password
    folders               list of folders, alternating between source folder and destination folder

    optional arguments:
    -h, --help            show this help message and exit
    -t, --test            do not copy, only test connections to source and destination
    -c, --create-folders  create folders on destination
    -r, --recurse         recurse into sub-folders
    -q, --quiet           be quiet, print no output
    -v, --verbose         print debug-level output
    -s N, --skip N        skip the first N message(s)
    -l N, --limit N       only copy at most N message(s)
