# Import beaverdam-specific code
import sys

sys.path.insert(0, "./src")
import core as bd
import presenters as bd_present
import view_dash as bd_views_dash

# Import stuff for config file
# NOTE:  use tomllib once using Python 3.11
from tomlkit import parse

# Path to config file
fp_config = "config.toml"

# Parse config file
with open(fp_config, "rb") as f:
    config = parse(f.read())

# Define database info
db_info = bd.MongoDbDatabase(
    str(config["database"]["address"]),
    int(config["database"]["port"]),
    config["database"]["db_name"],
    config["database"]["collection_name"],
)

# Query database
requested_queries = {}
requested_projections = dict.fromkeys(list(config["projections"].values()), 1)
query_output = db_info.query(requested_queries, requested_projections)

# Store query output as Table class; later this will enable adding columns to specify
# which sessions are selected
table_data = bd.Table(query_output)

# Initialize filter options
filter_criteria = bd.FilterCriteria()

# Filter for sessions meeting criteria
table_data.filter(filter_criteria)

# Convert the table to something useable by Dash
table_data_for_dash = bd_present.DashDataTable("testtable", table_data.df)

# Make a graph
pie_graph = bd_present.DashPieChart("testfig", table_data.df, config["plots"]["data_to_plot"])

# Make checkboxes
checkboxes = bd_present.DashFilterChecklist("testchecklist", config["queries"]["filter_options"])

# Make GUI
bd_views_dash.build_dash_app(table_data_for_dash, pie_graph, checkboxes)
