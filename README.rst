IMAP Copy
=========

This is a very simple tool to copy folders from one IMAP server to another server.


Example:

::

    python imapcopy.py imap.googlemail.com username@googlemail.com:password \
    mail.example.com "christoph@example.com:password" \
    "[Google Mail]/Alle Nachrichten" DestinationFolder

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
      -q, --quiet       ppsssh... be quiet. (no output)
      -v, --verbose     more output please (debug level)
