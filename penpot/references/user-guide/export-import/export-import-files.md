# Export and import Penpot files

You can export Penpot files to your computer and import them from your computer to your projects.

## Export Penpot files

Exporting files is useful for many reasons. Sometimes you want to have a backup of your files and sometimes it is useful to share Penpot files with a user that does not belong to one of your teams, or you want to have a backup of your files outside Penpot, both SaaS (design.penpot.app) or at a self-hosted instance.

### How to export Penpot files

#### Export a single file

You can download (export) files from the workspace and from the dashboard.

**From the [dashboard](/user-guide/first-steps/the-interface/#interface-dashboard)**: Select the download option at the file card menu.

**From the [workspace](/user-guide/first-steps/the-interface/#interface-workspace)**: Select the download option at the main menu.

#### Export multiple files

Select multiple files to export them at the same time. An overlay will show you the progress of the different exports.

#### Exporting files linked to Shared libraries

Exported files linked to shared libraries provide different ways to export their assets. Choose the one that suits you better.

- **Export shared libraries**: Files with shared libraries will be included in the export, maintaining their linkage.
- **Include shared library assets in file libraries**: Files will be exported with all external assets merged into the file library.
- **Treat shared library assets as basic layers**: Shared libraries will not be included in the export and no assets will be added to the library.

## Import Penpot files

The maximum file import size is currently limited to 1GB.

The import option is at the projects menu. Press “Import files” and then select one or more .penpot files to import. You can import a .zip file as well.

Right before importing the files to your project, you’ll still have the opportunity to review the items to be imported, have the information about the ones that can not be imported and also the chance to discard files.

## Penpot file format

Penpot export to a unique format that streamline the import and export of files and assets by being more efficient and interoperable.

Unlike other design tools, **Penpot's format is built on standard languages**. The exported file is essentially a ZIP archive containing binary assets (such as bitmap and vector images) alongside a readable JSON structure. By avoiding proprietary formats, Penpot empowers users with autonomy from specific tools while enabling seamless third-party integrations.

### Deprecated Penpot file formats

These formats can only be exported from version 2.3 or earlier versions, but can be imported to any Penpot version.

There are two different deprecated Penpot file formats in which you can import/export Penpot files. A standard one and a binary one. You always have the chance to use both for any file.

#### [Deprecated] Penpot file (.penpot).

The fast one. Binary Penpot specific.

- ✅ Highly efficient in terms of memory and transfer time when exporting and importing.
- ❌ It can be opened only in Penpot.
- ❌ Not transparent, code difficult to explore.

#### [Deprecated] Standard file (.zip).

The open one. A compressed file that includes SVG and JSON.

- ✅ Allows the file to be opened by other softwares (still, for those cases export to SVG seems to be the common practice).
- ✅ Allows some automations and integrations.
- ✅ Is a transparent, existing, open standard format.
- ❌ Highly inefficient in terms of memory and transfer time when exporting and importing (this is because SVG).
