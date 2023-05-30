"""Dash UI elements to show data as figures and graphs"""

import datafigure as fig
from dash import dcc
import plotly.express as px

class DashPieChart(fig.PieChart):
    """Create pie chart"""

    def __init__(self, graph_object):
        """Get and store figure options and other properties

        Args:
            graph_object (PieChart class from Presenter module): title and options for
            the graph
        """
        super().__init__(graph_object)

    def build(self):
        """Build plot for user interface

        Returns:
            dcc.Graph: Dash pie graph
        """

        return dcc.Graph(
            id=self.id,
            figure=px.pie(
                data_frame=self.df,
                names=list(self.df.columns.values)[0],
                title=self.title,
            ),
        )


class DashBarGraph(fig.BarGraph):
    """Create bar graph"""

    def __init__(self, graph_object):
        """Get and store figure options and other properties

        Args:
            graph_object (BarGraph class from Presenter module): title and options for
            the graph
        """
        super().__init__(graph_object)

    def build(self):
        """Build plot for user interface

        Returns:
            dcc.Graph: Dash histogram
        """

        return dcc.Graph(
            id=self.id,
            figure=px.histogram(
                data_frame=self.df,
                x=self.col_to_plot,
                title=self.title,
            ),
        )


class DashScatterPlot(fig.ScatterPlot):
    """Scatterplot figure"""

    def __init__(self, graph_object):
        """Get and store figure options and other properties

        Args:
            graph_object (ScatterPlot class from Presenter module): title and options for
            the graph
        """
        super().__init__(graph_object)

    def build(self):
        """Build plot for user interface

        Returns:
            dcc.Graph: Dash scatter plot
        """

        scatter_plot = dcc.Graph(
            id=self.id,
            figure=px.scatter(
                data_frame=self.df,
                x=self.col_to_plot[1],
                y=self.col_to_plot[0],
                # names = list(self.df.columns.values)[0],
                title=self.title,
            ),
        )

        # Update selection mode to avoid the error:
        #   unrecognized GUI edit: selections[0].xref
        # Otherwise, after selecting points in a dataframe, there is an error
        # (use the inspector in the browser to see the error) on plotly.js
        # versions 2.13.2 and 2.13.3.
        # https://github.com/plotly/react-plotly.js/issues/290
        # Here is a list of plotly versions and which version of plotly.js
        # they use:
        # https://github.com/plotly/plotly.py/releases
        # I got the error in plotly v5.11.0, 5.13.1, 5.9.0, and 5.8.2.
        # The error only occurs if the scatterplot data is updated as an output
        # after selecting points from the scatterplot, not if the points are updated
        # after selecting via checkboxes or pie graphs.
        scatter_plot.figure.update_layout(
            newselection_mode="gradual",
        )

        return scatter_plot