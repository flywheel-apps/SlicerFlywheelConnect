import datetime
import logging
import os
import os.path as op
import shutil
import tempfile
from glob import glob
from importlib import import_module
from pathlib import Path
from zipfile import ZipFile

import ctk
import DICOMLib
import qt
import slicer
import vtk
from slicer.ScriptedLoadableModule import *

from management.tree_management import TreeManagement

#
# flywheel_connect
#


class flywheel_connect(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        # TODO make this more human readable by adding spaces
        self.parent.title = "Flywheel Connect"
        self.parent.categories = ["Flywheel"]
        self.parent.dependencies = []
        self.parent.contributors = ["Joshua Jacobs (flywheel.io)"]
        self.parent.helpText = 'See <a href="https://github.com/flywheel-apps/SlicerFlywheelConnect">Flywheel Connect website</a> for more information.'
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = ""

        slicer.app.connect("startupCompleted()", self.onStartupCompleted)

    def onStartupCompleted(self):
        FlyW = ""
        try:
            FlyW = import_module("flywheel")
        except ModuleNotFoundError as e:
            if slicer.util.confirmOkCancelDisplay(
                "Flywheel Connect requires 'flywheel-sdk' Python package. Click OK to install it now."
            ):
                slicer.util.pip_install("flywheel-sdk")
                FlyW = import_module("flywheel")
        globals()["flywheel"] = FlyW


#
# flywheel_connectWidget
#


class flywheel_connectWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        """
        Initialize all form elements
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Declare Cache path
        self.CacheDir = Path(os.path.expanduser("~")) / "flywheelIO"

        # #################Declare form elements#######################

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

        # Data View Section
        self.dataCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
        self.dataCollapsibleGroupBox.setTitle("Data")
        self.layout.addWidget(self.dataCollapsibleGroupBox)

        dataFormLayout = qt.QFormLayout(self.dataCollapsibleGroupBox)

        #
        # group Selector ComboBox
        #
        self.groupSelectorLabel = qt.QLabel("Current group:")
        dataFormLayout.addWidget(self.groupSelectorLabel)

        # Selector ComboBox
        self.groupSelector = qt.QComboBox()
        self.groupSelector.enabled = False
        self.groupSelector.setMinimumWidth(200)
        dataFormLayout.addWidget(self.groupSelector)

        #
        # project Selector ComboBox
        #
        self.projectSelectorLabel = qt.QLabel("Current project:")
        dataFormLayout.addWidget(self.projectSelectorLabel)

        # Selector ComboBox
        self.projectSelector = qt.QComboBox()
        self.projectSelector.enabled = False
        self.projectSelector.setMinimumWidth(200)
        dataFormLayout.addWidget(self.projectSelector)

        # TreeView for Single Projects containers:
        self.treeView = qt.QTreeView()

        self.treeView.enabled = False
        self.treeView.setMinimumWidth(200)
        self.treeView.setMinimumHeight(350)
        self.tree_management = TreeManagement(self)
        dataFormLayout.addWidget(self.treeView)

        # Load Files Button
        self.loadFilesButton = qt.QPushButton("Load Selected Files")
        self.loadFilesButton.enabled = False
        dataFormLayout.addWidget(self.loadFilesButton)

        # Upload to Flywheel Button
        self.uploadFilesButton = qt.QPushButton(
            "Upload to Flywheel\nas Container Files"
        )
        self.uploadFilesButton.enabled = False
        dataFormLayout.addWidget(self.uploadFilesButton)

        # As Analysis Checkbox
        self.asAnalysisCheck = qt.QCheckBox("As Analysis")
        self.asAnalysisCheck.toolTip = (
            "Upload Files to Flywheel as an Analysis Container."
        )
        self.asAnalysisCheck.enabled = False

        dataFormLayout.addWidget(self.asAnalysisCheck)

        # ################# Connect form elements #######################
        self.connectAPIButton.connect("clicked(bool)", self.onConnectAPIPushed)

        self.groupSelector.connect("currentIndexChanged(QString)", self.onGroupSelected)

        self.projectSelector.connect(
            "currentIndexChanged(QString)", self.onProjectSelected
        )

        self.loadFilesButton.connect("clicked(bool)", self.onLoadFilesPushed)

        self.uploadFilesButton.connect("clicked(bool)", self.save_scene_to_flywheel)

        self.asAnalysisCheck.stateChanged.connect(self.onAnalysisCheckChanged)

        # Add vertical spacer
        self.layout.addStretch(1)

    def onConnectAPIPushed(self):
        """
        Connect to a Flywheel instance for valid api-key.
        """
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

            # Clear out any other instance's data from Slicer before proceeding.
            slicer.mrmlScene.Clear(0)
        except Exception as e:
            self.groupSelector.clear()
            self.groupSelector.enabled = False
            self.apiKeyTextBox.clear()
            self.projectSelector.clear()
            self.projectSelector.enabled = False
            slicer.util.errorDisplay(e)

    def onGroupSelected(self, item):
        """
        On selected Group from dropdown, update casecade

        Args:
            item (str): Group name or empty string
        """
        if item:
            group_id = self.groupSelector.currentData
            self.group = self.fw_client.get(group_id)
            projects = self.group.projects()
            self.projectSelector.enabled = len(projects) > 0
            self.projectSelector.clear()
            for project in projects:
                self.projectSelector.addItem(project.label, project.id)

    def onProjectSelected(self, item):
        """
        On selected project from dropdown, update the tree

        Args:
            item (str): Name of project or empty string
        """
        tree_rows = self.tree_management.source_model.rowCount()
        if item:
            project_id = self.projectSelector.currentData
            self.project = self.fw_client.get(project_id)

            # Remove the rows from the tree and repopulate
            if tree_rows > 0:
                self.tree_management.source_model.removeRows(0, tree_rows)
            self.tree_management.populateTreeFromProject(self.project)
            self.treeView.enabled = True
        else:
            self.treeView.enabled = False
            # Remove the rows from the tree and don't repopulate
            if tree_rows > 0:
                self.tree_management.source_model.removeRows(0, tree_rows)
            self.loadFilesButton.enabled = False

    def is_compressed_dicom(self, file_path, file_type):
        """
        Check file_path and file_type for a flywheel compressed dicom archive.

        Args:
            file_path (str): Path to cached file
            file_type (str): Type of Flywheel file

        Returns:
            boolean: True for supported compressed dicom type
        """
        if file_path.endswith(".zip") and file_type == "dicom":
            return True

        return False

    def load_dicom_archive(self, file_path):
        """
        Load unzipped DICOMs into Slicer.

        Args:
            file_path (str): path to the cached dicom archive.

        https://discourse.slicer.org/t/fastest-way-to-load-dicom/9317/2
        """
        with tempfile.TemporaryDirectory() as dicomDataDir:
            dicom_zip = ZipFile(file_path)
            dicom_zip.extractall(path=dicomDataDir)
            DICOMLib.importDicom(dicomDataDir)
            dicomFiles = slicer.util.getFilesInDirectory(dicomDataDir)
            loadablesByPlugin, loadEnabled = DICOMLib.getLoadablesFromFileLists(
                [dicomFiles]
            )
            loadedNodeIDs = DICOMLib.loadLoadables(loadablesByPlugin)

    def onLoadFilesPushed(self):
        """
        Load tree-selected files into 3D Slicer for viewing.
        """

        # If Cache not checked, delete CacheDir recursively
        if not self.useCacheCheckBox.checkState():
            shutil.rmtree(self.CacheDir)
            Path(self.CacheDir).mkdir(parents=True, exist_ok=True)

        # Cache all selected files
        self.tree_management.cache_selected_for_open()

        # Walk through cached files... This could use "types"
        for k, file_dict in self.tree_management.cache_files.items():
            file_path = file_dict["file_path"]
            file_type = file_dict["file_type"]
            # Check for Flywheel compressed dicom
            if self.is_compressed_dicom(file_path, file_type):
                try:
                    self.load_dicom_archive(file_path)
                    continue
                except Exception as e:
                    print("Not a valid DICOM archive.")
            # Load using Slicer default node reader
            if not slicer.app.ioManager().loadFile(file_path):
                print("Failed to read file: " + file_path)

    def save_analysis(self, parent_container_item, output_path):
        """
        Save selected files to a new analysis container under a parent container.

        Args:
            parent_container_item (ContainerItem): Tree Item representation of parent
                container.
            output_path (Path): Temporary path to where Slicer files are saved.
        """
        parent_container = self.fw_client.get(parent_container_item.data())

        # Get all cached paths represented in Slicer
        input_files_paths = [
            Path(node.GetFileName())
            for node in slicer.util.getNodesByClass("vtkMRMLStorageNode")
            if self.CacheDir in node.GetFileName()
        ]

        # Represent those files as file reference from their respective parents
        input_files = [
            self.fw_client.get(str(input_path.parents[1]).split("/")[-1])
            .get_file(input_path.name)
            .ref()
            for input_path in input_files_paths
        ]

        # Generic name... could be improved.
        analysis_name = "3D Slicer " + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Create analysis container
        analysis = parent_container.add_analysis(
            label=analysis_name, inputs=input_files
        )

        # Get all files from temp directory
        outputs = [
            file_path
            for file_path in glob(str(output_path / "*"))
            if Path(file_path).is_file()
        ]

        # Finalize analysis
        analysis.upload_file(outputs)

    def save_files_to_container(self, parent_container_item, output_path):
        """
        Save selected files to a parent Flywheel container.

        Files that already exist in the container are ignored.

        TODO: Update the file version

        Args:
            parent_container_item (ContainerItem):  Tree Item representation of parent
                container.
            output_path (Path): Temporary path to where Slicer files are saved.
        """
        parent_container = self.fw_client.get(parent_container_item.data()).reload()
        parent_container_files = [fl.name for fl in parent_container.files]
        for output_file in [
            file_path
            for file_path in glob(str(output_path / "*"))
            if (
                Path(file_path).is_file()
                and Path(file_path).name not in parent_container_files
            )
        ]:
            parent_container.upload_file(output_file)

    def save_scene_to_flywheel(self):
        """
        Save selected files in the current Slicer scene to a Flywheel Analysis or
        Container.
        """
        with tempfile.TemporaryDirectory() as tmp_output_path:
            output_path = Path(tmp_output_path)
            slicer.mrmlScene.SetRootDirectory(str(output_path))
            slicer.mrmlScene.SetURL(str(output_path / "Slicer_Scene.mrml"))
            if slicer.util.openSaveDataDialog():
                index = self.treeView.selectedIndexes()[0]
                container_item = self.tree_management.source_model.itemFromIndex(index)
                save_as_analysis = self.asAnalysisCheck.isChecked()
                if save_as_analysis:
                    self.save_analysis(container_item, output_path)
                else:
                    self.save_files_to_container(container_item, output_path)

            # Remove storage nodes with the tmp_output_path in them
            for node in [
                node
                for node in slicer.util.getNodesByClass("vtkMRMLStorageNode")
                if tmp_output_path in node.GetFileName()
            ]:
                slicer.mrmlScene.RemoveNode(node)

    def onAnalysisCheckChanged(self, item):
        """
        Update the text on the "Upload" button depending on item state

        Args:
            item (ItemData): Data from item... not used.
        """
        if self.asAnalysisCheck.isChecked():
            text = "Upload to Flywheel\nas Analysis"
        else:
            text = "Upload to Flywheel\nas Container Files"
        self.uploadFilesButton.setText(text)

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
        """Validates if the output is not the same as input"""
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
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_flywheel_connect1()

    def test_flywheel_connect1(self):
        """Ideally you should have several levels of tests.  At the lowest level
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
