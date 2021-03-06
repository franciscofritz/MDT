import signal
import sys

from PyQt5.QtCore import pyqtSignal

from mdt.gui.model_fit.design.ui_about_dialog import Ui_AboutDialog
from mdt.gui.model_fit.design.ui_runtime_settings_dialog import Ui_RuntimeSettingsDialog
from mdt.gui.model_fit.tabs.fit_model_tab import FitModelTab
from mdt.gui.model_fit.tabs.generate_brain_mask_tab import GenerateBrainMaskTab
from mdt.gui.model_fit.tabs.generate_roi_mask_tab import GenerateROIMaskTab
from mdt.gui.model_fit.tabs.view_results_tab import ViewResultsTab

import mdt.utils
import mot.configuration
from mdt.configuration import update_gui_config
from mdt.gui.model_fit.tabs.generate_protocol_tab import GenerateProtocolTab
from mot.cl_environments import CLEnvironmentFactory
from mot.load_balance_strategies import EvenDistribution

try:
    #python 2.7
    from Queue import Queue
except ImportError:
    # python 3.4
    from queue import Queue
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, QTimer, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QDialog, QDialogButtonBox
from mdt.gui.model_fit.design.ui_main_gui import Ui_MainWindow
from mdt.gui.utils import print_welcome_message, ForwardingListener, MessageReceiver, center_window, QtManager
from mdt.gui.model_fit.utils import SharedState
from mdt.log_handlers import LogDispatchHandler

__author__ = 'Robbert Harms'
__date__ = "2016-06-26"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


class MDTGUISingleModel(QMainWindow, Ui_MainWindow):

    def __init__(self, shared_state, computations_thread):
        super(MDTGUISingleModel, self).__init__()
        self.setupUi(self)
        self._shared_state = shared_state

        self._computations_thread = computations_thread
        self._computations_thread.signal_starting.connect(self.computations_started)
        self._computations_thread.signal_finished.connect(self.computations_finished)

        self._stdout_old = sys.stdout
        self._stderr_old = sys.stderr
        self._logging_update_queue = Queue()
        self._logging_update_thread = QThread()

        self._message_receiver = MessageReceiver(self._logging_update_queue)
        self._message_receiver.text_message_signal.connect(self.update_log)

        self._message_receiver.moveToThread(self._logging_update_thread)
        self._logging_update_thread.started.connect(self._message_receiver.run)
        self._logging_update_thread.start()
        self._connect_output_textbox()

        self.actionExit.setShortcuts(['Ctrl+q', 'Ctrl+w'])

        self.action_RuntimeSettings.triggered.connect(lambda: RuntimeSettingsDialog(self).exec_())
        self.actionAbout.triggered.connect(lambda: AboutDialog(self).exec_())

        self.executionStatusLabel.setText('Idle')
        self.executionStatusIcon.setPixmap(QtGui.QPixmap(":/main_gui/icon_status_red.png"))

        self.fit_model_tab = FitModelTab(shared_state, self._computations_thread)
        self.fit_model_tab.setupUi(self.fitModelTab)

        self.generate_mask_tab = GenerateBrainMaskTab(shared_state, self._computations_thread)
        self.generate_mask_tab.setupUi(self.generateBrainMaskTab)

        self.view_results_tab = ViewResultsTab(shared_state, self._computations_thread)
        self.view_results_tab.setupUi(self.viewResultsTab)

        self.generate_roi_mask_tab = GenerateROIMaskTab(shared_state, self._computations_thread)
        self.generate_roi_mask_tab.setupUi(self.generateROIMaskTab)

        self.generate_protocol_tab = GenerateProtocolTab(shared_state, self._computations_thread)
        self.generate_protocol_tab.setupUi(self.generateProtocolTab)

        self.tabs = [self.fit_model_tab, self.generate_mask_tab, self.generate_roi_mask_tab,
                     self.generate_protocol_tab, self.view_results_tab]

        self.MainTabs.currentChanged.connect(lambda index: self.tabs[index].tab_opened())

    def _connect_output_textbox(self):
        sys.stdout = ForwardingListener(self._logging_update_queue)
        sys.stderr = ForwardingListener(self._logging_update_queue)
        LogDispatchHandler.add_listener(ForwardingListener(self._logging_update_queue))
        print_welcome_message()

    def closeEvent(self, event):
        sys.stdout = self._stdout_old
        sys.stderr = self._stderr_old
        self._message_receiver.is_running = False
        self._logging_update_thread.quit()
        self._logging_update_thread.wait(10)
        super(MDTGUISingleModel, self).closeEvent(event)

    def send_sigint(self, *args):
        self.close()

    @pyqtSlot()
    def computations_started(self):
        self.executionStatusLabel.setText('Computing')
        self.executionStatusIcon.setPixmap(QtGui.QPixmap(":/main_gui/icon_status_green.png"))

    @pyqtSlot()
    def computations_finished(self):
        self.executionStatusLabel.setText('Idle')
        self.executionStatusIcon.setPixmap(QtGui.QPixmap(":/main_gui/icon_status_red.png"))

    @pyqtSlot(str)
    def update_log(self, string):
        sb = self.loggingTextBox.verticalScrollBar()
        scrollbar_position = sb.value()
        autoscroll = scrollbar_position == sb.maximum()
        self.loggingTextBox.moveCursor(QtGui.QTextCursor.End)
        self.loggingTextBox.insertPlainText(string)

        if autoscroll:
            sb.setValue(sb.maximum())
        else:
            sb.setValue(scrollbar_position)


class RuntimeSettingsDialog(Ui_RuntimeSettingsDialog, QDialog):

    def __init__(self, parent):
        super(RuntimeSettingsDialog, self).__init__(parent)
        self.setupUi(self)

        self.all_cl_devices = CLEnvironmentFactory.smart_device_selection()
        self.user_selected_devices = mot.configuration.get_cl_environments()
        self.cldevicesSelection.itemSelectionChanged.connect(self.selection_updated)

        self.cldevicesSelection.insertItems(0, [str(cl_device) for cl_device in self.all_cl_devices])

        load_balancer = mot.configuration.get_load_balancer()
        lb_used_devices = load_balancer.get_used_cl_environments(self.all_cl_devices)

        for ind, device in enumerate(self.all_cl_devices):
            self.cldevicesSelection.item(ind).setSelected(device in self.user_selected_devices
                                                          and device in lb_used_devices)

        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self._update_settings)

    @pyqtSlot()
    def selection_updated(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            any(self.cldevicesSelection.item(ind).isSelected() for ind in range(self.cldevicesSelection.count())))

    def _update_settings(self):
        selection = [ind for ind in range(self.cldevicesSelection.count())
                     if self.cldevicesSelection.item(ind).isSelected()]
        mot.configuration.set_cl_environments([self.all_cl_devices[ind] for ind in selection])
        mot.configuration.set_load_balancer(EvenDistribution())

        update_gui_config({'runtime_settings': {'cl_device_ind': selection}})


class AboutDialog(Ui_AboutDialog, QDialog):

    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        self.contentLabel.setText(self.contentLabel.text().replace('{version}', mdt.__version__))


class ComputationsThread(QThread):

    signal_starting = pyqtSignal()
    signal_finished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        """This is the thread handler for the computations.

        When running computations using this thread please connect signals to the starting and finished slot of this
        class. These handlers notify the main window of the computations.
        """
        super(ComputationsThread, self).__init__(*args, **kwargs)

    @pyqtSlot()
    def starting(self):
        self.signal_starting.emit()

    @pyqtSlot()
    def finished(self):
        self.signal_finished.emit()


def start_gui(base_dir=None, app_exec=True):
    """Start the model fitting GUI.

    Args:
        base_dir (str): the starting directory for the file opening actions
        app_exec (boolean): if true we execute the Qt application, set to false to disable.
    """
    try:
        mdt.configuration.load_user_gui()
    except IOError:
        pass

    app = QtManager.get_qt_application_instance()

    state = SharedState()
    state.base_dir = base_dir

    computations_thread = ComputationsThread()
    computations_thread.start()

    # catches the sigint
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    composite_model_gui = MDTGUISingleModel(state, computations_thread)
    signal.signal(signal.SIGINT, composite_model_gui.send_sigint)

    center_window(composite_model_gui)
    composite_model_gui.show()

    QtManager.add_window(composite_model_gui)
    if app_exec:
        QtManager.exec_()


if __name__ == '__main__':
    start_gui()
