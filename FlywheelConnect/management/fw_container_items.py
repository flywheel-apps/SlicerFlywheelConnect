import os
from pathlib import Path

from PythonQt import QtGui
from PythonQt.QtCore import Qt
from qt import QAbstractItemView


class FolderItem(QtGui.QStandardItem):
    """
    Folder Items are for the convenience of collapsing long lists into a tree node.
    """

    def __init__(self, parent_item, folder_name):
        """
        Initialize Folder Items unpopulated.

        Args:
            parent_item (ContainerItem): Container Item parent for Folder Item.
            folder_name (str): A name for the folder item (e.g. SESSIONS).
        """
        super(FolderItem, self).__init__()
        self.source_dir = parent_item.source_dir
        icon_path = "Resources/Icons/folder.png"
        icon = QtGui.QIcon(str(self.source_dir / icon_path))
        self.parent_item = parent_item
        self.parent_container = parent_item.container
        self.folderItem = QtGui.QStandardItem()
        self.setText(folder_name)
        self.setIcon(icon)
        parent_item.appendRow(self)


class AnalysisFolderItem(FolderItem):
    """
    Folder Item specifically for analyses.
    """

    def __init__(self, parent_item):
        """
        Initialize AnalysisFolderItem unpopulated.

        Args:
            parent_item (ContainerItem): Container that hosts analyses
                (projects, subjects, sessions, acquisitions)
        """
        folder_name = "ANALYSES"
        super(AnalysisFolderItem, self).__init__(parent_item, folder_name)
        # TODO: put folder w/ download icon
        icon_path = "Resources/Icons/dwnld-folder.png"
        icon = QtGui.QIcon(str(self.source_dir / icon_path))
        self.setIcon(icon)
        # TODO: ensure that these work.
        self.setToolTip("Double-Click to list Analyses.")

    def _dblclicked(self):
        if hasattr(self.parent_container, "analyses"):
            self.parent_container = self.parent_container.reload()
            icon_path = "Resources/Icons/folder.png"
            icon = QtGui.QIcon(str(self.source_dir / icon_path))
            self.setIcon(icon)
            if not self.hasChildren() and self.parent_container.analyses:

                for analysis in self.parent_container.analyses:
                    AnalysisItem(self, analysis)


class ContainerItem(QtGui.QStandardItem):
    """
    TreeView node to host all common functionality for Flywheel containers.
    """

    def __init__(self, parent_item, container):
        """
        Initialize new container item with its parent and flywheel container object.

        Args:
            parent_item (QtGui.QStandardItem): Parent of this item to instantiate.
            container (flywheel.Container): Flywheel container (e.g. group, project,...)
        """
        super(ContainerItem, self).__init__()
        self.has_analyses = False
        self.parent_item = parent_item
        self.container = container
        self.source_dir = Path(os.path.realpath(__file__)).parents[1]
        title = container.label
        self.setData(container.id)
        self.setText(title)
        self._set_icon()
        self.parent_item.appendRow(self)
        self._files_folder()
        self._analyses_folder()
        self._child_container_folder()

    def _set_icon(self):
        """
        Set the icon for the container item.
        """
        icon = QtGui.QIcon(str(self.source_dir / self.icon_path))
        self.setIcon(icon)

    def _files_folder(self):
        """
        Create a "FILES" folder if self.container has one.
        """
        if hasattr(self.container, "files"):
            self.filesItem = FolderItem(self, "FILES")

    def _list_files(self):
        """
        List all file items of a container object under the "FILES" folder.
        TODO: Make this a part of a filesFolderItem???
        """
        if hasattr(self.container, "files"):
            if not self.filesItem.hasChildren() and self.container.files:
                for fl in self.container.files:
                    FileItem(self.filesItem, fl)

    def _analyses_folder(self):
        """
        Create "ANALYSES" folder, if container has analyses object.
        """
        if hasattr(self.container, "analyses"):
            self.analysesItem = AnalysisFolderItem(self)

    def _child_container_folder(self):
        """
        Create a folder with the name of the child containers (e.g. SESSIONS)
        """
        if hasattr(self, "child_container_name"):
            self.folderItem = FolderItem(self, self.child_container_name)

    def _on_expand(self):
        """
        On expansion of container tree node, list all files.
        """
        # super(ContainerItem, self)._on_expand()
        self._list_files()


class GroupItem(ContainerItem):
    """
    TreeView Node for the functionality of group containers.
    """

    def __init__(self, parent_item, group):
        """
        Initialize Group Item with parent and group container.

        Args:
            parent_item (QtGui.QStandardItemModel): Top-level tree item or model.
            group (flywheel.Group): Flywheel group container to attach as tree node.
        """
        self.icon_path = "Resources/Icons/group.png"
        self.child_container_name = "PROJECTS"
        self.group = group
        super(GroupItem, self).__init__(parent_item, group)

    def _list_projects(self):
        """
        Populate with flywheel projects.
        """
        if not self.folderItem.hasChildren():
            for project in self.group.projects():
                ProjectItem(self.folderItem, project)

    def _on_expand(self):
        """
        On expansion of group tree node, list all projects.
        """
        super(GroupItem, self)._on_expand()
        self._list_projects()


class ProjectItem(ContainerItem):
    """
    TreeView Node for the functionality of Project containers.
    """

    def __init__(self, parent_item, project):
        """
        Initialize Project Item with parent and project container.

        Args:
            parent_item (FolderItem): The folder item tree node that is the parent.
            project (flywheel.Project): Flywheel project container to attach as tree
                node.
        """
        self.icon_path = "Resources/Icons/project.png"
        self.child_container_name = "SUBJECTS"
        super(ProjectItem, self).__init__(parent_item, project)
        self.has_analyses = True
        self.project = self.container

    def _list_subjects(self):
        """
        Populate with flywheel subjects.
        """
        if not self.folderItem.hasChildren():
            for subject in self.project.subjects():
                SubjectItem(self.folderItem, subject)

    def _on_expand(self):
        """
        On expansion of project tree node, list all subjects.
        """
        super(ProjectItem, self)._on_expand()
        self._list_subjects()


class SubjectItem(ContainerItem):
    """
    TreeView Node for the functionality of Subject containers.
    """

    def __init__(self, parent_item, subject):
        """
        Initialize Subject Item with parent and project container.

        Args:
            parent_item (FolderItem): The folder item tree node that is the parent.
            subject (flywheel.Subject): Flywheel subject container to attach as tree
                node.
        """
        self.icon_path = "Resources/Icons/subject.png"
        self.child_container_name = "SESSIONS"
        super(SubjectItem, self).__init__(parent_item, subject)
        self.has_analyses = True
        self.subject = self.container

    def _list_sessions(self):
        """
        Populate with flywheel sessions.
        """
        if not self.folderItem.hasChildren():
            for session in self.subject.sessions():
                SessionItem(self.folderItem, session)

    def _on_expand(self):
        """
        On expansion of subject tree node, list all sessions.
        """
        super(SubjectItem, self)._on_expand()
        self._list_sessions()


class SessionItem(ContainerItem):
    """
    TreeView Node for the functionality of Session containers.
    """

    def __init__(self, parent_item, session):
        """
        Initialize Session Item with parent and subject container.

        Args:
            parent_item (FolderItem): The folder item tree node that is the parent.
            session (flywheel.Session): Flywheel session container to attach as tree
                node.
        """
        self.icon_path = "Resources/Icons/session.png"
        self.child_container_name = "ACQUISITIONS"
        super(SessionItem, self).__init__(parent_item, session)
        self.has_analyses = True
        self.session = self.container

    def _list_acquisitions(self):
        """
        Populate with flywheel acquisitions.
        """
        if not self.folderItem.hasChildren():
            for acquisition in self.session.acquisitions():
                AcquisitionItem(self.folderItem, acquisition)

    def _on_expand(self):
        """
        On expansion of session tree node, list all acquisitions.
        """
        super(SessionItem, self)._on_expand()
        self._list_acquisitions()


class AcquisitionItem(ContainerItem):
    """
    TreeView Node for the functionality of Acquisition containers.
    """

    def __init__(self, parent_item, acquisition):
        """
        Initialize Acquisition Item with parent and Acquisition container.

        Args:
            parent_item (FolderItem): The folder item tree node that is the parent.
            acquisition (flywheel.Acquisition): Flywheel acquisitin container to attach
                as tree node.
        """
        self.icon_path = "Resources/Icons/acquisition.png"
        super(AcquisitionItem, self).__init__(parent_item, acquisition)
        self.has_analyses = True
        self.acquisition = self.container


class AnalysisItem(ContainerItem):
    """
    TreeView Node for the functionality of Analysis objects.
    """

    def __init__(self, parent_item, analysis):
        """
        Initialize Subject Item with parent and analysis object.

        Args:
            parent_item (FolderItem): The folder item tree node that is the parent.
            analysis (flywheel.Analysis): Flywheel analysis object to attach as tree
                node.
        """
        self.icon_path = "Resources/Icons/analysis.png"
        super(AnalysisItem, self).__init__(parent_item, analysis)


class FileItem(ContainerItem):
    """
    TreeView Node for the functionality of File objects.
    """

    def __init__(self, parent_item, file_obj):
        """
        Initialize File Item with parent and file object.

        Args:
            parent_item (FolderItem): The folder item tree node that is the parent.
            file_obj (flywheel.FileEntry): File object of the tree node.
        """
        file_obj.label = file_obj.name
        self.parent_item = parent_item
        self.container = file_obj
        
        self.file = file_obj
        self.file_type = file_obj.type
        if self._is_cached():
            self.icon_path = "Resources/Icons/file_cached.png"
        else:
            self.icon_path = "Resources/Icons/file.png"
        super(FileItem, self).__init__(parent_item, file_obj)
        if self._is_cached():
            self.setToolTip("File is cached.")
        else:
            self.setToolTip("File is not cached")

    def _get_cache_path(self):
        """
        Construct cache path of file (e.g. cache_root/group/.../file_id/file_name).

        Returns:
            pathlib.Path: Cache Path to file indicated.
        """
        file_parent = self.parent_item.parent().container
        file_path = Path(os.path.expanduser("~") + "/flywheelIO/")

        for par in ["group", "project", "subject", "session", "acquisition"]:
            if file_parent.parents[par]:
                file_path /= file_parent.parents[par]
        file_path /= file_parent.id
        file_path /= self.container.id
        file_path /= self.container.name
        return file_path

    def _is_cached(self):
        """
        Check if file is cached.

        Returns:
            bool: If file is cached locally on disk.
        """
        return self._get_cache_path().exists()

    def _add_to_cache(self):
        """
        Add file to cache directory under path.

        Returns:
            pathlib.Path, str: Path to file in cache and flywheel file_type
        """
        file_path = self._get_cache_path()
        file_parent = self.parent_item.parent().container
        if not file_path.exists():
            if not file_path.parents[0].exists():
                os.makedirs(file_path.parents[0])
            file_parent.download_file(self.file.name, str(file_path))
            self.icon_path = "Resources/Icons/file_cached.png"
            self.setToolTip("File is cached.")
            self._set_icon()
        return file_path, self.file_type
