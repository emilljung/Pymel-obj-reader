from exporter import doSomething

class UIController(QObject):
    def __init__(self, ui):
        QObject.__init__(self)
        self.ui = ui
        self.ui.show()
        
        #Options
        self.onlySelection = False
        self.groups = False
        self.materials = False
        self.typeOfCoords = 'object'
	
	"""Connect buttons etc to functions"""
	ui.exportButton.clicked.connect(self.exportClicked)    # Export
	ui.pushButton_2.clicked.connect(self.buttonAClicked)   # Cancel
	ui.browse.clicked.connect(self.browseClicked)          # Browse
	ui.checkBox.stateChanged.connect(self.check1Changed)   # Only Selection
	ui.checkBox_2.stateChanged.connect(self.check2Changed) # Groups
	ui.checkBox_4.stateChanged.connect(self.check4Changed) # Global or world coords 
	ui.checkBox_3.stateChanged.connect(self.check3Changed) # Materials

    def showUI(self):
        self.ui.show()

    def hideUI(self):
        self.ui.hide()

    def exportClicked(self):
        #Split path string to get file name and path
        pathSplit = self.ui.lineEdit.text().split('/') #pathSplit[-1] = file name
        path = ""
        
        for x in pathSplit[0:-1]: #Loop through all but the last one (which is the file name)
            path += x + '/'
        
        doSomething(self.onlySelection, self.groups, self.materials, self.typeOfCoords, path, pathSplit[-1])

    def browseClicked(self):
        self.ui.lineEdit.setText(pm.fileDialog(m=1)[:-2]) #m=1 write, m=0 read

    def buttonAClicked(self):
        self.ui.close()

    #Only selection
    def check1Changed(self, state):
        if self.ui.checkBox.isChecked():
            self.onlySelection = True
        else:
            self.onlySelection = False

    #Groups
    def check2Changed(self, state):
        if self.ui.checkBox_2.isChecked():
            self.groups = True
        else:
            self.groups = False

    #Materials
    def check3Changed(self, state):
        if self.ui.checkBox_3.isChecked():
            self.materials = True
        else:
            self.materials = False
        
    #Global or world coords
    def check4Changed(self, state):
        if self.ui.checkBox_4.isChecked():
            self.typeOfCoords = 'world'
        else:
            self.typeOfCoords = 'object'