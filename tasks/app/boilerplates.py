################
# File: /boilerplates.py
# Project: app
# Created Date: Tue Dec 10th 2019
# Author: Ashok Kumar P (ParokshaX) (ashok@paroksha.com)
# -----
# Last Modified: Fri Feb 7th 2020
# Modified By: Ashok Kumar P (ParokshaX) (ashok@paroksha.com)
# -----
# Copyright (c) <<projectCreationYear>> Your Company
#################
# pylint: disable=line-too-long
"""
Boilerplates
"""
from __future__ import print_function

import logging
import os
import re

try:
    from invoke import ctask as task
except ImportError:  # Invoke 0.13 renamed ctask to task
    from invoke import task


log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@task
def crud_module(context, module_name="", models=[]):
    # pylint: disable=unused-argument
    """
    Create CRUD (Create-Read-Update-Delete) empty module.

    Usage:
    $ invoke app.boilerplates.crud-module --module-name=articles --module-name-singular=article
    """
    try:
        import jinja2
    except ImportError:
        log.critical(
            "jinja2 is required to create boilerplates. Please, do `pip install jinja2`"
        )
        return

    if not module_name:
        log.critical("Module name is required")
        return

    if not re.match("^[a-zA-Z0-9_]+$", module_name):
        log.critical(
            "Module module_name is allowed to contain only letters, numbers and underscores "
            "([a-zA-Z0-9_]+)"
        )
        return

    module_path = "app/modules/%s" % module_name

    module_title = " ".join([word.capitalize() for word in module_name.split("_")])

    model_names = [
        "".join([word.capitalize() for word in model.split("_")]) for model in models
    ]

    if os.path.exists(module_path):
        log.critical("Module `%s` already exists.", module_name)
        return

    os.makedirs(module_path)

    sub_dirs = ["model", "schema", "api", "parameter"]

    for loc in sub_dirs:
        loc_path = "{}/{}".format(module_path, loc)
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                "tasks/app/boilerplates_templates/crud_module/{}".format(loc)
            )
        )
        os.makedirs(loc_path)

        template = env.get_template("__init__.py.template")
        template.stream(
            module_name=module_name,
            module_title=module_title,
            module_namespace=module_name.replace("_", "-"),
            models=models,
            model_names=model_names,
        ).dump("%s/%s.py" % (loc_path, "__init__"))

        for i in range(0, len(models)):
            template = env.get_template("component.py.template")

            template.stream(
                module_name=module_name,
                module_title=module_title,
                is_main=i == 0,
                model_name_singular=models[i],
                module_namespace=models[i].replace("_", "-"),
                models=models,
                model_names=model_names,
                model_name=model_names[i],
            ).dump("%s/%s.py" % (loc_path, models[i].replace("-", "_")))

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("tasks/app/boilerplates_templates/crud_module")
    )

    template = env.get_template("__init__.py.template")
    template.stream(
        module_name=module_name,
        module_title=module_title,
        module_namespace=module_name.replace("_", "-"),
        models=model_names,
    ).dump("%s/%s.py" % (module_path, "__init__"))

    log.info("Module `%s` has been created.", module_name)
    print(
        "Add `%(module_name)s` to `ENABLED_MODULES` in `config.py`\n"
        "ENABLED_MODULES = (\n"
        "\t'auth',\n"
        "\t'users',\n"
        "\t'teams',\n"
        "\t'%(module_name)s',\n\n"
        "\t'api',\n"
        ")\n\n"
        "You can find your module at `app/modules/` directory"
        % {"module_name": module_name}
    )
