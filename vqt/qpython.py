'''
Home of some helpers for python interactive stuff.
'''
import types
import traceback

from threading import Thread
from PyQt4 import QtCore, QtGui

from vqt.main import idlethread
from vqt.basics import *

@idlethread
def scripterr(msg, info):
    msgbox = QtGui.QMessageBox()
    msgbox.setText('Script Error: %s' % msg)
    msgbox.setInformativeText(info)
    msgbox.exec_()

class ScriptThread(Thread):

    def __init__(self, cobj, locals):
        Thread.__init__(self)
        self.setDaemon(True)
        self.cobj = cobj
        self.locals = locals

    def run(self):
        try:
            exec(self.cobj, self.locals)
        except Exception, e:
            scripterr(str(e), traceback.format_exc())

class VQPythonView(QtGui.QWidget):

    def __init__(self, locals=None, parent=None):
        if locals == None:
            locals = {}

        self._locals = locals

        QtGui.QWidget.__init__(self, parent=parent)

        self._textWidget = QtGui.QTextEdit(parent=self)
        self._botWidget = QtGui.QWidget(parent=self)
        self._help_button = QtGui.QPushButton('?', parent=self._botWidget)
        self._run_button = QtGui.QPushButton('Run', parent=self._botWidget)
        self._run_button.clicked.connect(self._okClicked)
        self._help_button.clicked.connect( self._helpClicked ) 

        self._help_text = None

        hbox = HBox( None, self._help_button, self._run_button )
        self._botWidget.setLayout( hbox )

        vbox = VBox( self._textWidget, self._botWidget )
        self.setLayout( vbox )

        self.setWindowTitle('Python Interactive')

    def _okClicked(self):
        pycode = str(self._textWidget.document().toPlainText())
        cobj = compile(pycode, "vqpython_exec.py", "exec")
        sthr = ScriptThread(cobj, self._locals)
        sthr.start()

    def _helpClicked(self):
        withhelp = []
        for lname,lval in self._locals.items():
            if type(lval) in (types.ModuleType, ):
                continue
            doc = getattr(lval, '__doc__', '\nNo Documentation\n')
            if doc == None:
                doc = '\nNo Documentation\n'
            withhelp.append( (lname, doc) )

        withhelp.sort()

        txt = 'Objects/Functions in the namespace:\n'
        for name,doc in withhelp:
            txt += ( '====== %s\n' % name )
            txt += ( '%s\n' % doc )

        self._help_text = QtGui.QTextEdit()
        self._help_text.setReadOnly( True )
        self._help_text.setWindowTitle('Python Interactive Help')
        self._help_text.setText( txt )
        self._help_text.show()


