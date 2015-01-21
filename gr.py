#!/usr/bin/env python
# -*- coding: utf-8 -*-
# some pieces were borrowed from https://github.com/deis/deis/ client
# specifically this: https://raw.githubusercontent.com/deis/deis/master/client/deis.py
# lots of parts were modeled off https://github.com/GrumpyRainbow/goodreads-py
# could not get the rainbow modules ^^ to work so I just stripped what I needed and put them in here.
 
'''gr


Usage: gr <command> [<args>...]

Auth commands::

  authenticate         Set up an authentication
  access_tokens        Get the tokens to resume the session later 
  user                 Get id of user who authorized OAuth.

User commands::

  status
  comment
  event
  fan
  follower
  friend
  group
  list
  notification
  books                get the list of the users books
  quote
  rate
  review
  shelf
  
Subcommands, use ``gr help [subcommand]`` to learn more::

  author               Author specific details
  book                 Get info about an author by id.
  search
  series
  topic

Options:
  -h --help     Show this screen.
  --version     Show version.
  
NOTE: make sure you set up your environment variables or store the account information locally in 
'''

from __future__ import unicode_literals, print_function
from docopt import docopt
from docopt import DocoptExit
import json
import locale
import logging
import os.path
import re
import requests
import subprocess
import sys
import time
import datetime
import urlparse
import urllib
import webbrowser
import xmltodict
import httplib2
from termcolor import colored
import pprint
from client.session import GRSession, GRSessionError

__version__ = "0.1.0"
__author__ = "Steven Scott"
__license__ = "MIT"


def _dispatch_cmd(method, args):
    logger = logging.getLogger(__name__)

    try:
        method(args)
    except EnvironmentError as err:
        logger.error(err.args[0])
        sys.exit(1)
    except ResponseError as err:
        resp = err.args[0]
        logger.error('{} {}'.format(resp.status_code, resp.reason))
        try:
            msg = resp.json()
            if 'detail' in msg:
                msg = "Detail:\n{}".format(msg['detail'])
        except:
            msg = resp.text
        logger.info(msg)
        sys.exit(1)

def _init_logger():
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)
    # TODO: add a --debug flag
    logger.setLevel(logging.INFO)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    
def trim(docstring):
    """
    Function to trim whitespace from docstring

    c/o PEP 257 Docstring Conventions
    <http://www.python.org/dev/peps/pep-0257/>
    """
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


class ResponseError(Exception):
    pass



class GRClient():
    '''Gr Client'''
    
    session = None
    host = "https://www.goodreads.com"
    client_id = "fhKd7UFFtWKFXU779QS2mA"
    client_secret = 'LJDsWEfkzMXoP3do8mJO04ZrTjJAQlL0b9Wiuz0f7qY'
    key = "nPwv45LOlOfy0dry1C7Gcw"
    secret = "78pLJTFAsdVvaJDteOD8WoEuwTEW8f3ixN7W1gzWhK4"
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def auth(self, args):
        """
        Valid commands for auth:

        auth:login        authenticate 
        auth:user         Get id of user who authorized OAuth. 

        Use `gr help [command]` to learn more.
        """
        return
    
    def auth_authenticate(self, args):
        """ 
        Go through Open Auththenication process.

        Usage: gr auth:authenticate [options]

        Options:
          --key=<key>
            provide a key
          --secret=<secret>
            provide a secret
        """
        access_token = args.get('--access_token')
        if not access_token and self.key:
            access_token = self.key
        access_token_secret = args.get('--access_token_secret')
        if not access_token_secret and self.secret:
            access_token_secret = self.secret
        
        self.session = GRSession(self.client_id, 
                                 self.client_secret,
                                 access_token, 
                                 access_token_secret)

        if access_token and access_token_secret:
            self.session.oath_resume()
        else: # Access not yet granted, allow via browser
            url = self.session.oath_start()
            webbrowser.open(url)
            while raw_input('Have you authorized me? (y/n) ') != 'y':
                pass
            self.session.oauth_finish()
            self.auth_access_tokens(args)

    def auth_access_tokens(self,args):
        """ 
        Return access tokens for storage, so that sessions can be 
        resumed easily.
        Returns: (access_token, access_token_secret) 
        """
        if not self.session:
            print(self.session)
            raise GRSessionError("No authenticated session.")
        print(self.session.access_token, self.session.access_token_secret)
        return self.session.access_token, self.session.access_token_secret

    
    def auth_user(self, args):
        """
        Get id of user who authorized OAuth.
        """
        self.auth_authenticate(args)
        if not self.session:
            raise GRSessionError("No authenticated session.")

        data_dict = self.session.get('api/auth_user', {'format':'xml'})
        # Parse response
        user_id = data_dict['user']['@id']
        name = data_dict['user']['name']
        # todo make this prettier 
        print(data_dict)
        return user_id, name
    
    def author(self, args):
        """
        Valid commands for author:

        author:info       Get info about an author by id. 
        author:books      Paginate an author's books.

        Use `gr help [command]` to learn more.
        """
        sys.argv[1] = 'author:info'
        args = docopt(self.author_info.__doc__)
        return self.author_info(args)
    
    def author_info(self,args):
        """
        Show the authors information page 

        Usage: gr author:info [options]

        Options:
          -a --author_id=<author_id>    author id
        """
        print(args)
        author_id = args.get('--author_id')
        
        if not author_id:
            raise Exception("--author_id needed ")
        
        payload = {'id': author_id, 'key': self.client_id }
        r = requests.get(self.host + "/author/show.xml", params=payload)
        
        print(xmltodict.parse(r.text))
        print(r.text)
        return
    
    def author_books(self,args):
        """
        Get the list of books from this author
        """
        return
    
    def user(self, args):
        """
        Valid commands for author:

        user:books      Paginate a users book list
        user:info       Get info about an author by id. 

        Use `gr help [command]` to learn more.
        """
        return  
    
    
    def user_books(self,args):
        """
        Show the users list of books 

        Usage: gr user:books [options]

        Options:
          -a --user_id=<user_id>    GR user id
        """
        print(args)
        user_id = args.get('--user_id')
        
        if not user_id:
            raise Exception("--user_id needed ")
        
        payload = {'id': user_id, 'key': self.client_id, 'format': 'xml' }
        r = requests.get(self.host + "/owned_books/user", params=payload)
        
#         print(xmltodict.parse(r.text))
        print(r.text)
        return
        
    
class GRRequestError(Exception):
    """ Custom request exception """
    def __init__(self, error_msg, url):
        self.error_msg = error_msg
        self.url = url

    def __str__(self):
        return self.error_msg + "\n" + self.url

class GRRequest:
    """ Handles the goodreads requests and response parsing """

    def __init__(self, path, additional_query_info, client_instance):
        """ """
        self.query_dict = dict(client_instance.query_dict.items() + additional_query_info.items())
        self.host = client_instance.host
        self.path = path
        # Will there be parameters?
        if len(self.query_dict) > 0:
            self.path += '?'

    def request(self, return_raw=False):
        """ """
        h = httplib2.Http('.cache')
        url_extension = self.path + urllib.urlencode(self.query_dict)
        response, content  = h.request(self.host + url_extension, "GET")

        # Check success
        if response['status'] != '200':
            raise GRRequestError(response['status'], url_extension)
            return

        # Some responses aren't xml structured (see get_book_id)
        if return_raw:
            return content
            
        # Parse response into dictionary
        data_dict = xmltodict.parse(content)
        if data_dict.has_key('error'):
            raise GRRequestError(data_dict['error'], url_extension)
        return data_dict['GRResponse']

from collections import OrderedDict
SHORTCUTS = OrderedDict([
    ('create', 'apps:create'),
    ('destroy', 'apps:destroy'),
    ('info', 'apps:info'),
    ('login', 'auth:login'),
    ('logout', 'auth:logout'),
    ('logs', 'apps:logs'),
    ('open', 'apps:open'),
    ('passwd', 'auth:passwd'),
    ('pull', 'builds:create'),
    ('register', 'auth:register'),
    ('rollback', 'releases:rollback'),
    ('run', 'apps:run'),
    ('scale', 'ps:scale'),
    ('sharing', 'perms:list'),
    ('sharing:list', 'perms:list'),
    ('sharing:add', 'perms:create'),
    ('sharing:remove', 'perms:delete'),
    ('whoami', 'auth:whoami'),
])       

def parse_args(cmd):
    """
    Parses command-line args applying shortcuts and looking for help flags.
    """
    if cmd == 'help':
        cmd = sys.argv[-1]
        help_flag = True
    else:
        cmd = sys.argv[1]
        help_flag = False
    # swap cmd with shortcut
    if cmd in SHORTCUTS:
        cmd = SHORTCUTS[cmd]
        # change the cmdline arg itself for docopt
        if not help_flag:
            sys.argv[1] = cmd
        else:
            sys.argv[2] = cmd
    # convert : to _ for matching method names and docstrings
    if ':' in cmd:
        cmd = '_'.join(cmd.split(':'))
    return cmd, help_flag


def main():
    '''Main entry point for the gr CLI.'''
    _init_logger()
    cli = GRClient()
    args = docopt(__doc__, version=__version__,options_first=True)
    cmd = args['<command>']
    cmd, help_flag = parse_args(cmd)
    # print help if it was asked for
    if help_flag:
        if cmd != 'help' and cmd in dir(cli):
            print(trim(getattr(cli, cmd).__doc__))
            return
        docopt(__doc__, argv=['--help'])
    # unless cmd needs to use sys.argv directly
    if hasattr(cli, cmd):
        method = getattr(cli, cmd)
    else:
        raise DocoptExit('Found no matching command, try `gr help`')
    # re-parse docopt with the relevant docstring
    docstring = trim(getattr(cli, cmd).__doc__)
    if 'Usage: ' in docstring:
        args.update(docopt(docstring))
    # dispatch the CLI command
    _dispatch_cmd(method, args)

    
if __name__ == '__main__':
    main()
