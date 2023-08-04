import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, dcc, html

from src.dashboard_pages import ChartHandler

app = Dash(
    external_stylesheets=[dbc.themes.LUX],
    suppress_callback_exceptions=True,
)


class DashBoard:
    """Dashboard to show information."""

    def __init__(self) -> None:
        """Initialize."""
        # contents for the main page
        self.home_contents = ChartHandler(app)

    def run(self) -> None:
        """Run."""
        app.layout = self._build_layout()

        # rendering pages
        @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
        def render_page_content(pathname):
            if pathname == "/":
                return self.home_contents.show()
            # elif pathname == "/dummy":
            #     return html.P("This is dummy page. Yay!")
            return html.P("404: Not found", className="text-danger")

        app.run_server(debug=True)

    def _build_layout(self) -> html.Div:
        """Build layout."""
        return html.Div(
            children=[
                dcc.Location(id="url"),
                self._get_sidebar(),
                self._get_contents(),
            ],
            style={"margin-top": "40px"},
        )

    def _get_sidebar(self) -> html.Div:
        """Get a sidebar."""
        SIDEBAR_STYLE = {
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "25rem",
            "padding": "2rem 1rem",
            "background-color": "#f8f9fa",
        }

        sidebar = html.Div(
            [
                html.H1("Upbit Dashboard", className="display-6"),
                html.Hr(),
                html.P("A simple sidebar with navigations.", className="lead"),
                dbc.Nav(
                    children=[
                        dbc.NavLink("Home", href="/", active="exact"),
                        # dbc.NavLink("Dummy Page", href="/dummy", active="exact"),
                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
            style=SIDEBAR_STYLE,
        )
        return sidebar

    def _get_contents(self) -> html.Div:
        """Get overall contents."""
        CONTENTS_STYLE = {
            "margin-left": "27rem",
            "margin-right": "2rem",
            "padding": "2rem 1rem",
        }
        content = html.Div(id="page-content", style=CONTENTS_STYLE)
        return content
