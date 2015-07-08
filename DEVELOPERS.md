# Notes for developers

As a developer you are invited to read the following.

## Use python Virtual Environments
A Virtual Environment is a tool that allows to create a minimal and customized environment, for every project,
in which only the needed dependecies are installed with the options needed (e.g. the particular version of
the dependency).

### Basic instructions to setup a working virtual environment
1. install virtualenv via pip:

    ```
    pip install virtualenv
  
    ```
2. create the virtual environment inside 'venv':

    ```
    cd project_name
    virtualenv  [-p path_to_preferred_interpreter] venv
    ```

3. virtual environment usage:

    To activate the virtual environment:

    ```
    source venv/bin/activate
    ```

    To return to the system's default environment:

    ```
    deactivate
    ```

### Virtual environment for mpm
As mpm uses Scrapy, which is supported under Python 2.7 only, the virtual
environment has to be setup with Python 2.7 as preferred interpreter.

Please also note that .gitignore already contains the folder 'venv' so you may want
use this as a name for the virtual environment.

## Requirements and dependencies
All the requirements and dependencies needed for mpm
are listed inside requirements_dev.txt.

To install them just type:

```
pip install -r requirements_dev.txt
```

## Git commit messages style
As a part of the mpm team you should use the following commit message convention:

```
Summary

-thing done #1
- ...
-thing done #n
```

Please note the blank line before the list.
