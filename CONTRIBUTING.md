## Development Notes
flywheel-connect is built in the [3D Slicer Extension Framework](https://www.slicer.org/wiki/Documentation/Nightly/Developers/Tutorials/Extension) leveraging the [flywheel python SDK](https://flywheel-io.github.io/core/branches/master/python/). It currently allows an authenticated user to browse through a simple container hierarchy (Groups->Projects->Sessions->Acquisitions) and retrieve nifti files from a selected acquisition to display in 3D Slicer. Future iterations of this extension are intended to 
1. Access files, information, and analyses at all levels of the Project->...->Acquisition hierarchy.
2. Allow uploading of a 3D Slicer "Medical Record Bundle" (.mrb zipped file) to a flywheel instance as an analysis object.
3. Download a Medical Record Bundle from flywheel and reinstantiate in 3D Slicer with all dependencies.

For developing with 3D Slicer, these 3D Slicer extensions (available through the "Extensions Manager") are highly recommended:

* [DeveloperToolsForExtensions](https://www.slicer.org/w/index.php/Documentation/Nightly/Extensions/DeveloperToolsForExtensions)
* [DebuggingTools](https://www.slicer.org/w/index.php/Documentation/Nightly/Extensions/DebuggingTools)

Furthermore, the [3D Slicer discourse community](https://discourse.slicer.org/) has been an invaluable resource.
