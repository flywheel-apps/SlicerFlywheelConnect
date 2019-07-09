import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# flywheel_connect
#

class flywheel_connect(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    try:
      import flywheel
    except Exception e:
      from pip._internal import main as pipmain
      pipmain(["install","flywheel-sdk"])
      import flywheel

    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "flywheel_connect" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Joshua Jacobs (flywheel.io)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# flywheel_connectWidget
#

class flywheel_connectWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    self.CacheDir='/Users/joshuajacobs/flywheelIO/' #TODO: Make an EditLine for this.... 
    # Give a line_edit and label for the API key
    self.apiKeyCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
    self.apiKeyCollapsibleGroupBox.setTitle('API Key Entry')

    self.layout.addWidget(self.apiKeyCollapsibleGroupBox)
    apiKeyFormLayout = qt.QFormLayout(self.apiKeyCollapsibleGroupBox)  

    # 
    # api Key Text Box
    # 
    self.apiKeyTextLabel = qt.QLabel('API Key:')
    apiKeyFormLayout.addWidget(self.apiKeyTextLabel)
    self.apiKeyTexBox =qt.QLineEdit()
    apiKeyFormLayout.addWidget(self.apiKeyTexBox)
    self.connectAPIButton = qt.QPushButton('Connect Flywheel')
    self.connectAPIButton.enabled = False
    apiKeyFormLayout.addWidget(self.connectAPIButton)


    self.groupsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
    self.groupsCollapsibleGroupBox.setTitle('groups')
    self.layout.addWidget(self.groupsCollapsibleGroupBox)
    
    groupsFormLayout = qt.QFormLayout(self.groupsCollapsibleGroupBox)

    #
    # group Selector ComboBox
    #
    self.groupSelectorLabel = qt.QLabel('Current group:')
    groupsFormLayout.addWidget(self.groupSelectorLabel)
    # Selector ComboBox
    self.groupSelector = qt.QComboBox()
    self.groupSelector.enabled = False
    self.groupSelector.setMinimumWidth(200)
    groupsFormLayout.addWidget(self.groupSelector)
    
    #
    # Use Cache CheckBox
    #
    self.useCacheCeckBox = qt.QCheckBox("Cache server responses")
    self.useCacheCeckBox.toolTip = '''For faster browsing if this box is checked\
    the browser will cache server responses and on further calls\
    would populate tables based on saved data on disk.'''

    groupsFormLayout.addWidget(self.useCacheCeckBox)
    self.useCacheCeckBox.setCheckState(True)
    self.useCacheCeckBox.setTristate(False)

    #
    # projects selector Form Area'
    #

    self.projectsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
    self.projectsCollapsibleGroupBox.setTitle('projects')
    self.layout.addWidget(self.projectsCollapsibleGroupBox)
    
    projectsFormLayout = qt.QFormLayout(self.projectsCollapsibleGroupBox)

    #
    # project Selector ComboBox
    #
    self.projectSelectorLabel = qt.QLabel('Current project:')
    projectsFormLayout.addWidget(self.projectSelectorLabel)
    # Selector ComboBox
    self.projectSelector = qt.QComboBox()
    self.projectSelector.enabled = False
    self.projectSelector.setMinimumWidth(200)
    projectsFormLayout.addWidget(self.projectSelector)

    """ #
    # subjects selector Form Area'
    #
    self.subjectsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
    self.subjectsCollapsibleGroupBox.setTitle('subjects')
    self.layout.addWidget(self.subjectsCollapsibleGroupBox)
    
    subjectsFormLayout = qt.QFormLayout(self.subjectsCollapsibleGroupBox)

    #
    # subject Selector ComboBox
    #
    self.subjectSelectorLabel = qt.QLabel('Current subject:')
    subjectsFormLayout.addWidget(self.subjectSelectorLabel)
    # Selector ComboBox
    self.subjectSelector = qt.QComboBox()
    self.subjectSelector.setMinimumWidth(200)
    subjectsFormLayout.addWidget(self.subjectSelector) """

    #
    # sessions selector Form Area'
    #
    
    self.sessionsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
    self.sessionsCollapsibleGroupBox.setTitle('sessions')
    self.layout.addWidget(self.sessionsCollapsibleGroupBox)
    
    sessionsFormLayout = qt.QFormLayout(self.sessionsCollapsibleGroupBox)

    #
    # session Selector ComboBox
    #
    self.sessionSelectorLabel = qt.QLabel('Current session:')
    sessionsFormLayout.addWidget(self.sessionSelectorLabel)
    # Selector ComboBox
    self.sessionSelector = qt.QComboBox()
    self.sessionSelector.enabled = False
    self.sessionSelector.setMinimumWidth(200)
    sessionsFormLayout.addWidget(self.sessionSelector)
    
    #
    # acquisitions selector Form Area'
    #
    
    self.acquisitionsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
    self.acquisitionsCollapsibleGroupBox.setTitle('acquisitions')
    self.layout.addWidget(self.acquisitionsCollapsibleGroupBox)
    
    acquisitionsFormLayout = qt.QFormLayout(self.acquisitionsCollapsibleGroupBox)

    #
    # acquisition Selector ComboBox
    #
    self.acquisitionSelectorLabel = qt.QLabel('Current acquisition:')
    acquisitionsFormLayout.addWidget(self.acquisitionSelectorLabel)
    # Selector ComboBox
    self.acquisitionSelector = qt.QComboBox()
    self.acquisitionSelector.enabled = False
    self.acquisitionSelector.setMinimumWidth(200)
    acquisitionsFormLayout.addWidget(self.acquisitionSelector)
    self.acquisitionButton = qt.QPushButton('Retrieve Acquisition')
    self.acquisitionButton.enabled = False
    acquisitionsFormLayout.addWidget(self.acquisitionButton)
    
    # connections
    self.apiKeyTexBox.connect('textChanged(QString)',self.onApiKeyTextChanged)
    self.connectAPIButton.connect('clicked(bool)',self.onConnectAPIPushed)
    self.groupSelector.connect('currentIndexChanged(QString)',self.onGroupSelected)
    self.projectSelector.connect('currentIndexChanged(QString)',self.onProjectSelected)
    self.sessionSelector.connect('currentIndexChanged(QString)', self.onSessionSelected)
    self.acquisitionSelector.connect('currentIndexChanged(QString)',self.onAcquisitionSelected)
    self.acquisitionButton.connect('clicked(bool)',self.onAcquisitionPushed)
    
    # Add vertical spacer
    self.layout.addStretch(1)

  def onApiKeyTextChanged(self,item):
    self.connectAPIButton.enabled=True

  def onConnectAPIPushed(self):
    # Instantiate and connect widgets ...
    self.fw = flywheel.Client(self.apiKeyTexBox.text)
    #if client valid: TODO
    groups=self.fw.groups()
    self.groupSelector.enabled = True
    self.groupSelector.clear()
    for group in groups:
      self.groupSelector.addItem(group.label,group.id)

  def onGroupSelected(self,item):
    self.group = self.fw.get(self.groupSelector.currentData)
    self.projectSelector.enabled = True
    self.projectSelector.clear()
    projects=self.group.projects()
    for project in projects:
      self.projectSelector.addItem(project.label,project.id)

  def onProjectSelected(self,item):
    self.project = self.group.projects()[self.projectSelector.currentIndex]
    sessions = self.project.sessions()
    self.sessionSelector.enabled = True
    self.sessionSelector.clear()
    for session in sessions:
      self.sessionSelector.addItem(session.label,session.id)

  def onSessionSelected(self,item):
    self.session = self.project.sessions()[self.sessionSelector.currentIndex]
    acquisitions= self.session.acquisitions()
    self.acquisitionSelector.enabled = True
    self.acquisitionSelector.clear()
    self.acquisitionButton.enabled = True
    for acquisition in acquisitions:
      self.acquisitionSelector.addItem(acquisition.label,acquisition.id)
      
  def onAcquisitionSelected(self,item):
    self.acquisition = self.session.acquisitions()[self.acquisitionSelector.currentIndex]
    

  def onAcquisitionPushed(self):
    self.acquisition.download_file(self.acquisition.files[0].name,self.CacheDir+ '/' + self.acquisition.files[0].name)
    if 'seg' in self.acquisition.files[0].name:
    	slicer.util.loadLabelVolume(self.CacheDir + '/' + self.acquisition.files[0].name)
    else:
    	slicer.util.loadVolume(self.CacheDir + '/' + self.acquisition.files[0].name)
    
  def cleanup(self):
    pass

  """ def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = flywheel_connectLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag) """

#
# flywheel_connectLogic
#

class flywheel_connectLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('flywheel_connectTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class flywheel_connectTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_flywheel_connect1()

  def test_flywheel_connect1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = flywheel_connectLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
