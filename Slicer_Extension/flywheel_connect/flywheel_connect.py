import logging
import os
import os.path as op
import shutil
import subprocess
import sys
import unittest
from importlib import import_module

import ctk
import qt
import slicer
import vtk
from slicer.ScriptedLoadableModule import *


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


#
# flywheel_connect
#


class flywheel_connect(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        FlyW = ""
        try:
            FlyW = import_module("flywheel")
        except Exception:
            install("flywheel-sdk")
            FlyW = import_module("flywheel")
        globals()["flywheel"] = FlyW

        ScriptedLoadableModule.__init__(self, parent)
        # TODO make this more human readable by adding spaces
        self.parent.title = "flywheel_connect"
        self.parent.categories = ["Flywheel"]
        self.parent.dependencies = []
        # replace with "Firstname Lastname (Organization)"
        self.parent.contributors = ["Joshua Jacobs (flywheel.io)"]
        self.parent.helpText = (
            "This is an example of scripted loadable module bundled in an extension."
            "It performs a simple thresholding on the input volume and optionally"
            "captures a screenshot."
        )
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = (
            "This file was originally developed by Jean-Christophe Fillion-Robin,"
            "Kitware Inc. and Steve Pieper, Isomics, Inc. and was partially funded"
            "by NIH grant 3P41RR013218-12S1."
        )  # replace with organization, grant and thanks.


#
# flywheel_connectWidget
#


class flywheel_connectWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.CacheDir = os.path.expanduser("~") + "/flywheelIO/"

        # Give a line_edit and label for the API key
        self.apiKeyCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
        self.apiKeyCollapsibleGroupBox.setTitle("API Key Entry")

        self.layout.addWidget(self.apiKeyCollapsibleGroupBox)
        apiKeyFormLayout = qt.QFormLayout(self.apiKeyCollapsibleGroupBox)

        #
        # api Key Text Box
        #
        self.apiKeyTextLabel = qt.QLabel("API Key:")
        apiKeyFormLayout.addWidget(self.apiKeyTextLabel)
        self.apiKeyTextBox = qt.QLineEdit()
        self.apiKeyTextBox.setEchoMode(qt.QLineEdit.Password)
        apiKeyFormLayout.addWidget(self.apiKeyTextBox)
        self.connectAPIButton = qt.QPushButton("Connect Flywheel")
        self.connectAPIButton.enabled = True
        apiKeyFormLayout.addWidget(self.connectAPIButton)

        self.logAlertTextLabel = qt.QLabel("")
        apiKeyFormLayout.addWidget(self.logAlertTextLabel)

        #
        # CacheDir Text Box
        #
        self.cacheDirTextLabel = qt.QLabel("Disk Cache:")
        apiKeyFormLayout.addWidget(self.cacheDirTextLabel)
        self.cacheDirTextBox = qt.QLineEdit()
        self.cacheDirTextBox.setText(self.CacheDir)
        apiKeyFormLayout.addWidget(self.cacheDirTextBox)

        #
        # Use Cache CheckBox
        #
        self.useCacheCheckBox = qt.QCheckBox("Cache Images")
        self.useCacheCheckBox.toolTip = (
            """Images cached to "Disk Cache"."""
            "Otherwise, deleted at every new retrieval."
        )

        apiKeyFormLayout.addWidget(self.useCacheCheckBox)
        self.useCacheCheckBox.setCheckState(True)
        self.useCacheCheckBox.setTristate(False)

        self.groupsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
        self.groupsCollapsibleGroupBox.setTitle("groups")
        self.layout.addWidget(self.groupsCollapsibleGroupBox)

        groupsFormLayout = qt.QFormLayout(self.groupsCollapsibleGroupBox)

        #
        # group Selector ComboBox
        #
        self.groupSelectorLabel = qt.QLabel("Current group:")
        groupsFormLayout.addWidget(self.groupSelectorLabel)

        # Selector ComboBox
        self.groupSelector = qt.QComboBox()
        self.groupSelector.enabled = False
        self.groupSelector.setMinimumWidth(200)
        groupsFormLayout.addWidget(self.groupSelector)

        #
        # projects selector Form Area'
        #
        self.projectsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
        self.projectsCollapsibleGroupBox.setTitle("projects")
        self.layout.addWidget(self.projectsCollapsibleGroupBox)

        projectsFormLayout = qt.QFormLayout(self.projectsCollapsibleGroupBox)

        #
        # project Selector ComboBox
        #
        self.projectSelectorLabel = qt.QLabel("Current project:")
        projectsFormLayout.addWidget(self.projectSelectorLabel)
        # Selector ComboBox
        self.projectSelector = qt.QComboBox()
        self.projectSelector.enabled = False
        self.projectSelector.setMinimumWidth(200)
        projectsFormLayout.addWidget(self.projectSelector)

        #
        # sessions selector Form Area'
        #
        self.sessionsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
        self.sessionsCollapsibleGroupBox.setTitle("sessions")
        self.layout.addWidget(self.sessionsCollapsibleGroupBox)

        sessionsFormLayout = qt.QFormLayout(self.sessionsCollapsibleGroupBox)

        #
        # session Selector ComboBox
        #
        self.sessionSelectorLabel = qt.QLabel("Current session:")
        sessionsFormLayout.addWidget(self.sessionSelectorLabel)
        # Selector ComboBox
        self.sessionSelector = qt.QComboBox()
        self.sessionSelector.enabled = False
        self.sessionSelector.setMinimumWidth(200)
        sessionsFormLayout.addWidget(self.sessionSelector)

        #
        # session-level Analysis Selector ComboBox
        #
        self.analysisSelectorLabel = qt.QLabel("Analyses:")
        sessionsFormLayout.addWidget(self.analysisSelectorLabel)
        # Selector ComboBox
        self.analysisSelector = qt.QComboBox()
        self.analysisSelector.enabled = False
        self.analysisSelector.setMinimumWidth(200)
        sessionsFormLayout.addWidget(self.analysisSelector)

        #
        # session-level Analysis-file Selector ComboBox
        #
        self.analysisFilesSelectorLabel = qt.QLabel("Analysis-files:")
        sessionsFormLayout.addWidget(self.analysisFilesSelectorLabel)
        # Selector ComboBox
        self.analysisFilesSelector = qt.QComboBox()
        self.analysisFilesSelector.enabled = False
        self.analysisFilesSelector.setMinimumWidth(200)
        sessionsFormLayout.addWidget(self.analysisFilesSelector)

        self.analysisFileButton = qt.QPushButton("Retrieve Analysis File")
        self.analysisFileButton.enabled = False
        sessionsFormLayout.addWidget(self.analysisFileButton)

        #
        # acquisitions selector Form Area'
        #
        self.acquisitionsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
        self.acquisitionsCollapsibleGroupBox.setTitle("acquisitions")
        self.layout.addWidget(self.acquisitionsCollapsibleGroupBox)

        acquisitionsFormLayout = qt.QFormLayout(self.acquisitionsCollapsibleGroupBox)

        #
        # acquisition Selector ComboBox
        #
        self.acquisitionSelectorLabel = qt.QLabel("Current acquisition:")
        acquisitionsFormLayout.addWidget(self.acquisitionSelectorLabel)
        # Selector ComboBox
        self.acquisitionSelector = qt.QComboBox()
        self.acquisitionSelector.enabled = False
        self.acquisitionSelector.setMinimumWidth(200)
        acquisitionsFormLayout.addWidget(self.acquisitionSelector)

        #
        # acquisition-level file Selector ComboBox
        #
        self.acquisitionFilesSelectorLabel = qt.QLabel("Acquisition-files:")
        acquisitionsFormLayout.addWidget(self.acquisitionFilesSelectorLabel)
        # Selector ComboBox
        self.acquisitionFilesSelector = qt.QComboBox()
        self.acquisitionFilesSelector.enabled = False
        self.acquisitionFilesSelector.setMinimumWidth(200)
        acquisitionsFormLayout.addWidget(self.acquisitionFilesSelector)

        self.acquisitionFileButton = qt.QPushButton("Retrieve Acquisition File")
        self.acquisitionFileButton.enabled = False
        acquisitionsFormLayout.addWidget(self.acquisitionFileButton)

        #
        # Segmentations selector Form Area'
        #
        self.segmentationsCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
        self.segmentationsCollapsibleGroupBox.setTitle("segmentations")
        self.layout.addWidget(self.segmentationsCollapsibleGroupBox)

        segmentationsFormLayout = qt.QFormLayout(self.segmentationsCollapsibleGroupBox)

        #
        # Segmentations Selector ComboBox
        #
        self.segmentationsSelectorLabel = qt.QLabel("Current segmentation:")
        segmentationsFormLayout.addWidget(self.acquisitionSelectorLabel)
        # Selector ComboBox
        self.segmentationSelector = slicer.qMRMLNodeComboBox()
        self.segmentationSelector.nodeTypes = (("vtkMRMLSegmentationNode"), "")
        self.segmentationSelector.noneEnabled = False
        self.segmentationSelector.setMRMLScene(slicer.mrmlScene)
        self.segmentationSelector.setToolTip("Select fixed segmentation")
        self.segmentationSelector.name = "segmentationSelector"

        segmentationsFormLayout.addWidget(self.segmentationSelector)
        self.segmentationButton = qt.QPushButton("Upload Segmentation")
        self.segmentationButton.enabled = False
        segmentationsFormLayout.addWidget(self.segmentationButton)

        # connect signals and slots
        # self.apiKeyTextBox.connect("textChanged(QString)", self.onApiKeyTextChanged)

        self.connectAPIButton.connect("clicked(bool)", self.onConnectAPIPushed)

        self.groupSelector.connect("currentIndexChanged(QString)", self.onGroupSelected)

        self.projectSelector.connect(
            "currentIndexChanged(QString)", self.onProjectSelected
        )

        self.sessionSelector.connect(
            "currentIndexChanged(QString)", self.onSessionSelected
        )
        self.analysisSelector.connect(
            "currentIndexChanged(QString)", self.onAnalysisSelected
        )

        self.analysisFilesSelector.connect(
            "currentIndexChanged(QString)", self.onAnalysisFileSelect
        )

        self.analysisFileButton.connect("clicked(bool)", self.onAnalysisFilePushed)

        self.acquisitionSelector.connect(
            "currentIndexChanged(QString)", self.onAcquisitionSelected
        )

        self.acquisitionFilesSelector.connect(
            "currentIndexChanged(QString)", self.onAcquisitionFileSelected
        )

        self.acquisitionFileButton.connect(
            "clicked(bool)", self.onAcquisitionFilePushed
        )

        self.segmentationSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onSegmentationsChanged
        )

        self.segmentationButton.connect("clicked(bool)", self.ExportSegmentation)

        self.onSegmentationsChanged()
        # Add vertical spacer
        self.layout.addStretch(1)

    def onApiKeyTextChanged(self, item):
        self.connectAPIButton.enabled = True

    def onConnectAPIPushed(self):
        try:
            # Instantiate and connect widgets ...
            if self.apiKeyTextBox.text:
                self.fw_client = flywheel.Client(self.apiKeyTextBox.text)
            else:
                self.fw_client = flywheel.Client()
            fw_user = self.fw_client.get_current_user()["email"]
            fw_site = self.fw_client.get_config()["site"]["api_url"]
            self.logAlertTextLabel.setText(
                f"You are logged in as {fw_user} to {fw_site}"
            )
            # if client valid: TODO
            groups = self.fw_client.groups()
            self.groupSelector.enabled = True
            self.groupSelector.clear()
            for group in groups:
                self.groupSelector.addItem(group.label, group.id)
        except Exception as e:
            self.groupSelector.clear()
            self.groupSelector.enabled = False
            self.apiKeyTextBox.clear()
            self.projectSelector.clear()
            self.projectSelector.enabled = False
            self.sessionSelector.clear()
            self.sessionSelector.enabled = False
            self.acquisitionSelector.clear()
            self.acquisitionSelector.enabled = False
            self.acquisitionFileButton.enabled = False
            self.segmentationButton.enabled = False
            slicer.util.errorDisplay(e)

    def onGroupSelected(self, item):
        if item:
            group_id = self.groupSelector.currentData
            self.group = self.fw_client.get(group_id)
            projects = self.group.projects()
            self.projectSelector.enabled = len(projects) > 0
            self.projectSelector.clear()
            for project in projects:
                self.projectSelector.addItem(project.label, project.id)

    def onProjectSelected(self, item):
        if item:
            project_id = self.projectSelector.currentData
            self.project = self.fw_client.get(project_id)
            sessions = self.project.sessions()
            self.sessionSelector.enabled = len(sessions) > 0
            self.sessionSelector.clear()
            for session in sessions:
                self.sessionSelector.addItem(session.label, session.id)
        else:
            self.sessionSelector.enabled = False
            self.sessionSelector.clear()
            self.analysisSelector.enabled = False
            self.analysisSelector.clear()
            self.analysisFilesSelector.enabled = False
            self.analysisFilesSelector.clear()
            self.analysisFileButton.enabled = False
            self.acquisitionSelector.enabled = False
            self.acquisitionSelector.clear()
            self.acquisitionFilesSelector.enabled = False
            self.acquisitionFilesSelector.clear()
            self.acquisitionFileButton.enabled = False
            self.segmentationButton.enabled = False

    def onSessionSelected(self, item):
        if item:
            session_id = self.sessionSelector.currentData
            self.session = self.fw_client.get(session_id)
            self.session = self.session.reload()

            sessionAnalyses = self.session.analyses
            self.analysisSelector.enabled = len(sessionAnalyses) > 0
            self.analysisSelector.clear()
            self.analysisFilesSelector.enabled = False
            self.analysisFilesSelector.clear()
            for analysis in sessionAnalyses:
                self.analysisSelector.addItem(analysis.label, analysis.id)

            acquisitions = self.session.acquisitions()
            self.acquisitionSelector.enabled = len(acquisitions) > 0
            self.acquisitionSelector.clear()
            for acquisition in acquisitions:
                self.acquisitionSelector.addItem(acquisition.label, acquisition.id)
        else:
            self.analysisSelector.enabled = False
            self.analysisSelector.clear()
            self.analysisFileButton.enabled = False
            self.analysisFilesSelector.enabled = False
            self.analysisFilesSelector.clear()
            self.acquisitionSelector.enabled = False
            self.acquisitionSelector.clear()
            self.acquisitionFilesSelector.enabled = False
            self.acquisitionFilesSelector.clear()
            self.acquisitionFileButton.enabled = False
            self.segmentationButton.enabled = False

    def onAnalysisSelected(self, item):
        if item:
            analysis_id = self.analysisSelector.currentData
            self.sessionAnalysis = self.fw_client.get(analysis_id).reload()
            files = self.sessionAnalysis["files"]
            self.analysisFilesSelector.enabled = len(files) > 0
            self.analysisFilesSelector.clear()
            self.analysisFileButton.enabled = len(files) > 0
            for fl in files:
                self.analysisFilesSelector.addItem(fl.name, fl.id)

    def onAnalysisFileSelect(self, item):
        if item:
            self.analysis_file = self.sessionAnalysis["files"][
                self.analysisFilesSelector.currentIndex
            ]

    def onAnalysisFilePushed(self):
        # Create the save Path:
        ana_file_dir = os.path.join(
            self.CacheDir,
            self.group.id,
            self.project.id,
            self.session.id,
            self.sessionAnalysis.id,
            self.analysis_file.id,
        )
        # TODO: fw sdk methods the "resolver" to browse hierarchy?
        try:
            if not self.useCacheCheckBox.checkState():
                shutil.rmtree(self.CacheDir)
            if not os.path.exists(ana_file_dir):
                os.makedirs(ana_file_dir)
        except Exception as e:
            slicer.util.errorDisplay(e)

        filename = self.analysis_file.name
        filepath = os.path.join(ana_file_dir, filename)
        # TODO: accomodate dicoms.....
        if not os.path.exists(filepath) and ("nii.gz" in filename):
            self.sessionAnalysis.download_file(filename, filepath)
            slicer.util.loadVolume(filepath)
        elif "nii.gz" in filename:
            slicer.util.loadVolume(filepath)

    def onAcquisitionSelected(self, item):
        if self.acquisitionSelector.currentIndex >= 0:
            self.acquisition = self.session.acquisitions()[
                self.acquisitionSelector.currentIndex
            ].reload()
            files = self.acquisition.files
            self.acquisitionFilesSelector.enabled = len(files) > 0
            self.acquisitionFilesSelector.clear()
            self.acquisitionFileButton.enabled = len(files) > 0
            for fl in files:
                self.acquisitionFilesSelector.addItem(fl.name, fl.id)

    def onAcquisitionFileSelected(self, item):
        self.acquisition_file = self.acquisition.files[
            self.acquisitionFilesSelector.currentIndex
        ]

    def onAcquisitionFilePushed(self):
        # Create the save Path:
        acq_file_dir = os.path.join(
            self.CacheDir,
            self.group.id,
            self.project.id,
            self.session.id,
            self.acquisition.id,
            self.acquisition_file.id,
        )
        # TODO: fw sdk methods the "resolver" to browse hierarchy?
        try:
            if not self.useCacheCheckBox.checkState():
                shutil.rmtree(self.CacheDir)
            if not os.path.exists(acq_file_dir):
                os.makedirs(acq_file_dir)
        except Exception as e:
            slicer.util.errorDisplay(e)
        filename = self.acquisition_file.name
        filepath = os.path.join(acq_file_dir, filename)
        # TODO: accomodate dicoms.....
        if not os.path.exists(filepath) and ("nii.gz" in filename):
            self.acquisition.download_file(filename, filepath)
            slicer.util.loadVolume(filepath)
        elif "nii.gz" in filename:
            slicer.util.loadVolume(filepath)

    def onSegmentationsChanged(self):
        if isinstance(
            self.segmentationSelector.currentNode(), slicer.vtkMRMLSegmentationNode
        ) and (self.acquisitionSelector.currentIndex >= 0):
            self.segmentationButton.enabled = True
        else:
            self.segmentationButton.enabled = False

    def ExportSegmentation(self):
        # gather references nodes
        segmentationNode = self.segmentationSelector.currentNode()
        referenceVolumeNode = segmentationNode.GetNodeReference(
            segmentationNode.GetReferenceImageGeometryReferenceRole()
        )
        labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLLabelMapVolumeNode"
        )

        # convert segmentation to label map
        slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(
            segmentationNode, labelmapVolumeNode, referenceVolumeNode
        )

        # Create filename and save.
        orig_file = referenceVolumeNode.GetStorageNode().GetFileName()
        filename = (
            referenceVolumeNode.GetStorageNode()
            .GetFileName()
            .replace(".nii.gz", "_seg.nii.gz")
        )
        myStorageNode = labelmapVolumeNode.CreateDefaultStorageNode()
        myStorageNode.SetFileName(filename)
        myStorageNode.WriteData(labelmapVolumeNode)

        # How to save to flywheel?
        # This acquisition save does not work....
        # self.acquisition.update_file(filename)
        # gives "needs dictionary or kwargs"
        # when given these, it gives APIException()

        # What about Analysis object?
        file_ref = self.acquisition.get_file(op.basename(orig_file)).ref()
        anal = self.session.add_analysis(
            label="3D Slicer Segmentation", inputs=[file_ref]
        )
        anal.upload_output(filename)

    def cleanup(self):
        pass


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

    def hasImageData(self, volumeNode):
        """This is an example logic method that
        returns true if the passed in volume
        node has valid image data
        """
        if not volumeNode:
            logging.debug("hasImageData failed: no volume node")
            return False
        if volumeNode.GetImageData() is None:
            logging.debug("hasImageData failed: no image data in volume node")
            return False
        return True

    def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
        """Validates if the output is not the same as input
        """
        if not inputVolumeNode:
            logging.debug("isValidInputOutputData failed: no input volume node defined")
            return False
        if not outputVolumeNode:
            logging.debug(
                "isValidInputOutputData failed: no output volume node defined"
            )
            return False
        if inputVolumeNode.GetID() == outputVolumeNode.GetID():
            logging.debug(
                "isValidInputOutputData failed: input and output volume is the same. "
                "Create a new volume for output to avoid this error."
            )
            return False
        return True

    def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
        """
        Run the actual algorithm
        """

        if not self.isValidInputOutputData(inputVolume, outputVolume):
            slicer.util.errorDisplay(
                "Input volume is the same as output volume. "
                "Choose a different output volume."
            )
            return False

        logging.info("Processing started")

        # Compute the thresholded output volume using the Threshold Scalar Volume
        # CLI module
        cliParams = {
            "InputVolume": inputVolume.GetID(),
            "OutputVolume": outputVolume.GetID(),
            "ThresholdValue": imageThreshold,
            "ThresholdType": "Above",
        }
        cliNode = slicer.cli.run(
            slicer.modules.thresholdscalarvolume,
            None,
            cliParams,
            wait_for_completion=True,
        )

        # Capture screenshot
        if enableScreenshots:
            self.takeScreenshot("flywheel_connectTest-Start", "MyScreenshot", -1)

        logging.info("Processing completed")

        return True


class flywheel_connectTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ 
        Do whatever is needed to reset the state - 
        typically a scene clear will be enough.
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
            nodeNames="FA",
            fileNames="FA.nrrd",
            uris="http://slicer.kitware.com/midas3/download?items=5767",
        )
        self.delayDisplay("Finished with download and loading")

        volumeNode = slicer.util.getNode(pattern="FA")
        logic = flywheel_connectLogic()
        self.assertIsNotNone(logic.hasImageData(volumeNode))
        self.delayDisplay("Test passed!")

