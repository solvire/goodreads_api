#!/usr/bin/env python
# -*- coding: utf-8 -*-
# some pieces were borrowed from https://github.com/deis/deis/ client
'''gr


Usage: gr <command> [<args>...]

Auth commands::

  user                 Get id of user who authorized OAuth.

Author commands::

  books                Paginate an author's books.
  show                 Get info about an author by id.

Book commands::

  isbn_to_id           Get the Goodreads book ID given an ISBN. 
  review_counts        Get review statistics given a list of ISBNs. 
  show                 Get the reviews for a book given a Goodreads book id. 
  show_by_isbn         Get the reviews for a book given an ISBN. 
  title                Get the reviews for a book given a title string. 

Comment commands::

  create
  list

Events commands::

  list

Fanship commands::

  create
  destroy
  show

Followers commands::

  create
  destroy

Friend commands::

  confirm_recommendation
  confirm_request
  requests
  create

Group commands::

  join
  list
  members
  search
  show

List commands::

  book 
  
Notifications commands::

  show

Notifications commands::

  all

OwnedBooks commands::

  create
  list
  show
  update

Quotes commands::

  create

Ratings commands::

  create
  destroy

ReadStatuses commands::

  show

Recommendations commands::

  show

Review commands::

  create
  edit
  list
  recent_reviews
  show
  show_by_user_and_book

Search commands::

  authors
  books

Series commands::

  show
  list
  work

Shelves commands::

  add_to_shelf
  add_books_to_shelves
  list

Topic commands::

  create
  group_folder
  show
  unread_group

Updates commands::

  friends

UserShelves commands::

  create
  update

User commands::

  show
  compare
  followers
  following
  friends

UserStatus commands::

  create
  destroy
  show
  index

Work commands::

  editions

  gr -h | --help
  gr --version

Options:
  -h --help     Show this screen.
  --version     Show version.
'''

from __future__ import unicode_literals, print_function
from docopt import docopt
from docopt import DocoptExit
import json
import locale
import logging
import os.path
import re
import subprocess
import sys
import time
import urlparse
import Goodreads
from termcolor import colored

__version__ = "0.1.0"
__author__ = "Steven Scott"
__license__ = "MIT"


def _dispatch_cmd(method, args):
    logger = logging.getLogger(__name__)
    if args.get('--app'):
        args['--app'] = args['--app'].lower()
    try:
        method(args)
    except requests.exceptions.ConnectionError as err:
        logger.error("Couldn't connect to the Deis Controller:\n{}\nMake sure that the Controller URI is \
correct and the server is running.".format(err))
        sys.exit(1)
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
    # convert : to _ for matching method names and docstrings
    if ':' in cmd:
        cmd = '_'.join(cmd.split(':'))
    return cmd, help_flag

def main():
    '''Main entry point for the gr CLI.'''
    args = docopt(__doc__, version=__version__)
    
    _init_logger()
    cli = GRClient()
    args = docopt(__doc__, version=__version__,
                  options_first=True)
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
        raise DocoptExit('Found no matching command, try `deis help`')
    # re-parse docopt with the relevant docstring
    docstring = trim(getattr(cli, cmd).__doc__)
    if 'Usage: ' in docstring:
        args.update(docopt(docstring))
    # dispatch the CLI command
    _dispatch_cmd(method, args)

    
    print('running')
    print(args)

if __name__ == '__main__':
    main()