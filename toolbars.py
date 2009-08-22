from gettext import gettext as _

from sugar.graphics.toolbarbox import ToolbarBox
from sugar.activity.widgets import ActivityToolbarButton
from sugar.activity.widgets import StopButton

class PrimaryToolbar(ToolbarBox):
    def __init__(self, act):
        ToolbarBox.__init__(self)
        
        self._activity = act
        
        activity_button = ActivityToolbarButton(self._activity)
        self.toolbar.insert(activity_button, 0)
        
        stop_button = StopButton(self._activity)
        self.toolbar.insert(stop_button, -1)