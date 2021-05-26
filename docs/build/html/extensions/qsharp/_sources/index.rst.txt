pytket-qsharp
==================================

.. image:: CQCLogo.png
   :width: 120px
   :align: right

Microsoft's `QDK <https://docs.microsoft.com/en-us/quantum/install-guide>`_ is a
language and associated toolkit for quantum programming.

``pytket-qsharp`` is an extension to ``pytket`` that allows ``pytket`` circuits to be
executed on simulators and resource estimators from the Microsoft QDK.

``pytket-qsharp`` is available for Python 3.7, 3.8 and 3.9, on Linux, MacOS and Windows. To
install, run:

``pip install pytket-qsharp``

In order to use ``pytket-qsharp`` you will first need to install the ``dotnet`` SDK
(3.1) and the ``iqsharp`` tool. On some Linux systems it is also necessary to
modify your ``PATH``:

1. See `this <https://dotnet.microsoft.com/download/dotnet-core/3.1>`_ page for instructions on installing the SDK on your operating system.
2. On Linux, ensure that the `dotnet` tools directory is on your path. Typically this will be ``~/.dotnet/tools``.
3. Run ``dotnet tool install -g Microsoft.Quantum.IQSharp``.
4. Run ``dotnet iqsharp install --user``.

.. toctree::
    api.rst
    changelog.rst
