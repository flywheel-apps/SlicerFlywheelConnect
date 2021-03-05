from PythonQt import QtGui
from PythonQt.QtCore import Qt
from qt import QAbstractItemView, QItemSelectionModel, QMenu

from .fw_container_items import (
    AnalysisFolderItem,
    ContainerItem,
    FileItem,
    GroupItem,
    ProjectItem,
)


class TreeManagement:
    """
    Class that coordinates all tree-related functionality.
    """

    def __init__(self, main_window):
        """
        Initialize treeView object from Main Window.

        Args:
            main_window (QtWidgets.QMainWindow): [description]
        """
        self.main_window = main_window
        self.treeView = self.main_window.treeView
        self.cache_files = {}
        tree = self.treeView
        #https://doc.qt.io/archives/qt-4.8/qabstractitemview.html
        tree.selectionMode = QAbstractItemView.ExtendedSelection
        tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tree.clicked.connect(self.tree_clicked)
        tree.doubleClicked.connect(self.tree_dblclicked)
        tree.expanded.connect(self.on_expanded)

        tree.setContextMenuPolicy(Qt.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.open_menu)
        self.source_model = QtGui.QStandardItemModel()
        tree.setModel(self.source_model)
        self.selection_model = QItemSelectionModel(self.source_model)
        tree.setSelectionModel(self.selection_model)
        tree.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def tree_clicked(self, index):
        """
        Cascade the tree clicked event to relevant tree node items.

        Args:
            index (QtCore.QModelIndex): Index of tree item clicked.
        """
        item = self.get_id(index)

    def tree_dblclicked(self, index):
        """
        Cascade the double clicked signal to the tree node double clicked.

        Args:
            index (QtCore.QModelIndex): Index of tree node double clicked.
        """
        item = self.get_id(index)
        if isinstance(item, AnalysisFolderItem):
            item._dblclicked()

    def populateTree(self):
        """
        Populate the tree starting with groups
        """
        groups = self.main_window.fw_client.groups()
        for group in groups:
            group_item = GroupItem(self.source_model, group)

    def populateTreeFromProject(self, project):
        """
        Populate Tree from a single Project
        """
        project_item = ProjectItem(self.source_model, project)

    def get_id(self, index):
        """
        Retrieve the tree item from the selected index.

        Args:
            index (QtCore.QModelIndex): Index from selected tree node.

        Returns:
            QtGui.QStandardItem: Returns the item with designated index.
        """
        item = self.source_model.itemFromIndex(index)
        id = item.data()
        # I will want to move this to "clicked" or "on select"
        # self.ui.txtID.setText(id)
        return item

    def open_menu(self, position):
        """
        Function to manage context menus.

        Args:
            position (QtCore.QPoint): Position right-clicked and where menu rendered.
        """
        indexes = self.treeView.selectedIndexes()
        if len(indexes) > 0:
            hasFile = False
            for index in indexes:
                item = self.source_model.itemFromIndex(index)
                if isinstance(item, FileItem):
                    hasFile = True

            menu = QMenu()
            if hasFile:
                action = menu.addAction("Cache Selected Files")
                action.triggered.connect(self._cache_selected)
            menu.exec_(self.treeView.viewport().mapToGlobal(position))

    def on_selection_changed(self):
        """
        Enable or disable load and upload buttons based on selected tree items.

        If a FileItem is selected, the load button is enabled.
        Else if a ContainerItem (e.g. Project, Session,...) is selected, upload is
        is enabled.
        """        
        indexes = self.treeView.selectedIndexes()
        has_file = False
        containers_selected = 0
        if len(indexes) > 0:
            for index in indexes:
                item = self.source_model.itemFromIndex(index)
                if isinstance(item, FileItem):
                    has_file = True
                elif isinstance(item, ContainerItem):
                    containers_selected += 1
        else:
            has_file = False

        self.main_window.loadFilesButton.enabled = has_file
        upload_enabled = containers_selected == 1
        self.main_window.uploadFilesButton.enabled = upload_enabled
        self.main_window.asAnalysisCheck.enabled = upload_enabled

    def _cache_selected(self):
        """
        Cache selected files to local directory,
        """
        # TODO: Acknowledge this is for files only or change for all files of selected
        #       Acquisitions.
        indexes = self.treeView.selectedIndexes()
        if len(indexes) > 0:
            for index in indexes:
                item = self.source_model.itemFromIndex(index)
                if isinstance(item, FileItem):
                    item._add_to_cache()

    def on_expanded(self, index):
        """
        Triggered on the expansion of any tree node.

        Used to populate subtree on expanding only.  This significantly speeds up the
        population of the tree.

        Args:
            index (QtCore.QModelIndex): Index of expanded tree node.
        """
        item = self.source_model.itemFromIndex(index)
        if hasattr(item, "_on_expand"):
            item._on_expand()

    def cache_selected_for_open(self):
        """
        Cache selected files if necessary for opening in application.
        """
        tree = self.treeView
        self.cache_files.clear()
        for index in tree.selectedIndexes():
            file_path = self.main_window.CacheDir
            item = self.source_model.itemFromIndex(index)
            if isinstance(item, FileItem):
                file_path, file_type = item._add_to_cache()

                self.cache_files[item.container.id] = {
                    "file_path": str(file_path),
                    "file_type": file_type
                }
