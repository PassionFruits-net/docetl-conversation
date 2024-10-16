#! /usr/bin/python

from setuptools import setup, find_packages
import os.path
    
setup(
    name = "docetl-conversation",
    description = "",
    install_requires = [
        "llama-index",
        "llama-index-llms-openai",
        "jinja2",
        "numpy"
    ],
    version = "0.0.1",
    author = "Egil Moeller",
    author_email = "redhog@redhog.org",
    license = "GPL",
    url = "https://github.com/redhog/docetl-conversation",
    packages = find_packages(),
    entry_points = {
        "docetl.operation": [
            "conversation = docetl_conversation.operation:ConversationOperation"
        ]

    }
)
