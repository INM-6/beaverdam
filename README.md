# Beaverdam

![Beaverdam logo](/src/beaverdam/viewer/_assets/beaverdam-logo_long.png)

***Build, Explore, and Visualize Experimental Data and Metadata***

Beaverdam is a Python package that centralizes your data or metadata and shows you a high-level overview of trends.  It combines (meta)data files into a single database, then generates a dashboard in your web browser so you can interactively explore.  Beaverdam was designed to be pretty simple, and give you the information you need to decide which (possibly less-simple) things to do next.

(Meta)data formats currently supported are [JSON](https://www.json.org) and [odML](https://g-node.github.io/python-odml), though in principle Beaverdam's MongoDB backend supports any file type that can be converted to JSON.

Currently, Beaverdam runs locally on your machine, and can build or access local or remote databases.

Beaverdam's dashboard shows configurable filters, plots, and a table with details of each (meta)data file.  It even has dark and light mode.  Here's an example:

![Beaverdam screenshot](/img/2024-04-12_dark-light.png)

## Dependencies

Beaverdam requires the following to be installed on your computer, plus a browser and terminal of your choice:

- **Python** (to run Beaverdam)
- **MongoDB** (to handle databases)
  - We tested Beaverdam with MongoDB Community Edition.  Installation instructions for various operating systems are in the [MongoDB documentation](https://www.mongodb.com/docs/manual/tutorial/).
  - We recommend enabling MongoDB to start automatically when your computer boots, so you don't have to manually start it each time you run Beaverdam.  On Linux, enable this option using `sudo systemctl enable mongod`.

## Installation

1. Make sure you have the [dependencies](#dependencies).
1. [*Optional but recommended*] Create a Python virtual environment using e.g. [venv](https://docs.python.org/3/library/venv.html) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
1. In a terminal, ensure you are in the Python interpreter or your virtual environment, and do one of the following:
    - **Install from GitHub:**
        - `pip install git+ssh://git@github.com/INM-6/beaverdam`
    - **Install from PyPi:**
        - *coming soon*

## How to use Beaverdam

### Configuration

A single configuration file contains all the information for Beaverdam to access the database and set options for the dashboard.  It's probably easiest to edit the example configuration file `config.toml` with your specific information.  Find more information on the contents of the configuration file in its comments and in the documentation [TODO].

### Build a database

1. Ensure all your metadata files are under one parent directory.  Within the directory, they can be sorted into subdirectories, and there can also be non-metadata files present.  Beaverdam will recursively search the parent directory to identify and ingest all files with a specified file extension.
1. [Install](#installation) Beaverdam and edit the [configuration](#configuration) file.  Important parameters for this step are:
   - location (parent directory) and type (file extension) of metadata files
   - database information
1. In a terminal, enter the Python interpreter or the virtual environment where you [installed](#installation) beaverdam, and run `beaverdam build config.toml`, where `config.toml` is the name and **relative** path of your configuration file

You will see a progress bar appear as Beaverdam builds or updates your database.  Any errors or warnings will be written to `beaverdam.log`, so please check this file afterwards in a text editor to see if there was a problem!

### View a database

1. [Build](#build-a-database) a database
1. Edit the [configuration](#configuration) file.  Important parameters for this step are:
   - database information
   - location within a metadata file of each field you want to show - see the documentation for more information [TODO]
     - for metadata files with complex structures, it might be helpful to find field locations using a tool like [Studio3T](https://studio3t.com/free/) or its free-forever predecessor [Robo3T](https://github.com/Studio3T/robomongo)
   - which metadata fields to show as filters, in the datatable, and in graphs
1. In a terminal, enter the Python interpreter or the virtual environment where you [installed](#installation) beaverdam, and run `beaverdam view config.toml`, where `config.toml` is the name and **relative** path of your configuration file
1. Follow the instructions to open the resulting link in your web browser - on Linux, this is `Ctrl+click`
1. Use the filter checkboxes and interactive graphs to explore your metadata!
1. When you're finished, close the terminal or exit the process - on Linux, this is `Ctrl+C`

## How to cite

TODO

## Acknowledgements

**Main authors:**  [Heather More](https://github.com/hlmore) and [Michael Denker](https://github.com/mdenker)

**Contributors:**  [Anton Pirogov](https://github.com/apirogov)

Many of Beaverdam's tools and practices are from the [FAIR Python Cookiecutter](https://github.com/Materials-Data-Science-and-Informatics/fair-python-cookiecutter) template.

The initial version of Beaverdam (called Owl) was produced by Lena Blind, Annika Röthenbacher, Jana Schelter, Julia Wellmann, and Jianing Sun.

This project was developed at the Institute for Advanced Simulation (IAS-6 and IAS-9) of the Jülich Research Center and supported by the Helmholtz Metadata Collaboration (HMC) Platform, EU Grant 945539 (HBP SGA3), and the NRW network iBehave (NW21-049).
