.. _quick-start-section:

Quick Start
===========


In this section it's showed how to create an empty plugin from the template command available on alfaism-sdk, with this
template you can easily customize your application to extendedn alfasim funcionatlies.


The ALFAsim-SDK is a python package that helps the developers in the process to create an application, in order to use
this tool it's necessary to have a Python Interpreter with at leat version 3.6. For more details on how to install Python check
this link https://www.python.org/downloads/


1) From a terminal, install the ALFASIM SDK from pip

.. code-block:: python

    pip install alfasim-sdk

2) Create an empty


A Plugin is a compressed bundle of files. As a minimum, this includes two components:
1) plugin.yaml with the information to be displayed over the application
2) DLL that contains the implemented model.

Additional files can be included, such as an icon image and a documentation file.


Deve implementar o `plugin.py` hooks do GUI e pre solver configs
Deve implementar o `plugin.c` hooks do solver
