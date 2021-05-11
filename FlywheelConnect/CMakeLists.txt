#-----------------------------------------------------------------------------
set(MODULE_NAME flywheel_connect)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  management/__init__.py
  management/fw_container_items.py
  management/tree_management.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  Resources/Icons/acquisition.png
  Resources/Icons/analysis.png
  Resources/Icons/app_viewer_screenshot.png
  Resources/Icons/download.png
  Resources/Icons/dwnld-folder.png
  Resources/Icons/file.png
  Resources/Icons/file_cached.png
  Resources/Icons/folder.png
  Resources/Icons/group.png
  Resources/Icons/project.png
  Resources/Icons/session.png
  Resources/Icons/subject.png 
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()
