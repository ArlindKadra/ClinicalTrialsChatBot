from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QLineEdit, QTabWidget, QScrollArea, QSizePolicy
from PyQt5.QtWidgets import QAbstractScrollArea, QAction
from src.MapWidget import MapWidget
from src.DialogWidget import DialogWidget
from src.InputConsole import InputConsole
from src.DialogFlow import DialogFlow
from src.TreeWidget import TreeWidget
from src.ChartWidget import ChartWidget
from src.DatabaseConnector import DatabaseConnector
from src.HintWindow import HintWindow
from src.LogWindow import logger, LogWindow

from src.DBConnector import DBConnector


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setCentralWidget(QWidget(self))
        self.l_h = QHBoxLayout(self.centralWidget())

        # Initialize all components
        self.map_widget = MapWidget(self.centralWidget())
        self.chart_widget = ChartWidget(self.centralWidget())
        self.disease_widget = TreeWidget("disease", self.centralWidget())
        self.drug_widget = TreeWidget("drug", self.centralWidget())
        self.dialog_widget = DialogWidget(self.centralWidget())
        self.input_console = InputConsole(self.centralWidget())
        self.dialogflow = DialogFlow(self)
        #self.database_connector = DatabaseConnector(self)
        self.database_connector = DBConnector(self)

        # Arrange components in a layout
        self.l_h_left = QHBoxLayout()
        self.l_v_middle = QVBoxLayout()
        self.l_v_right = QVBoxLayout()

        self.l_h.addLayout(self.l_h_left, 1)
        self.l_h.addLayout(self.l_v_middle, 3)
        self.l_h.addLayout(self.l_v_right, 2)

        self.tab_widget_visualization = QTabWidget(self.centralWidget())
        self.scroll_area = QScrollArea(self.centralWidget())
        self.scroll_area.setWidget(self.chart_widget)
        self.scroll_area.setWidgetResizable(True)
        self.tab_widget_visualization.addTab(self.scroll_area, 'Chart')
        self.tab_widget_visualization.addTab(self.map_widget, 'Map')
        self.l_v_middle.addWidget(self.tab_widget_visualization)

        self.l_v_right.addWidget(self.dialog_widget)
        self.l_v_right.addWidget(self.input_console)

        self.tab_widget = QTabWidget(self.centralWidget())
        self.tab_widget.addTab(self.disease_widget, 'Disease')
        self.tab_widget.addTab(self.drug_widget, 'Drug')

        self.l_h_left.addWidget(self.tab_widget, 1)

        # Declare interaction between the components
        self.input_console.user_message_entered_signal.connect(self.dialogflow.process_user_message)

        # Highlight diseases and drugs for which we search in the database
        self.dialogflow.bot_request_signal.connect(self.disease_widget.highlight_bot_request)
        self.dialogflow.bot_request_signal.connect(self.drug_widget.highlight_bot_request)

        # Display conversation
        self.dialogflow.user_speak_signal.connect(self.dialog_widget.user_message_entered)
        self.dialogflow.bot_speak_signal.connect(self.dialog_widget.bot_message_entered)

        # Query SQL database
        self.dialogflow.bot_request_signal.connect(self.database_connector.process_bot_request)

        # Display query on the chart and on the map
        self.database_connector.bot_request_processed_signal.connect(self.map_widget.display_processed_request)
        self.database_connector.bot_request_processed_signal.connect(self.chart_widget.display_processed_request)

        # Add some additional features
        # Double click on the disease and drug tree will insert text to the input_console
        self.disease_widget.element_selected.connect(self.input_console.insert)
        self.drug_widget.element_selected.connect(self.input_console.insert)

        # Add additional actions
        self.file_menu = self.menuBar().addMenu('File')

        self.log_window = LogWindow()
        self.open_log_action = QAction('Open Log')
        self.open_log_action.triggered.connect(self.log_window.show)
        self.file_menu.addAction(self.open_log_action)
        logger.set_log_window(self.log_window)

        self.hint_window = HintWindow()
        self.open_hints_action = QAction('Tips and Hints')
        self.open_hints_action.triggered.connect(self.hint_window.show)
        self.file_menu.addAction(self.open_hints_action)

        logger.log('Start application')

