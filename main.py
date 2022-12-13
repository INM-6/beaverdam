## IMPORTS

# Import beaverdam-specific code
import sys

sys.path.insert(0, "./src")
import core as bd
import presenters as bdp
import view_dash as bdv
import parser



## INPUTS

# Path to config file
fp_config = "config.toml"

## CODE

# Parse config file
config = parser.parse_config(fp_config)

# Define database info
db_info = bd.MongoDbDatabase(
    str(config.database["address"]),
    int(config.database["port"]),
    config.database["db_name"],
    config.database["collection_name"],
)

# Query database
requested_queries = {}
requested_projections = dict.fromkeys(list(config.projections.values()), 1)
query_output = db_info.query(requested_queries, requested_projections)

# Store query output as Table class; later this will enable adding columns to specify
# which sessions are selected
table_data = bd.Table(query_output)

# Initialize filter options
filter_criteria = bd.FilterCriteria()

# Filter for sessions meeting criteria
table_data.filter(filter_criteria)

# Convert the table to something useable by Dash.  NOTE: keys and vals for the
# projections need to be switched to provide the input expected by DataTable
table_data_for_dash = bdp.DataTable(
    "testtable", table_data.df, {y: x for x, y in config.projections.items()}
)

# Make a graph
pie_graph = bdp.DashPieChart(
    "testfig", table_data.df, config.plots["data_to_plot"]
)

# Make checkboxes
checkboxes = bdp.DashFilterChecklist(
    list(config.queries.keys())[0], db_info, list(config.queries.values())[0]
)

# Make GUI
bdv.build_dash_app(table_data_for_dash, pie_graph, checkboxes)
