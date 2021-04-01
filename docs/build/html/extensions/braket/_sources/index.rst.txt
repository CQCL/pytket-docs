pytket-braket
==================================

.. image:: CQCLogo.png
   :width: 120px
   :align: right

``pytket-braket`` is an extension to ``pytket`` that allows ``pytket`` circuits to
be executed on quantum devices and simulators via Amazon's Braket service.

``pytket-braket`` is available for Python 3.7, 3.8 and 3.9, on Linux, MacOS and Windows.
To install, run:

``pip install pytket-braket``

.. note::   Requires an `Amazon Braket <https://aws.amazon.com/braket/>`_ account.

pytket.extensions.braket
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: pytket.extensions.braket
    :special-members:
    :members: BraketBackend


.. automodule:: pytket.extensions.braket.backends.config
    :members: