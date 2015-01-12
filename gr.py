#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''gr

Usage:
  gr auth user
  gr author books
  gr auth user
  gr author books
  gr author show
  gr book isbn_to_id
  gr book review_counts
  gr book show
  gr book show_by_isbn
  gr book title
  gr comment create
  gr comment list
  gr events list
  gr fanship create
  gr fanship destroy
  gr fanship show
  gr followers create
  gr followers destroy
  gr friend confirm_recommendation
  gr friend confirm_request
  gr friend requests
  gr friends create
  gr group join
  gr group list
  gr group members
  gr group search
  gr group show
  gr list book
  gr notifications
  gr owned_books create
  gr owned_books list
  gr owned_books show
  gr owned_books update
  gr quotes create
  gr rating create
  gr rating destroy
  gr read_statuses show
  gr recommendations show
  gr review create
  gr review edit
  gr reviews list
  gr review recent_reviews
  gr review show
  gr review show_by_user_and_book
  gr search authors
  gr search books
  gr series show
  gr series list
  gr series work
  gr shelves add_to_shelf
  gr shelves add_books_to_shelves
  gr shelves list
  gr topic create
  gr topic group_folder
  gr topic show
  gr topic unread_group
  gr updates friends
  gr user_shelves create
  gr user_shelves update
  gr user show
  gr user compare
  gr user followers
  gr user following
  gr user friends
  gr user_status create
  gr user_status destroy
  gr user_status show
  gr user_status index
  gr work editions
  gr -h | --help
  gr --version

Options:
  -h --help     Show this screen.
  --version     Show version.
'''

from __future__ import unicode_literals, print_function
from docopt import docopt

__version__ = "0.1.0"
__author__ = "Steven Scott"
__license__ = "MIT"


def main():
    '''Main entry point for the gr CLI.'''
    args = docopt(__doc__, version=__version__)
    print(args)

if __name__ == '__main__':
    main()