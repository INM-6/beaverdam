# Things to go into config.toml
# also see configparser:  https://docs.python.org/3/library/configparser.html

# Database info
config_address = "localhost"
config_port = 27017
config_db_name = "testodml"
config_collection_name = "odmlmetadata"
# Query info
# config_requested_queries = {
#     "Document.sections.subject.sections.Subject.properties.GivenName.value": {
#         "$in": ["Enya"]
#     }
# }
config_requested_queries = {}
config_requested_projections = {
    "Document.sections.session.sections.Session.properties.Name.value": 1,
    "Document.sections.subject.sections.Subject.properties.GivenName.value": 1,
    "Document.sections.session.sections.Session.sections.Task.properties.ShortName.value": 1,
    "Document.sections.TaskParameters.properties.dtp_filename.value": 1,
    "Document.sections.session.sections.Session.sections.Performance.properties.AverageTrialTime.value": 1,
    "Document.sections.session.sections.Session.sections.Performance.properties.AverageErrorCount.value": 1,
    "Document.sections.SessionInfo.sections.spike_sorting1.properties.SortingAuthor.value": 1,
    "Document.sections.SessionInfo.sections.spike_sorting2.properties.SortingAuthor.value": 1,
    "Document.sections.SessionInfo.sections.spike_sorting3.properties.SortingAuthor.value": 1,
    "Document.sections.SessionInfo.sections.spike_sorting4.properties.SortingAuthor.value": 1,
    "Document.sections.session.sections.Session.sections.DataQuality.properties.Electrophysiology.value": 1,
    "Document.sections.session.sections.Session.sections.DataQuality.properties.Eye.value": 1,
    "Document.sections.session.sections.Session.sections.DataQuality.properties.Hand.value": 1,
    "Document.sections.session.sections.Session.properties.Modality1.value": 1,
    "Document.sections.session.sections.Session.properties.Modality2.value": 1,
    "Document.sections.session.sections.Session.properties.Modality3.value": 1,
}
config_data_to_plot = "Document.sections.subject.sections.Subject.properties.GivenName.value"
config_filter_options = {"Document.sections.subject.sections.Subject.properties.GivenName.value": "Enya"}
# config_requested_queries = {
#     'Document.sections.subject.sections.Subject.properties.GivenName.value': {
#         'ID': 'GivenName',
#         'value': ''
#     }
# }
# config_requested_projections = {
#     'Document.sections.subject.sections.Subject.properties.GivenName.value': {
#         'ID': 'Session name',
#         'value': 1
#     }
# }

# Import beaverdam-specific code
import sys
sys.path.insert(0, './src')
import core as bd
import presenters as bd_present
import view_dash as bd_views_dash

# Define database info
db_info = bd.MongoDbDatabase(
    config_address, config_port, config_db_name, config_collection_name
)

# initialize table_data, then pass into db_info.query as the dataframe to store the output in

# Query database
query_output = db_info.query(config_requested_queries, config_requested_projections)

# Store query output as Table class; later this will enable adding columns to specify
# which sessions are selected
table_data = bd.Table(query_output)

# Initialize filter options
filter_criteria = bd.FilterCriteria()

# Filter for sessions meeting criteria
table_data.filter(filter_criteria)

# Convert the table to something useable by Dash
table_data_for_dash = bd_present.DashDataTable('testtable', table_data.df)

# Make a graph
pie_graph = bd_present.DashPieChart('testfig', table_data.df, config_data_to_plot)

# Make checkboxes
checkboxes = bd_present.DashFilterChecklist('testchecklist', config_filter_options)

# Make GUI
bd_views_dash.build_dash_app(table_data_for_dash, pie_graph, checkboxes)

veronica = 5
