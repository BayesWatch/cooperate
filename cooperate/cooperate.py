# -*- coding: utf-8 -*-
import os
import json
import subprocess
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

def execute(experiment, experiment_logfile, persistent=False):
    postfix = []
    while True:
        try:
            return subprocess.run(experiment + postfix, check=True)
        except subprocess.CalledProcessError:
            if experiment_logfile is not None:
                print("I was " + experiment_logfile)
            if not persistent:
                raise
        if os.path.exists("cooperate.persistent.postfix"):
            with open("cooperate.persistent.postfix", "r") as f:
                postfix = [f.read()]

def execute_single(to_run, persistent=False):
    # if we want to add a flag to rerun jobs
    if persistent:
        flag = input("Flag to append, when failed: ")
        if len(flag) > 0:
            with open("cooperate.persistent.postfix", "w") as f:
                f.write(flag)

    # read all experiments
    with open(to_run, "r") as f:
        schedule = json.load(f)
    # print out all the experiments
    for i, experiment in enumerate(schedule):
        if "executed" == experiment[0]:
            print("%i (previously executed): "%i, experiment[1:])
        else:
            print("%i: "%i, experiment)
    # remove one
    experiment_idx = int(input("Experiment to run: "))
    experiment_to_run = schedule[experiment_idx]
    if "executed" == experiment_to_run[0]:
        experiment_to_run = experiment_to_run[1:]
    # write experiments back with this one marked
    with open(to_run, "w") as f:
        schedule[experiment_idx] = ["executed"] + experiment_to_run
        f.write(json.dumps(schedule))
    # run this experiment
    print("Running: ", " ".join(experiment_to_run))
    execute(experiment_to_run, None, persistent)

def run_experiments(to_run, persistent=False):
    # if we want to add a flag to rerun jobs
    if persistent:
        flag = input("Flag to append, when failed: ")
        if len(flag) > 0:
            with open("cooperate.persistent.postfix", "w") as f:
                f.write(flag)
    # find a place to write a logfile
    experiment_logfile, i = "cooperate_%i", 0
    while os.path.exists(experiment_logfile%i):
        i += 1 
    experiment_logfile = experiment_logfile%i
    try:
        while True:
            # read all experiments
            with open(to_run, "r") as f:
                schedule = json.load(f)
            # filter for experiments that have not been run yet
            remaining = not_run_yet(schedule)
            # remove one
            experiment_idx = remaining.pop()
            experiment_to_run = schedule[experiment_idx]
            # write experiments back with this one marked
            with open(to_run, "w") as f:
                schedule[experiment_idx] = ["executed"] + experiment_to_run
                f.write(json.dumps(schedule))
            print("Running: ", " ".join(experiment_to_run))
            # and write this to file, noting which GPU it is being run on:
            with open(experiment_logfile, "w") as f:
                f.write(" ".join(experiment_to_run))
            execute(experiment_to_run, experiment_logfile, persistent)
    except IndexError:
        print("All experiments completed.")

def not_run_yet(schedule):
    return [i for i,e in enumerate(schedule) if e[0] != "executed"]

def progress(running_json):
    def status(running_json):
        with open(running_json, "r") as f:
            schedule = json.load(f)
        # filter for experiments that have not been run yet
        remaining = not_run_yet(schedule)
        return len(remaining), len(schedule)
    remaining, total = status(running_json)
    print(f"Executed (not necessarily completed): {total-remaining}/{total}")
