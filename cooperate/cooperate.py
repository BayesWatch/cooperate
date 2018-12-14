# -*- coding: utf-8 -*-
import json
from shutil import copyfile
from random import shuffle

"""Utility for generating a json prescribing experiments, and for running
experiments."""


def build_doe(file_path):
    """Build a design of experiments json file."""
    # if it doesn't end in `.json` add that
    if file_path[-5:] != '.json':
        file_path += '.json'
    # get user to input experiment script name
    print("Generating design of experiments...")
    script_name = input("Name of script (example: main.py):")
    assert script_name[-3:] == '.py'
    # static options
    print("Static option settings, example: --lr 0.1")
    print("These will be kept fixed for all experiments.")
    static_options, static_option = [], 'not_empty'
    while len(static_option) > 0:
        static_option = input("Static option (leave empty if done):")
        if len(static_option) > 0:
            static_options += static_option.split(" ")
    # can now set up script template
    template = ["python", script_name] + static_options
    # dynamic options
    print("Dynamic option names, example: --lr")
    print("These will be varied according to following options.")
    dyn, d = [], 'not_empty'
    while len(d) > 0:
        d = input("Dynamic option name (leave empty if done):")
        if len(d) > 0:
            dyn.append(d)
    # iterate over dynamic options and query for linear or log or manual
    dyn_vals = {}
    for d in dyn:
        dyn_vals[d] = space_values(d)
    # how to iterate over these settings?
    print("How to combine these options?")
    combine = ""
    while combine not in ['factorial', 'random', 'zip']:
        combine = input("factorial/random/zip:")
    if combine == 'factorial':
        experiments = factorial_experiments(template, dyn, dyn_vals)
    elif combine == 'random':
        N = input("Number of random combinations: ")
        experiments = factorial_experiments(template, dyn, dyn_vals)
        shuffle(experiments)
        experiments = experiments[:N]
    elif combine == 'zip':
        # have to assume we have the same number of values for each option
        experiments = [template[:]]*len(dyn_vals[dyn[0]])
        for i in range(len(experiments)):
            for d in dyn:
                experiments[i] += [d, dyn_vals[d][i]]
    with open(file_path, "w") as f:
        f.write(json.dumps(experiments))
    # always create a backup, to save repeating the generation process
    copyfile(file_path, file_path+'.backup')
    return None


def factorial_experiments(template, dyn, dyn_vals):
    experiments = []
    from itertools import product
    for vals in product(*[dyn_vals[d] for d in dyn]):
        experiment = template[:]
        for d, v in zip(dyn, vals):
            experiment += [d, v]
        experiments.append(experiment)
    return experiments


def space_values(dynamic_option):
    print("Values to iterate over for dynamic option: %s" % dynamic_option)
    space = ''
    while space not in ['log', 'linear', 'manual']:
        space = input("log/linear/manual:")
    if space == 'linear':
        import numpy as np
        low = float(input("Low:"))
        high = float(input("High:"))
        steps = int(input("Number of steps:"))
        values = [str(v) for v in np.linspace(low, high, steps)]
    elif space == 'log':
        import numpy as np
        low = np.log10(float(input("Low:")))
        high = np.log10(float(input("High:")))
        steps = int(input("Number of steps:"))
        values = [str(v) for v in np.logspace(low, high, steps)]
    elif space == 'manual':
        values, value = [], "not_empty"
        while len(value) > 0:
            value = input("Append value for dynamic option "
                          "(leave empty when done):")
            if len(value) > 0:
                values.append(value)
    return values
