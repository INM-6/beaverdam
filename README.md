# Beaverdam

![Beaverdam logo](/src/beaverdam/viewer/_assets/beaverdam-logo_long.png)

***Build, Explore, and Visualize Experimental Data and Metadata***

Beaverdam is a Python package that centralizes your data or metadata and shows you a high-level overview of trends.  It combines (meta)data files into a single database, then generates a dashboard in your web browser so you can interactively explore.  Beaverdam was designed to be pretty simple, and give you the information you need to decide which (possibly less-simple) things to do next.

(Meta)data formats currently supported are [JSON](https://www.json.org) and [odML](https://g-node.github.io/python-odml), though in principle Beaverdam's MongoDB backend supports any file type that can be converted to JSON.

Currently, Beaverdam runs locally on your machine, and can build or access local or remote databases.

Beaverdam's dashboard shows configurable filters, plots, and a table with details of each (meta)data file.  It even has dark and light mode!  Here's an example:

![Beaverdam screenshot](/img/2024-04-12_17-15_light_cropped.png)

## Dependencies

Beaverdam requires the following to be installed on your computer, plus a browser and terminal of your choice:

- **Python** (to run Beaverdam)
  - Downloads and installation instructions for various operating systems are on the [Python downloads page](https://www.python.org/downloads/)
  - Some people prefer the [conda](https://www.anaconda.com/download/) distribution of Python, which includes extra features and packages - consider [miniconda](https://docs.anaconda.com/free/miniconda/index.html) instead if you don't want to install >4GB of stuff ;)
- **MongoDB** (to handle databases)
  - We tested Beaverdam with MongoDB Community Edition.  Installation instructions for various operating systems are in the [MongoDB documentation](https://www.mongodb.com/docs/manual/tutorial/).
  - After installing MongoDB, we recommend enabling it to start automatically when your computer boots, so you don't have to manually start it each time you run Beaverdam.  On Linux, enable this option using:
    ```
    sudo systemctl enable mongod
    ```

## Installation

1. Make sure you have the dependencies (see [Dependencies](#dependencies)).
1. [*Optional but recommended*] Create a Python virtual environment using e.g. [venv](https://docs.python.org/3/library/venv.html) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).
1. In a terminal [*recommended to be in your virtual environment*], run
    ```
    pip install git+ssh://git@github.com/INM-6/beaverdam
    ```

## How to use Beaverdam

Using Beaverdam is a two-step process:  first, build a database from your (meta)data files; next, view and explore the database by generating a dashboard in a browser window.  Before carrying out these two steps, you will need to ensure your files are Beaverdam-friendly, and set up the necessary configuration file.

You can try out building and viewing a database using the example dataset and configuration file in the [`/example`](example/README.md#beaverdam-example) directory of this repo.

Schematically, Beaverdam works like this:

![Beaverdam schematic](/img/beaverdam_schematic.png)

### (Meta)data files

We designed Beaverdam to have as few restrictions as possible.  However, in order to properly find and parse information, Beaverdam makes the following assumptions:

- **One parent directory**:  Beaverdam looks for files in all subdirectories of a specified parent directory
- **One file per record** (e.g. experiment, session, person)
- **Unique file names**:  Beaverdam uses filenames as unique identifiers, and will replace records in the database if files have the same name.  Hover text in plots often includes the filename to identify data points, so to make your life easier we suggest choosing meaningful names :)
- **Same file extension** (*one* of `.odml` or `.json`):  Beaverdam will include all files with this extension inside the parent directory.  Other types of files can be present; Beaverdam will ignore them.
- **Same data structure**:  A given (meta)data field must exist in the same hierarchical location in all files that contain that field.  It doesn't have to exist in all files, though.  This is a restriction from MongoDB.  For example, if one json file has a section `subject` with a subsection `name`, Beaverdam can only combine this with information from other files in which `name` is also a subsection of `subject` (rather than a top-level section itself).

### Configuration

A single configuration file contains all the information for Beaverdam to access the database and set options for the dashboard.  It's probably easiest to download the template configuration file `config_template.toml` from the main directory of this repository, then edit it with your specific details.  Find more information within the configuration file.

### Build a database

1. Ensure all your [files](#metadata-files) are organized and formatted correctly.
1. [Install](#installation) Beaverdam and edit the [configuration file](#configuration).  Important sections for this step are:
   - `[raw_metadata]`:  location (parent directory) and type (file extension) of metadata files
   - `[database]`:  location of database
1. Make sure MongoDB is running.  If you have just installed it, or haven't enabled it to start automatically when your computer boots, you will need to do this manually.  On Linux, follow [these instructions](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/#start-mongodb).
1. In a terminal, enter the virtual environment where you [installed](#installation) beaverdam, and run
    ```
    beaverdam build config.toml
    ```
    where `config.toml` is the name and **relative** path of your configuration file

    You will see a progress bar appear as Beaverdam builds or updates your database.  Any errors or warnings will be written to `beaverdam.log` in the same directory as your configuration file - please check the log file afterwards in a text editor to see if there was a problem!

### View a database

1. [Build](#build-a-database) a database
1. Edit the [configuration file](#configuration).  Important sections for this step are:
   - `[database]`:  location of database
   - `[fields]`:  location of each field you want to show
   - `[filters]`, `[table]`, and `[plots]`:  which metadata fields to show as filters, in the datatable, and in graphs
1. Make sure MongoDB is running.  If you just built a database, it's already running and you can proceed to the next step.  If not, and if you haven't enabled MongoDB to start automatically when your computer boots, you will need to do this manually.  On Linux, follow [these instructions](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/#start-mongodb).
1. In a terminal, enter the virtual environment where you [installed](#installation) beaverdam, and run
    ```
    beaverdam view config.toml
    ```
    where `config.toml` is the name and **relative** path of your configuration file
1. Follow the instructions to open the resulting link in your web browser - on Linux, this is `Ctrl+click`
1. Use the filter checkboxes and interactive graphs to explore your metadata!
1. When you're finished, close the terminal or exit the process - on Linux, this is `Ctrl+C`

## How to cite

Use the information in the [citation file](https://github.com/INM-6/beaverdam/blob/documentation/CITATION.cff), which follows the [citation file format](https://citation-file-format.github.io).

## How to contribute

Do you have a question or suggestion, or did you find a problem?  We would love to hear about it!  Please open an [issue](https://github.com/INM-6/beaverdam/issues).

Do you want to fix a problem yourself, or add a new feature?  Awesome!  Please open a [pull request](https://github.com/INM-6/beaverdam/pulls).

## Authors and contributors

**Main authors:**  [Heather More](https://github.com/hlmore) and [Michael Denker](https://github.com/mdenker)

**Contributors:**  [Anton Pirogov](https://github.com/apirogov)

## Acknowledgements

Many of Beaverdam's tools and practices are from the [FAIR Python Cookiecutter](https://github.com/Materials-Data-Science-and-Informatics/fair-python-cookiecutter) template.  Beaverdam uses [somesy](https://github.com/Materials-Data-Science-and-Informatics/somesy) to manage its metadata.

The initial version of Beaverdam (called Owl) was produced by Lena Blind, Annika Röthenbacher, Jana Schelter, Julia Wellmann, and Jianing Sun.

This project was developed at the Institute for Advanced Simulation (IAS-6 and IAS-9) of the Jülich Research Center and supported by the Helmholtz Metadata Collaboration (HMC) Platform, EU Grant 945539 (HBP SGA3), and the NRW network iBehave (NW21-049).
