cmake_minimum_required(VERSION 3.5)

project(flywheel_connect)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/flywheel_connect")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Joshua Jacobs (flywheel.io)")
set(EXTENSION_DESCRIPTION "This extension is to allow data exchange between a flywheel instance and 3D Slicer.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/flywheel_connect.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/flywheel_connect/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(flywheel_connect)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
