# Common paired file types
PAIRED_FILE_TYPES = {"mhd": "raw", "hdr": "img"}

# TODO: test all major volume and surface file types.
#       Ensure tests pass for these types.
#       Other files will be thoroughly tested on customer request for those file types.
# https://www.slicer.org/wiki/Documentation/4.8/SlicerApplication/SupportedDataFormat
# https://slicer.readthedocs.io/en/latest/user_guide/data_loading_and_saving.html#supported-data-formats
SLICER_DATA_FORMATS = {
    "volumes": [
        ".dcm",  # DICOM
        ".nrrd",  # NRRD
        ".nhdr",  # NRRD
        ".mhd",  # MetaImage
        ".mha",  # MetaImage
        ".vtk",  # vtkVolume
        ".hdr",  # Analyze
        ".img",  # Analyze
        ".img.gz",  # Analyze
        ".nia,",  # NIfTI
        ".nii",  # NIfTI
        ".nii.gz",  # NIfTI
        ".bmp",
        ".pic",
        ".mask",
        ".gipl",
        ".gipl.gz",
        ".jpg",
        ".jpeg",
        ".lsm",
        ".png",
        ".spr",
        ".tif",
        ".tiff",
        ".mgz",
        ".mrc",
        ".rec",
    ],
    "models": [
        ".vtk",  # vtkPolyData
        ".vtp",  # vtkPolyData
        ".stl",  # StereoLithography
        ".obj",  # Wavefront
        ".orig",  # FreeSurfer
        ".inflated",  # FreeSurfer
        ".sphere",  # FreeSurfer
        ".white",  # FreeSurfer
        ".smoothwm",  # FreeSurfer
        ".pial",  # FreeSurfer
        ".g",
        ".byu",
    ],
    "fiducials": [".fcsv", ".mrk.json", ".json"],
    "rulers": [".acsv"],
    "transforms": [
        ".h5",  # ITK Transforms
        ".tfm",  # ITK Transforms
        ".mat",  # Matlab Transforms
        ".nrrd",  # Displacement Field
        ".nhdr",  # Displacement Field
        ".mha",  # Displacement Field
        ".mhd",  # Displacement Field
        ".nii",  # Displacement Field
        ".nii.gz",  # Displacement Field
    ],
    "transfer_functions": [".vp"],
    "lookup_tables": [".ctbl"],
    "double_arrays": [".mcsv"],
}
