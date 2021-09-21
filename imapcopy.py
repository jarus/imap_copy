# -*- coding: utf-8 -*-
"""
    imapcopy

    Simple tool to copy folders from one IMAP server to another server.


    :copyright: (c) 2013 by Christoph Heer.
    :license: BSD, see LICENSE for more details.
"""

import sys
import hashlib
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
    folder_mapping = []

    def __init__(self, source_server, destination_server, folder_mapping,
                 source_auth=(), destination_auth=(), create_folders=False,
                 recurse=False, skip=0, limit=0):

        self.logger = logging.getLogger("IMAP_Copy")

        self.source.update(source_server)
        self.destination.update(destination_server)
        self.source_auth = source_auth
        self.destination_auth = destination_auth

        self.folder_mapping = folder_mapping
        self.create_folders = create_folders

        self.skip = skip
        self.limit = limit

        self.recurse = recurse

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
        # Detecting delimiter on destination server
        code, folder_list = connection.list()

        folder_name_list = []
        for box in folder_list:
            parts = box.decode('utf-8').split('"')
            if len(parts) == 5:
                folder_name_list.append(parts[3].strip())
            elif len(parts) == 3:
                folder_name_list.append(parts[2].strip())

        folder_names = ', '.join(folder_name_list)
        self.logger.info("%s has the following folders: %s" % (target, folder_names))

        self.delimiter = folder_list[0].split(b'"')[1]

    def connect(self):
        self._connect('source')
        self._connect('destination')

    def _disconnect(self, target):
        if not hasattr(self, '_conn_%s' % target):
            return

        connection = getattr(self, '_conn_%s' % target)
        if connection.state == 'SELECTED':
            connection.close()
            self.logger.info("Close folder on %s" % target)

        self.logger.info("Disconnect from %s server" % target)
        connection.logout()
        delattr(self, '_conn_%s' % target)

    def disconnect(self):
        self._disconnect('source')
        self._disconnect('destination')

    def copy(self, source_folder, destination_folder, skip, limit, recurse=True):

        # There should be no files stored in / so we are bailing out
        if source_folder == '':
            return

        # Connect to source and open folder
        status, data = self._conn_source.select(source_folder, True)
        if status != "OK":
            self.logger.error("Couldn't open source folder %s" %
                              source_folder)
            sys.exit(2)

        # Connect to destination and open or create folder
        status, data = self._conn_destination.select(destination_folder)
        if status != "OK" and not self.create_folders:
            self.logger.error("Couldn't open destination folder %s" %
                              destination_folder)
            sys.exit(2)
        else:
            self.logger.info("Create destination folder %s" %
                             destination_folder)
            self._conn_destination.create(destination_folder)
            status, data = self._conn_destination.select(destination_folder)

        # Look for mails
        self.logger.info("Looking for mail in %s" % source_folder)
        status, data = self._conn_source.search(None, 'ALL')
        data = data[0].split()
        mail_count = len(data)

        self.logger.info("Start copy %s => %s (%d mails)" % (
            source_folder, destination_folder, mail_count))

        progress_count = 0
        copy_count = 0

        for msg_num in data:
            progress_count += 1
            if progress_count <= skip:
                self.logger.info("Skipping mail %d of %d" % (
                    progress_count, mail_count))
                continue
            else:
                status, data = self._conn_source.fetch(msg_num, '(RFC822 FLAGS INTERNALDATE)')

                flags_line = data[0][0].decode('ascii')
                if flags_line.find('FLAGS') < 0 and len(data) > 1:
                    flags_line = data[1].decode('ascii')
                message = data[0][1]

                flags_start = flags_line.index('FLAGS (') + len('FLAGS (')
                flags_end = flags_line.index(')', flags_start)

                flags = '(' + flags_line[flags_start:flags_end] + ')'

                internaldate_start = flags_line.index('INTERNALDATE ') + len('INTERNALDATE ')
                internaldate_end = flags_line.find(' RFC822', internaldate_start)
                if internaldate_end < 0:
                    internaldate_end = flags_line.find(' FLAGS', internaldate_start)
                if internaldate_end < 0:
                    internaldate_end = flags_line.find(')', internaldate_start)
                if internaldate_end < 0:
                    internaldate_end = len(flags_line)

                internaldate = flags_line[internaldate_start:internaldate_end]

                self._conn_destination.append(
                    destination_folder, flags, internaldate, message,
                )

                copy_count += 1
                message_sha1 = hashlib.sha1(message).hexdigest()

                self.logger.info("Copy mail %d of %d (copy_count=%d, sha1(message)=%s)" % (
                    progress_count, mail_count, copy_count, message_sha1))

                if limit > 0 and copy_count >= limit:
                    self.logger.info("Copy limit %d reached (copy_count=%d)" % (
                        limit, copy_count))
                    break

        self.logger.info("Copy complete %s => %s (%d out of %d messages copied)" % (
            source_folder, destination_folder, copy_count, mail_count))

        if self.recurse and recurse:
            self.logger.info("Getting list of folders under %s" % source_folder)
            connection = self._conn_source
            typ, data = connection.list(source_folder)
            for d in data:
                if d:
                    l_resp = d.split('"')
                    # response = '(\HasChildren) "/" INBOX'
                    if len(l_resp) == 3:

                        source_mbox = d.split('"')[2].strip()
                        # make sure we don't have a recursive loop
                        if source_mbox != source_folder:
                            # maybe better use regex to replace only start of the souce name
                            dest_mbox = source_mbox.replace(source_folder, destination_folder)
                            self.logger.info("starting copy of folder %s to %s " % (source_mbox, dest_mbox))
                            self.copy(source_mbox, dest_mbox, skip, limit, False)

    def run(self):
        try:
            self.connect()
            for source_folder, destination_folder in self.folder_mapping:

                if ' ' in source_folder and '"' not in source_folder:
                    source_folder = '"%s"' % source_folder
                if ' ' in destination_folder and '"' not in destination_folder:
                    destination_folder = '"%s"' % destination_folder

                self.copy(source_folder, destination_folder, self.skip, self.limit)
        finally:
            self.disconnect()

    def test_connections(self):
        self.logger.info("Testing connections to source and destination")
        try:
            self.connect()
            self.logger.info("Test OK")
        except Exception as e:
            self.logger.error("Connection error: %s" % str(e))
        finally:
            self.disconnect()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('source',
                        help="source host, e.g. imap.googlemail.com:993")

    parser.add_argument('source_auth', metavar='source-auth',
                        help="source host credentials, e.g. username@host.de:password")

    parser.add_argument('destination',
                        help="destination host, e.g. imap.otherhoster.com:993")

    parser.add_argument('destination_auth', metavar='destination-auth',
                        help="destination host credentials, e.g. username@host.de:password")

    parser.add_argument('folders', type=str, nargs='*',
                        help="list of folders, alternating between source folder and destination folder")

    parser.add_argument('-t', '--test', dest='test_connections',
                        action="store_true", default=False,
                        help="do not copy, only test connections to source and destination")

    parser.add_argument('-c', '--create-folders', dest='create_folders',
                        action="store_true", default=False,
                        help="create folders on destination")

    parser.add_argument('-r', '--recurse', dest='recurse',
                        action="store_true", default=False,
                        help="recurse into subfolders")

    parser.add_argument('-q', '--quiet', action="store_true", default=False,
                        help="be quiet, print no output")

    parser.add_argument('-v', '--verbose', action="store_true", default=False,
                        help="print debug-level output")

    def check_negative(value):
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError("%s is an invalid positive integer value" % value)
        return ivalue

    parser.add_argument("-s", "--skip", default=0, metavar="N", type=check_negative,
                        help="skip the first N message(s)")

    parser.add_argument("-l", "--limit", default=0, metavar="N", type=check_negative,
                        help="only copy at most N message(s)")

    args = parser.parse_args()

    _source = args.source.split(':')
    source = {'host': _source[0]}
    if len(_source) > 1:
        source['port'] = int(_source[1])

    _destination = args.destination.split(':')
    destination = {'host': _destination[0]}
    if len(_destination) > 1:
        destination['port'] = int(_destination[1])

    source_auth = tuple(args.source_auth.split(':'))
    destination_auth = tuple(args.destination_auth.split(':'))

    if not args.test_connections:
        if len(args.folders) < 2:
            print("Missing folders")
            sys.exit(1)
        elif len(args.folders) % 2 != 0:
            print("Please provide an even number of folders")
            sys.exit(1)

    folder_mapping = list(zip(args.folders[::2], args.folders[1::2]))

    imap_copy = IMAP_Copy(source, destination, folder_mapping, source_auth,
                          destination_auth, create_folders=args.create_folders,
                          recurse=args.recurse, skip=args.skip, limit=args.limit)

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
        if args.test_connections:
            imap_copy.test_connections()
        else:
            imap_copy.run()
    except KeyboardInterrupt:
        imap_copy.disconnect()


if __name__ == '__main__':
    main()
