===============================
Good Reads API - goodreads_api
===============================

.. image:: https://badge.fury.io/py/goodreads_api.png
    :target: http://badge.fury.io/py/goodreads_api

.. image:: https://travis-ci.org/solvire/goodreads_api.png?branch=master
        :target: https://travis-ci.org/solvire/goodreads_api

.. image:: https://pypip.in/d/goodreads_api/badge.png
        :target: https://crate.io/packages/goodreads_api?version=latest


A GoodReads API Command Line Tool

Features
--------

* TODO

Requirements
------------

- Python >= 2.6 or >= 3.3


Installation
------------

To get things going set up a virtualenv. I prefer the `virtualenvwrapper`. It makes things a little bit easier.  

	git clone https://github.com/solvire/goodreads_api.git
	cd goodreads_api/
	mkvirtualenv gr
	python setup.py install
	touch ~/.goodreads_api.ini
	

I have found to be _autoenv_ https://github.com/kennethreitz/autoenv useful on this project since I don't touch it very often.

Now run gr.py

	python gr.py help
	
Authenticate 

	python gr.py auth:authenticate --client_secret=SECRET --client_id=CLIENTID
	python gr.py auth:user
	

Other Libraries
---------------

It looks like most of the other libs out there are pretty incomplete.  I know why too after working with the API. I'm going to try to complete a few more calls.  If anyone is interested please go ahead and fork this.


License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/solvire/gr/blob/master/LICENSE>`_ file for more details.
