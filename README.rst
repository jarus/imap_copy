IMAP Copy
=========

This is a very simple tool to copy folders from one IMAP server to another server.


Example:

The example below copies all messages from the INBOX of your other server into
the 'OTHER-SERVER/Inbox' folder of Gmail.

::

    python imapcopy.py "imap.otherserver.com.au:993" "username:password" \
    "imap.googlemail.com:993" "username@gmail.com:password" \
    "INBOX" "OTHER-SERVER/Inbox" --verbose

Since Gmail terribly throttles uploading and downloading mails over IMAP, you 
may find the 'skip' and 'limit' options handy. If Gmail disconnected you after
copying 123 emails out of your total 1000 emails in the example shown above, 
you may use the following command to resume copying skipping the first 123 
messages.

::

    python imapcopy.py "imap.otherserver.com.au:993" "username:password" \
    "imap.googlemail.com:993" "username@gmail.com:password" \
    "INBOX" "OTHER-SERVER/Inbox" --skip 123

Similarly the 'limit' option allows you to copy only the N number of messages
excluding the skipped messages. For example, the following command will copy
message no. 124 to 223 into Gmail.

::

    python imapcopy.py "imap.otherserver.com.au:993" "username:password" \
    "imap.googlemail.com:993" "username@gmail.com:password" \
    "INBOX" "OTHER-SERVER/Inbox" --skip 123 --limit 100

There is also 'recurse' option that copies contents of folders with all of
its subfolders. Also if you replace source mailbox with empty string, it will
copy all contents of that mailbox:

:: 

    python imapcopy.py "imap.otherserver.com.au:993" "username:password" \
    "imap.googlemail.com:993" "username@gmail.com:password" \
    "" "OTHER-SERVER" --recurse

Usage:

::

    usage: imapcopy.py [-h] [-q] [-v]
                   source source-auth destination destination-auth mailboxes
                   [mailboxes ...]

    positional arguments:
      source            Source host ex. imap.googlemail.com:993
      source-auth       Source host authentication ex. username@host.de:password
      destination       Destination host ex. imap.otherhoster.com:993
      destination-auth  Destination host authentication ex.
                        username@host.de:password
      mailboxes         List of mailboxes alternate between source mailbox and
                        destination mailbox.

    optional arguments:
      -h, --help        show this help message and exit
      -c, --create-mailboxes
                        Create the mailboxes on destination
      -r, --recurse     Recurse into submailboxes
      -q, --quiet       ppsssh... be quiet. (no output)
      -v, --verbose     more output please (debug level)
      -s N, --skip N    skip the first N message(s)
      -l N, --limit N   only copy N number of message(s)
  
Only tested on Python 2.7.
