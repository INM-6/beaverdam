## IMPORTS

# Import beaverdam-specific code
import sys
sys.path.insert(0, "./src")
import core as bd
import presenter as bdp
import view_dash as bdv
import controller as bdc
import parser

## INPUTS

# Path to config file
fp_cfg = "config.toml"

## CODE

class BeaverApp:
    def __init__(self, fp_cfg):
        self.model = bd.Core(fp_cfg)
        self.presenter = bdp.Presenter(fp_cfg)
        self.view = bdv.DashView()#datatable, single_checkbox_list, single_figure)
        self.controller = bdc.Controller()

        self.presenter.set_model(self.model)
        self.controller.set_model(self.model)
        self.view.set_presenter(self.presenter)
        self.view.set_controller(self.controller)

    def run(self):
        self.view.launch_app()

def main():
    app = BeaverApp(fp_cfg)
    app.run()

main()
        

# # Define database info
# db = bd.MongoDbDatabase(fp_cfg)

# # Query database
# query_request = bd.MongoDbQueryIO()
# query_request.set_query_input({})
# query_request.set_query_output(fp_cfg)
# session_table = bd.DataTable(db.query(query_request))

# # Store query output as Table class; later this will enable adding columns to specify
# # which sessions are selected
# #table_data = bd.Table(query_output)

# # Initialize filter options
# filter_criteria = bd.FilterCriteria({}
#     #{"Document.sections.subject.sections.Subject.properties.GivenName.value": ["Enya"]}
# )

# # Filter for sessions meeting criteria
# session_table.filter(filter_criteria)

# # Make the data table
# cfg_projections = parser.parse_config(fp_cfg, "projections")
# table_to_display = bdp.PrettyDataTable(session_table, cfg_projections.projections)

# # Make a graph
# cfg_plots = parser.parse_config(fp_cfg, "plots")
# pie_graph = bdp.PieChart(
#     session_table,
#     cfg_plots.plots["data_to_plot"],
#     cfg_projections.projections,
#     "Make nice plot titles",
# )

# # Make checkbox list
# cfg_checkbox_info = parser.parse_config(fp_cfg, "queries")
# checkboxes = bdp.FilterChecklist(
#     db,
#     list(cfg_checkbox_info.queries.values())[0],
#     list(cfg_checkbox_info.queries.keys())[0],
# )

# Make GUI
# bdv.build_dash_app(table_to_display, pie_graph, checkboxes)
