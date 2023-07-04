"""UI elements to show data as figures and graphs"""

import uielement as uielement


class DataFigure(uielement.UiElement):
    """General class for figures"""

    def __init__(self, UIelement):
        """Set the type property of the data figure

        Args:
            UIelement (the appropriate DataFigure class from the Presenter module):
            contains all information required to build the figure
        """
        super().__init__(UIelement)
        # Set type of UI element
        self.id["type"] = "DataFigure"

    def build(self):
        pass


class PieChart(DataFigure):
    """Create pie chart"""

    def __init__(self, graph_object):
        """Get and store figure options and other properties

        Args:
            graph_object (PieChart class from Presenter module): title and options for
            the graph
        """
        super().__init__(graph_object)

        # Set type of UI element
        self.id["type"] = "PieChart"

        # Duplicate fields from graph_object [there's got to be a nicer way to do this]
        self.field = graph_object.col_to_plot
        self.df = graph_object.df
        self.graph_type = graph_object.graph_type
        self.title = graph_object.title


class BarGraph(DataFigure):
    """Create bar graph"""

    def __init__(self, graph_object):
        """Get and store figure options and other properties

        Args:
            graph_object (BarGraph class from Presenter module): title and options for
            the graph
        """
        super().__init__(graph_object)

        # Set type of UI element
        self.id["type"] = "BarGraph"

        # Duplicate fields from graph_object [there's got to be a nicer way to do this]
        # self.col_to_plot = graph_object.col_to_plot
        self.field = graph_object.field
        self.df = graph_object.df
        self.graph_type = graph_object.graph_type
        self.title = graph_object.title


class ScatterPlot(DataFigure):
    """Scatterplot figure"""

    def __init__(self, graph_object):
        """Get and store figure options and other properties

        Args:
            graph_object (ScatterPlot class from Presenter module): title and options for
            the graph
        """
        super().__init__(graph_object)

        # Set type of UI element
        self.id["type"] = "ScatterPlot"

        # Duplicate fields from graph_object [there's got to be a nicer way to do this]
        # self.col_to_plot = graph_object.col_to_plot
        self.field = graph_object.field
        self.df = graph_object.df
        self.graph_type = graph_object.graph_type
        self.title = graph_object.title
