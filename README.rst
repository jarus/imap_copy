IMAP Copy
=========

This is a very simple tool to copy folders from one IMAP server to another server.


Example:

::

    python imapcopy.py "imap.servername.com.au:993" "username:password" \
    "imap.googlemail.com:993" "username@gmail.com:password" \
    "INBOX" "[Google Mail]/All Mail"

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
      -q, --quiet       ppsssh... be quiet. (no output)
      -v, --verbose     more output please (debug level)
      -s N, --skip N    skip the first N message(s)
      -l N, --limit N   only copy N number of message(s)
  
Only tested on Python 2.7.4.
