=========
Cooperate
=========


Cooperate runs experiments on different machines sharing a filesystem.

This is for you if you:

* Have a set of experiments to run with different settings.
* Those settings are passed as command line arguments.
* You have different machines to run these experiments on, and...
* Those machines share a file system (perhaps AFS).

You won't have to modify the script running your experiment, or set up
anything. This code doesn't do anything clever, and has almost no requirements
(just Click, for cmdline).

How does it work?
-----------------

Cooperate does two independent things:

1. Makes a ``.json`` file containing a list of commands to run experiments.
2. Loops over the experiments in those ``.json`` files, removing one at a time
   and running it.

Making an experiment schedule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's not actually necessary to use this package to generate your experiment
json. The json file to run experiments only has contain a list containing
tuples of the parts of the command to be run. For example:

    [
      ["python", "main.py", "--lr", "0.1"],
      ["python", "main.py", "--lr", "0.2"],
    ]

It's even possible to write this yourself in an editor, but you may want to
save a backup because the original ``.json`` will be destroyed when the
experiment is run.  Creating this in Python yourself gives you much more
control, and you can just regenerate the experiment schedule each time.

Alternatively, to create a ``.json`` file use the following command:

    cooperate --doe <experiment_json_name.json>

Then, follow the prompts to generate a set of experiment options.

Running experiments
~~~~~~~~~~~~~~~~~~~

Cooperate is designed to be run on many different machines, or multiple times
on the same machine. For example, if you have 4 GPUs you would like to run
experiments on, you can just call ``cooperate`` four times in separate shells
with different settings for ``CUDA_VISIBLE_DEVICES``. It is always called the
same way:

    cooperate --run <experiment_json_name.json>

Distributed experiments
~~~~~~~~~~~~~~~~~~~~~~~

If you're running experiments on separate machines, all you need to do is place
the ``.json`` file containing your experiment schedule on a filesystem shared
by all of those machines.

Install
--------

If you're using conda, it may be better to install the requirement through that
first, to save pip making a mess of your virtual environment:

    conda install click

Then install via pip (it'll install the requirement if you didn't do the
previous step):

    pip install git+https://github.com/Bayeswatch/cooperate

FAQ
---

What about my results?
~~~~~~~~~~~~~~~~~~~~~~

They'll be saved wherever they're saved on each machine you ran the command
from.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
