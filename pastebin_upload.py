#!/usr/bin/env python


import sys
import urllib
import os.path
import argparse
import ConfigParser

class FakeSecHead(object):
  def __init__(self, fp):
    self.fp = fp
    self.sechead = '[root]\n'

  def readline(self):
    if self.sechead:
      try: 
        return self.sechead
      finally: 
        self.sechead = None
    else: 
      return self.fp.readline()

settings = {
    'api_option': 'paste',
    }

__privacy_choices = ['public', 'unlisted', 'private']


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('filename')
  parser.add_argument('--privacy', '-p', choices=__privacy_choices, default='public', help='defaults to public')
  parser.add_argument('--name', '-n', default=None, help='defaults to filename')
  parser.add_argument('--format', '-f', default=None, help='defaults to None')
  parser.add_argument('--config', '-c', default=None, help='defaults to ~/.pastebin_settings')
  parser.add_argument('--expire', '-e', choices=['10M', '1H', '1D', '1W', '2W', '1M', '6M', '1Y'], default=None, help='defaults to never')
  parser.add_argument('--dev', default=None, help='pastebin dev key', default=None)
  parser.add_argument('--user', default=None, help='pastebin user key', default=None)
  args = parser.parse_args()

  config_file = "~/.pastebin_settings"
  if args.config:
    config_file = args.config

  settings['api_dev_key'] = args.dev
  settings['api_user_key'] = args.user

  if args.dev == None or args.user == None:
    config = ConfigParser.SafeConfigParser()
    try:
      config.readfp(FakeSecHead(open(os.path.expanduser(config_file))))
    except:
      print """could not open config (%s)""" % config_file
      return 2

    if args.dev == None:
      try:
        settings['api_dev_key'] = config.get('root', 'dev_key')
      except:
        print """config (%s) is missing (dev_key)""" % config_file
        return 2

    if args.user == None:
      try:
        settings['api_user_key'] = config.get('root', 'user_key')
      except:
        print """config (%s) is missing (api_key)""" % config_file
        return 2

  if os.path.isdir(args.filename) == False:
    if os.path.isfile(sys.argv[1]):
      code = open(args.filename, 'r').read()
    else:
      code = sys.argv[1]
    settings['api_paste_code'] = code
    settings['api_paste_name'] = urllib.quote_plus(sys.argv[1])
    if args.name:
      settings['api_paste_name'] = args.name
    if args.format:
      settings['api_paste_format'] = args.format
    if args.expire:
      settings['api_paste_expire_date'] = args.expire

    settings['api_paste_private'] = __privacy_choices.index(args.privacy)
    params = urllib.urlencode(settings)
    url = urllib.urlopen("https://pastebin.com/api/api_post.php", params)
    print url.read()
    return 1
  else:
    print """cannot upload directory (%s)""" % (args.filename)
    return 2

if __name__ == '__main__':
  status = main()
  sys.exit(status)
