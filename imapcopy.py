# -*- coding: utf-8 -*-
"""
    imapcopy

    Simple tool to copy folders from one IMAP server to another server.


    :copyright: (c) 2013 by Christoph Heer.
    :license: BSD, see LICENSE for more details.
"""

import sys
import imaplib
import logging
import argparse


class IMAP_Copy(object):

    source = {
        'host': 'localhost',
        'port': 993
    }
    source_auth = ()
    destination = {
        'host': 'localhost',
        'port': 993
    }
    destination_auth = ()
    mailbox_mapping = []

    def __init__(self, source_server, destination_server, mailbox_mapping,
                 source_auth=(), destination_auth=(), create_mailboxes=False):

        self.logger = logging.getLogger("IMAP_Copy")

        self.source.update(source_server)
        self.destination.update(destination_server)
        self.source_auth = source_auth
        self.destination_auth = destination_auth

        self.mailbox_mapping = mailbox_mapping
        self.create_mailboxes = create_mailboxes

    def _connect(self, target):
        data = getattr(self, target)
        auth = getattr(self, target + "_auth")

        self.logger.info("Connect to %s (%s)" % (target, data['host']))
        if data['port'] == 993:
            connection = imaplib.IMAP4_SSL(data['host'], data['port'])
        else:
            connection = imaplib.IMAP4(data['host'], data['port'])

        if len(auth) > 0:
            self.logger.info("Authenticate at %s" % target)
            connection.login(*auth)

        setattr(self, '_conn_%s' % target, connection)
        self.logger.info("%s connection established" % target)

    def connect(self):
        self._connect('source')
        self._connect('destination')

    def _disconnect(self, target):
        if not hasattr(self, '_conn_%s' % target):
            return

        connection = getattr(self, '_conn_%s' % target)
        if connection.state == 'SELECTED':
            connection.close()
            self.logger.info("Close mailbox on %s" % target)

        self.logger.info("Disconnect from %s server" % target)
        connection.logout()
        delattr(self, '_conn_%s' % target)

    def disconnect(self):
        self._disconnect('source')
        self._disconnect('destination')

    def copy(self, source_mailbox, destination_mailbox):
        # Connect to source and open mailbox
        status, data = self._conn_source.select(source_mailbox, True)
        if status != "OK":
            self.logger.error("Couldn't open source mailbox %s" %
                              source_mailbox)
            sys.exit(2)

        # Connect to destination and open or create mailbox
        status, data = self._conn_destination.select(destination_mailbox)
        if status != "OK" and not self.create_mailboxes:
            self.logger.error("Couldn't open destination mailbox %s" %
                              destination_mailbox)
            sys.exit(2)
        else:
            self.logger.info("Create destination mailbox %s" %
                             destination_mailbox)
            self._conn_destination.create(destination_mailbox)
            status, data = self._conn_destination.select(destination_mailbox)

        # Look for mails
        self.logger.info("Looking for mails in %s" % source_mailbox)
        status, data = self._conn_source.search(None, 'ALL')
        data = data[0].split()
        mail_count = len(data)

        self.logger.info("Start copy %s => %s (%d mails)" % (
                         source_mailbox, destination_mailbox, mail_count))
        progress_count = 0
        for msg_num in data:
            status, data = self._conn_source.fetch(msg_num, '(RFC822 FLAGS)')
            message = data[0][1]
            flags = data[1][8:][:-2]  # Not perfect.. Waiting for bug reports

            self._conn_destination.append(
                destination_mailbox, flags, None, message
            )

            progress_count += 1
            self.logger.info("Copy mail %d of %d" % (
                             progress_count, mail_count))

        self.logger.info("Copy complete %s => %s (%d mails)" % (
                         source_mailbox, destination_mailbox, mail_count))

    def run(self):
        try:
            self.connect()
            for source_mailbox, destination_mailbox in self.mailbox_mapping:
                self.copy(source_mailbox, destination_mailbox)
        finally:
            self.disconnect()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source',
                        help="Source host ex. imap.googlemail.com:993")
    parser.add_argument('source_auth', metavar='source-auth',
                        help="Source host authentication ex. "
                             "username@host.de:password")

    parser.add_argument('destination',
                        help="Destination host ex. imap.otherhoster.com:993")
    parser.add_argument('destination_auth', metavar='destination-auth',
                        help="Destination host authentication ex. "
                             "username@host.de:password")

    parser.add_argument('mailboxes', type=str, nargs='+',
                        help='List of mailboxes alternate between source '
                             'mailbox and destination mailbox.')
    parser.add_argument('-c', '--create-mailboxes', dest='create_mailboxes',
                        action="store_true", default=False,
                        help='Create the mailboxes on destination')
    parser.add_argument('-q', '--quiet', action="store_true", default=False,
                        help='ppsssh... be quiet. (no output)')
    parser.add_argument('-v', '--verbose', action="store_true", default=False,
                        help='more output please (debug level)')

    args = parser.parse_args()

    _source = args.source.split(':')
    source = {'host': _source[0]}
    if len(_source) > 1:
        source['port'] = _source[1]

    _destination = args.destination.split(':')
    destination = {'host': _destination[0]}
    if len(_destination) > 1:
        destination['port'] = _destination[1]

    source_auth = tuple(args.source_auth.split(':'))
    destination_auth = tuple(args.destination_auth.split(':'))

    if len(args.mailboxes) % 2 != 0:
        print "Not valid count of mailboxes!"
        sys.exit(1)

    mailbox_mapping = zip(args.mailboxes[::2], args.mailboxes[1::2])

    imap_copy = IMAP_Copy(source, destination, mailbox_mapping, source_auth,
                          destination_auth,
                          create_mailboxes=args.create_mailboxes)

    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    imap_copy.logger.addHandler(streamHandler)

    if not args.quiet:
        streamHandler.setLevel(logging.INFO)
        imap_copy.logger.setLevel(logging.INFO)
    if args.verbose:
        streamHandler.setLevel(logging.DEBUG)
        imap_copy.logger.setLevel(logging.DEBUG)

    try:
        imap_copy.run()
    except KeyboardInterrupt:
        imap_copy.disconnect()

if __name__ == '__main__':
    main()
