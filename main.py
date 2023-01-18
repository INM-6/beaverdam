## IMPORTS

# Import beaverdam-specific code
import sys
sys.path.insert(0, "./src")
import core as bd
import presenters as bdp
import view_dash as bdv
import controllers as bdc
import parser

## INPUTS

# Path to config file
fp_cfg = "config.toml"

## CODE

# Define database info
db = bd.MongoDbDatabase(fp_cfg)

# Query database
query_request = bd.MongoDbQueryIO()
query_request.set_query_input({})
query_request.set_query_output(fp_cfg)
session_table = bd.DataTable(db.query(query_request))

# Store query output as Table class; later this will enable adding columns to specify
# which sessions are selected
#table_data = bd.Table(query_output)

# Make checkbox list
cfg_checkbox_info = parser.parse_config(fp_cfg, "queries")
checkboxes = bdp.FilterChecklist(
    db,
    list(cfg_checkbox_info.queries.values())[0],
    list(cfg_checkbox_info.queries.keys())[0],
)

# Initialize filter options
filter_criteria = bd.FilterCriteria({}
    #{"Document.sections.subject.sections.Subject.properties.GivenName.value": ["Enya"]}
)

# Filter for sessions meeting criteria
table_data.filter(filter_criteria)

# Make the data table
table_to_display = bdp.DataTable(table_data.df, cfg.projections)

# Make a graph
pie_graph = bdp.PieChart(
    table_data.df,
    cfg.plots["data_to_plot"],
    cfg.projections,
    "Make nice plot titles",
)

# Make checkboxes
checkboxes = bdp.FilterChecklist(
    db_info,
    list(cfg.queries.values())[0],
    list(cfg.queries.keys())[0],
)

# Make GUI
bdv.build_dash_app(table_to_display, pie_graph, checkboxes)
