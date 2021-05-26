pytket-qulacs
==================================

.. image:: CQCLogo.png
   :width: 120px
   :align: right

`Qulacs <https://docs.qulacs.org/en/latest/index.html>`_ is an optimized quantum
circuit simulator.

``pytket-qulacs`` is an extension to ``pytket`` that allows ``pytket`` circuits
to be simulated using ``qulacs``.

``pytket-qulacs`` is available for Python 3.7, 3.8 and 3.9, on Linux, MacOS and Windows.
To install, run:

``pip install pytket-qulacs``

GPU acceleration
~~~~~~~~~~~~~~~~

To use the ``QulacsGPUBackend``, which can take advantage of a CUDA-enabled GPU
on your machine for faster simulation, it is necessary to first install the CUDA
toolset. For platform-specific instructions on how to do this, see:

- `Linux <https://docs.nvidia.com/cuda/cuda-installation-guide-linux/>`_
- `MacOS <https://docs.nvidia.com/cuda/cuda-installation-guide-mac-os-x/>`_
- `Windows <https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/>`_

Afterwards, install ``qulacs-gpu``:

``pip install qulacs-gpu``

The ``QulacsGPUBackend`` has an identical API to the ``QulacsBackend``.

.. toctree::
    api.rst
    changelog.rst
