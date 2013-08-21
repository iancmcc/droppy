.. title:: Home
.. highlight:: python
.. currentmodule:: droppy
.. raw:: html

.. _Dropwizard: http://dropwizard.codahale.com
.. _formencode: http://formencode.org
.. _bottle: http://bottlepy.org

=======================================================
Droppy - Python framework for rapid service development
=======================================================
Droppy (inspired by Dropwizard_) takes the boilerplate out of creating
a production-ready RESTful web service. It ties together several stable Python
libraries and takes care of all the plumbing, so you can focus exclusively on
function. Out of the box, you get:

* **Configuration** Define a configuration class; Droppy will deserialize and
  validate a config file against it and make the result available to your app.
* **Protocols** 
* **Client mode** Droppy will automatically create a client to talk to your service.
* **Fixtures** Writing tests for your app is simple with generated test cases.
* **Documentation** Droppy can generate Sphinx documentation from your code.
* **Managed components** The application lifecycle is available to set
  up and clean up database connections or whatever you need.




Contents:

.. toctree::
   :maxdepth: 1

   configuration


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


License
===================

Code and documentation are available according to the Apache 2 License:

.. include:: ../LICENSE
  :literal:
