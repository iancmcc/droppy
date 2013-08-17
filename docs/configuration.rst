.. _configuration:

Configuration
=============
Droppy has a number of configuration parameters it uses out of the box. It also
provides a built-in mechanism for extending the configuration to provide
parameters specific to your application. 

Parsing and validation are handled automatically. Droppy can parse YAML or
JSON, and uses the excellent formencode_ library for validation.

.. _formencode: http://www.formencode.org/en/latest/