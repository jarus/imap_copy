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
                 source_auth=(), destination_auth=()):

        self.logger = logging.getLogger("IMAP_Copy")

        self.source.update(source_server)
        self.destination.update(destination_server)
        self.source_auth = source_auth
        self.destination_auth = destination_auth

        self.mailbox_mapping = mailbox_mapping

    def _connect(self, target):
        _data = getattr(self, target)
        _auth = getattr(self, target + "_auth")

        self.logger.info("Connect to %s (%s)" % (target, _data['host']))
        if _data['port'] == 993:
            connection = imaplib.IMAP4_SSL(_data['host'], _data['port'])
        else:
            connection = imaplib.IMAP4(_data['host'], _data['port'])

        if len(_auth) > 0:
            self.logger.info("Authenticate at %s" % target)
            connection.login(*_auth)

        setattr(self, '_conn_%s' % target, connection)
        self.logger.info("%s connection established" % target)

    def connect(self):
        self._connect('source')
        self._connect('destination')

    def copy(self, source_mailbox, destination_mailbox):
        status, data = self._conn_source.select(source_mailbox)
        if status != "OK":
            self.logger.error(data[0])
            sys.exit(2)

        status, data = self._conn_destination.select(destination_mailbox)
        if status != "OK":
            self.logger.error(data[0])
            sys.exit(2)

        self.logger.info("Looking for mails in %s" % source_mailbox)
        status, data = self._conn_source.search(None, 'ALL')
        data = data[0].split()
        mail_count = len(data)

        self.logger.info("Start copy %s => %s (%d mails)" % (
                         source_mailbox, destination_mailbox, mail_count))
        progress_count = 0
        for msg_num in data:
            status, data = self._conn_source.fetch(msg_num, '(RFC822)')
            self._conn_destination.append(
                destination_mailbox, None, None, data[0][1]
            )

            progress_count += 1
            self.logger.info("Copy mail %d of %d" % (
                             progress_count, mail_count))

        self.logger.info("Copy complete %s => %s (%d mails)" % (
                         source_mailbox, destination_mailbox, mail_count))

    def run(self):
        self.connect()
        for source_mailbox, destination_mailbox in self.mailbox_mapping:
            self.copy(source_mailbox, destination_mailbox)


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
                          destination_auth)

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

    imap_copy.run()

if __name__ == '__main__':
    main()
