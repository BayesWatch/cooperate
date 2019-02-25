=========
Cooperate
=========

Cooperate is for running experiments in different locations by 
accessing a shared list stored as a json file.

You know when you're running a simple script, maybe like:

``python main.py --lr 0.1``

And then you realise you want to run various settings for ``--lr`` so 
so you write a bash script to iterate over values, and passing them.
This works OK, but what if you have 1 GPU on your local machine, 4 on
a shared server and another one your friend is letting you use on their 
laptop? You want to run all your grid search settings on all those 
machines so they'll be finished faster.

You could split up the experiments based on which machines are going to
run them faster and run scripts on all the different machines, *or* you
could use ``cooperate``.

This is for you if you:

* Have a set of experiments to run with different settings.
* Those settings are passed as command line arguments.
* You have different machines to run these experiments on, and...
* Those machines share a file system (perhaps AFS).

You won't have to modify the script running your experiment, or set up
anything. This code doesn't do anything clever, and has almost no requirements
(just Click, for cli).

Quick Start
-----------

Install
^^^^^^^

If you're using conda, it may be better to install the requirement through that
first, to save pip making a mess of your virtual environment:

``conda install click``

Then install via pip (it'll install the requirement if you didn't do the
previous step):

``pip install git+https://github.com/Bayeswatch/cooperate``

Generate a json
^^^^^^^^^^^^^^^

Following on from the ``python main.py --lr`` example above, first you
generate a json file with the experiments you want to run. For example,
you could write a small Python script to do it:

::
  import json
  experiment_list = []
  for lr_setting in [0.1, 0.2, 0.3, 0.4]:
      experiment = "python main.py --lr %.2f"%lr_setting
      # commands must be a list
      experiment_list.append(experiment.split(" "))
  with open("my_experiments.json", "w") as f:
      f.write(json.dumps(experiment_list))

Which would produce a json file like this:

``[["python", "main.py", "--lr", "0.1"], ...]``

Place this json file, ``my_experiments.json`` somewhere all the machines
you want to run experiments on can access. For example, if you are using
AFS, somewhere in your home directory.

``cp my_experiments.json ~/experiment_lists/``

Run Experiments
^^^^^^^^^^^^^^^

In each place we would like to run these experiments, on different
machines, navigate to the location you would have to be to run the
original command (``python main.py --lr 0.1``), *as if you were going
to run each setting manually*. Then, run this command in each 
location, independently:

``cooperate --run ~/experiment_lists/my_experiments.json``

Each experiment in the list will be executed in sequence, whenever
a machine finishes running its current experiment.

*A warning*: if your experiment hits an error, whichever location
hit the error will stop and print the error, *but* you will notice
that the json file will still list the experiment as "executed"
(because it was). The failed experiment will be stored in a log
file called ``cooperate_<experiment number>`` where the number
is based on how many times you've called ``cooperate``. The name
of this file should be printed with the error, so you can find
it and run this experiment again manually, or put it back in 
``my_experiments.json``.

How does it work?
-----------------

Cooperate does two independent things:

1. Makes a ``.json`` file containing a list of commands to run experiments.
2. Loops over the experiments in those ``.json`` files, choosing one at a time,
   prepending "executed" to the command in the json and then running the
   command.

Making an experiment schedule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's not actually necessary to use this package to generate your experiment
json. The json file to run experiments only has contain a list containing
tuples of the parts of the command to be run. For example:

.. codeblock:: json
  [
    ["python", "main.py", "--lr", "0.1"],
    ["python", "main.py", "--lr", "0.2"],
  ]

It's even possible to write this yourself in an editor. Creating this in Python
yourself gives you much more control, and you can just regenerate the
experiment schedule each time you need to make a change.

Alternatively, to create a ``.json`` file use the following command:

``cooperate --doe <experiment_json_name.json>``

Then, follow the prompts to generate a set of experiment options.

Running experiments
~~~~~~~~~~~~~~~~~~~

Cooperate is designed to be run on many different machines, or multiple times
on the same machine. For example, if you have 4 GPUs you would like to run
experiments on, you can just call ``cooperate`` four times in separate shells
with different settings for ``CUDA_VISIBLE_DEVICES``. It is always called the
same way:

``cooperate --run <experiment_json_name.json>``

Distributed experiments
~~~~~~~~~~~~~~~~~~~~~~~

If you're running experiments on separate machines, all you need to do is place
the ``.json`` file containing your experiment schedule on a filesystem shared
by all of those machines.

FAQ
---

What about my results/logs?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

It just runs the commands in the ``.json`` file, so whatever happens when you
run your experiment normally will happen. You may have to set your experiment
to save results to a file named according to the settings it was run with.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
