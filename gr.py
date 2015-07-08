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
  friends              get a list of user's friends
  group
  list
  notification
  books                get the list of the users books
  quote
  rate
  review
  shelf                get the list of books from a specific shelf
  shelves              get the list of the shelves the user has (read, to-read, etc)
  authors              get a list of the authors that the user has read from infile
  
Subcommands, use ``gr help [subcommand]`` to learn more::

  author               Author specific details
  book                 Get info about an author by id.
  search
  series
  topic

Options:
  -h --help           Show this screen.
  --version           Show version.
  --outfile=FILE      Output location
  --format=FORMAT     Output format 
  --infile=FILE       Some input files - can be anything  
  
NOTE: make sure you set up your environment variables or store the account information locally in 
'''
import json
import logging
import requests
import sys
import urllib
import webbrowser
import xmltodict
import httplib2
import os
import xml.etree.ElementTree as ET
from docopt import docopt
from docopt import DocoptExit
from posixpath import expanduser
from dicttoxml import dicttoxml
from termcolor import colored
from client.session import GRSession, GRSessionError
from collections import OrderedDict
from pprint import pprint
from client.response import GRResponse, ResponseFormatter
from ConfigParser import RawConfigParser


__version__ = "0.1.0"
__author__ = "Steven Scott"
__license__ = "MIT"


SHORTCUTS = OrderedDict([
    ('create', 'apps:create'),
    ('destroy', 'apps:destroy'),
    ('whoami', 'auth:whoami'),
])       


def _dispatch_cmd(method, args):
    logger = logging.getLogger(__name__)
    logger.info('In dispatch with args')
    
    """
    Setting up the common parameters
    General items are output of file etc
    Formatting. 
    User Information. 
    Keys
    """
    try:
        # a mixed response will come back 
        response = method(args)
        handle_output(response, args)
        
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

def handle_output(response, args):
    logger = logging.getLogger(__name__)
    """
    Take the response from the function call and see what we need to do with it.
     
    """
    outfile = args.get('--outfile')
    outfile_format = args.get('--format')
    
    if not outfile_format:
        outfile_format = 'xml'
        
    logger.info('Outfile format: ' + outfile_format)
    
    rf = ResponseFormatter()
    retvals = rf.get_formatted_response(response, outfile_format)
    
    if outfile:
        logger.info('Opening the outfile file ' + outfile)
        f = open(outfile,'w')
        logger.info('preppring write')
        f.write(retvals)
        f.close()
        return
    
    print(response)
    return retvals
    

def _init_logger():
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)
    # TODO: add a --debug flag
    logger.setLevel(logging.DEBUG)
    handler.setLevel(logging.DEBUG)
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
    config = None
    auth_section = 'secrets'
    host = "https://www.goodreads.com"
    env_file = ""
    client_id = ""
    client_secret = ""
    key = "nPwv45LOlOfy0dry1C7Gcw"
    secret = "78pLJTFAsdVvaJDteOD8WoEuwTEW8f3ixN7W1gzWhK4"
    
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.setup_config()


    def setup_config(self):        
        self.config = RawConfigParser()
        self.env_file = expanduser('~') + '/.goodreads_api.ini';
        self.config.read(self.env_file)
        
        if not self.config.has_section(self.auth_section):
            print('Setting up config with section: ' + self.auth_section)
            self.config.add_section(self.auth_section)
            self.config.set(self.auth_section, 'ACCESS_TOKEN', None)
            self.config.set(self.auth_section, 'ACCESS_TOKEN_SECRET', None)
            
        self.key = self.config.get(self.auth_section, 'ACCESS_TOKEN')
        self.secret = self.config.get(self.auth_section, 'ACCESS_TOKEN_SECRET')
        self.config.write(self.env_file)

    def auth(self, args):
        """
        Valid commands for auth:

        auth:authenticate        authenticate 
        auth:user         Get id of user who authorized OAuth. 

        Use `gr help [command]` to learn more.
        """
        return
    
    def auth_authenticate(self, args):
        """ 
        Go through Open Authentication process.

        Usage: gr auth:authenticate [options]

        Options:
          --client_id=<client_id>
            provide a client_id
          --client_secret=<client_secret>
            provide a client_secret
          --access_token=<access_token>
            a user access token
          --access_token_secret=<access_token_secret>
            a user access token secret
        """
        self.client_id = args.get('--client_id')
        self.client_secret = args.get('--client_secret')


        access_token = args.get('--access_token')
        # was the key loaded from config 
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
            self.session.oauth_resume()
        else: # Access not yet granted, allow via browser
            print("Getting OAuth")
            url = self.session.oauth_start()
            webbrowser.open(url)
            while raw_input('Have you authorized me? (y/n) ') != 'y':
                pass
            self.session.oauth_finish()
            self.auth_access_tokens(args)
            print("AccessToken: " + self.session.access_token)
            print("AccessTokenSecret: " + self.session.access_token_secret)
            self.config.set(self.auth_section,'ACCESS_TOKEN',self.session.access_token)
            self.config.set(self.auth_section,'ACCESS_TOKEN_SECRET',self.session.access_token_secret)

    def auth_access_tokens(self,args):
        """ 
        Return access tokens for storage, so that sessions can be 
        resumed easily.
        Returns: (access_token, access_token_secret) 
        """
        if not self.session:
            print(self.session)
            raise GRSessionError("No authenticated session.")
        
        return self.session.access_token, self.session.access_token_secret

    
    def auth_user(self, args):
        """
        Get id of user who authorized OAuth.
        """
        print(self.session)
        print("in user")
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
#         sys.argv[1] = 'author:info'
#         args = docopt(self.author_info.__doc__)
#         return self.author_info(args)
        return
    
    def author_info(self,args):
        """
        Show the authors information page 

        Usage: gr author:info [options]

        Options:
          -a --author_id=<author_id>   Author ID
          --outfile=FILE               Output location
          --format=FORMAT              Output format 
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

        user:info       Get info about an author by id. 
        user:books      Paginate a users book list
        user:friends    Get a list of the user's friends
        user:shelves    Get the user's shelves
        user:shelf      Get the list of books from a specific shelf 
        user:authors    Get the authors for this user's read books - OFFLINE OP

        Use `gr help [command]` to learn more.
        """
        return  
    
    
    def user_books(self,args):
        """
        Show the users list of books 

        Usage: gr user:books [options]

        Options:
          -u --user_id=<user_id>    GR user id
          --outfile=FILE      Output location
          --format=FORMAT    Output format 
        """
        self.auth_authenticate(args)
        if not self.session:
            raise GRSessionError("No authenticated session.")
        #print(args)
        user_id = args.get('--user_id')
        
        if not user_id:
            raise Exception("--user_id needed ")
        
        payload = {'id': user_id, 'key': self.client_id, 'format': 'xml' }
        return self.session.get(self.host + "/owned_books/user", payload)
        
#         print(xmltodict.parse(r.text))
    
    def user_friends(self,args):
        """
        Show the users list of books 

        Usage: gr user:friends [options]

        Options:
          -u --user_id=<user_id>    GR user id
          --outfile=FILE      Output location
          --format=FORMAT    Output format 
        """
        print(args)
        return
        self.auth_authenticate(args)
        if not self.session:
            raise GRSessionError("No authenticated session.")
            
        #print(args)
        user_id = args.get('--user_id')
        
        if not user_id:
            raise Exception("--user_id needed ")
        
        payload = {'id': user_id, 'key': self.client_id, 'format': 'xml' }
        return self.session.get(self.host + "/friend/user/" +user_id, payload)
        
#         print(xmltodict.parse(r.text))

    def user_shelves(self,args):
        """
        Show the users list of shelves 

        Usage: gr user:shelves [options]

        Options:
          -u --user_id=<user_id>    GR user id
          --outfile=FILE      Output location
          --format=FORMAT    Output format 
        """
        self.auth_authenticate(args)
        if not self.session:
            raise GRSessionError("No authenticated session.")
            
        #print(args)
        user_id = args.get('--user_id')
        
        if not user_id:
            raise Exception("--user_id needed ")
        
        payload = {'id': user_id, 'key': self.client_id, 'format': 'xml' }
        r = self.session.get(self.host + "/shelf/list/" +user_id, payload)
        
#         print(xmltodict.parse(r.text))
        print(r.text)
        return
    
    def user_shelf(self,args):
        """
        Show the users list of books on a shelf 

        Usage: gr user:shelf [options]

        Options:
          -u --user_id=<user_id>    GR user id
          -s --shelf=<shelf>        [default: 'read']
          --sort=<sort>             title, author, cover, rating, year_pub, date_pub, date_pub_edition, 
                                    date_started, date_read, date_updated, date_added, recommender, 
                                    avg_rating, num_ratings, review, read_count, votes, random
          --search=<query>          query to search through a users list of books
          --order=<order>           a, d (optional)
          --page=<n>                1-N (optional)
          --per_page=<n>            1-200 (optional)
          --outfile=FILE            Output location
          --format=FORMAT           Output format 
        """
        self.auth_authenticate(args)
        if not self.session:
            raise GRSessionError("No authenticated session.")
            
        user_id = args.get('--user_id')
        
        if not user_id:
            raise Exception("--user_id needed ")
        
        shelf = args.get('--shelf')
        sort = args.get('--sort')
        search = args.get('--search')
        order = args.get('--order')
        page = args.get('--page')
        per_page = args.get('--per_page')
        
        payload = {'id': user_id, 'key': self.client_id, 'format': 'xml', 
                   'v': 2, 'shelf': shelf, 'order': order,
                   'sort': sort, 'page': page,  'per_page': per_page,
                   'search': search
                   }
        return self.session.get(self.host + "/review/list/" +user_id, payload)
    
    def user_authors(self,args):
        """
        Show or parse the users list of read authors. 
        OFFLINE operation - must have run user:shelf to get theset values 
        This must be run after the user:shelf command has created the downloaded list of books
        Output can be either JSON CSV or XML 

        Usage: gr user:authors [options]

        Options:
          -u --user_id=<user_id>    GR user id
          -s --shelf=<shelf>        [default: 'read']
          --infile=FILE             Input file - might be list of reviews already downloaded 
          --outfile=FILE            Output location
          --format=FORMAT           Output format
        """
        self._logger.info('users:authors - starting ')
        infile = args.get('--infile')
        
        if not infile:
            raise Exception('This is an offline operation - profide a file --infile downloaded with user:shelf ')
        
        if not os.path.isfile(infile):
            raise Exception('Invalid file ' + infile)
        
        tree = ET.parse(infile)
        root = tree.getroot()
        authroot = {}
        for author in root.iter('author'):
            aid = int(author.find('id').text)
            authroot[aid] = {
                'name': author.find('name').text.strip('\n'),
                'image_url': author.find('image_url').text.strip('\n'),
                'small_image_url': author.find('small_image_url').text.strip('\n'),
                'link': author.find('link').text.strip('\n')
                             }
        
        return GRResponse(json.dumps(authroot), 'json')
            
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
