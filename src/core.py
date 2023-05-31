"""Query databases of metadata and filter the results.

:copyright:
:licence:
"""

import metadatasource as datasource
import datatablecore as datatable


class Core:
    """The core/model of the user interface"""

    def __init__(self, cfg):
        """Query database to create data table

        Args:
            cfg (dict):  contains dicts with information to configure each object that
            will be generated.  Keys should include:
                'database' -- information required to access the database
                'filters' -- which database fields to turn into checkboxes
        """

        # Define database info
        self.db = datasource.MongoDbDatabase(cfg["database"])
        # Store information about fields to query and their display names
        # keys = display names, vals = access information for database (e.g. location)
        self.db.set_fields(cfg["fields"])

        # Query database for data table
        data_table = datatable.DataTableCore(
            self.db.query({}, list(self.db.fields.keys()))
        )
        # Initialize filter options
        data_table.set_filter({})
        # Store data table
        self.data_table = data_table
