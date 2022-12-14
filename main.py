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
fp_cfg = "config.toml"
# Required headings in config file
cfg_sections = ["database", "queries", "projections", "plots"]

## CODE

# Parse config file
cfg = parser.parse_config(fp_cfg, cfg_sections)

# Define database info
db_info = bd.MongoDbDatabase(
    str(cfg.database["address"]),
    int(cfg.database["port"]),
    cfg.database["db_name"],
    cfg.database["collection_name"],
)

# Query database
requested_queries = {}
requested_projections = dict.fromkeys(list(cfg.projections.values()), 1)
query_output = db_info.query(requested_queries, requested_projections)

# Store query output as Table class; later this will enable adding columns to specify
# which sessions are selected
table_data = bd.Table(query_output)

# Initialize filter options
filter_criteria = bd.FilterCriteria()

# Filter for sessions meeting criteria
table_data.filter(filter_criteria)

# Make the data table
table_data_for_dash = bdp.DataTable("testtable", table_data.df, cfg.projections)

# Make a graph
pie_graph = bdp.PieChart(
    "testfig",
    table_data.df,
    cfg.plots["data_to_plot"],
    cfg.projections,
    "Make nice plot titles",
)

# Make checkboxes
checkboxes = bdp.FilterChecklist(
    list(cfg.queries.keys())[0] + "_checklist",
    db_info,
    list(cfg.queries.values())[0],
    list(cfg.queries.keys())[0],
)

# Make GUI
bdv.build_dash_app(table_data_for_dash, pie_graph, checkboxes)
