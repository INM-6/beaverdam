"""Query databases of metadata and filter the results.
"""

import metadatasource
import datatablecore


class Core:
    """The core/model of the user interface"""

    def __init__(self, cfg):
        """Query database to create data table

        Args:
            cfg (dict):  contains dicts with information to configure each object that
            will be generated.  Keys should include:
                'database' -- information required to access the database
                'fields' -- location in the database of each metadata field, and the
                    name to use to refer to each metadata field
                'filters' -- which database fields to turn into checkboxes
        """

        # Define database info
        self.db = metadatasource.MongoDbDatabase(cfg["database"])
        # Store information about fields to query and their field names
        # keys = field names, vals = access information for database (e.g. location)
        self.db.set_fields(cfg["fields"])

        # Query database for data table
        self.data_table = datatablecore.DataTableCore(
            self.db.query({}, list(self.db.fields.keys()))
        )
        # Initialize filter options
        self.data_table.set_filter({})
