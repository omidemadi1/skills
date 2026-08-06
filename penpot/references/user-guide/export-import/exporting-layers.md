# Exporting layers

In Penpot you can setup export presets for different file formats and scales.

## How to export

You can set up different export configurations to suit your needs. Each export configuration is called "export preset".

### Create export preset

To export a layer you need to select it and at the Design panel add an export preset pressing the “+” button of the Export section.

Export presets can be also found at the **[View mode](/user-guide/first-steps/the-interface/#interface-viewmode)** with the code tab activated.

You can set as many export presets as you need for the same layer. Set multiple exports to get the same layer in different scales and/or formats with just one click.

### Remove export preset

To **remove an export preset** you have to select the layer and then press the “-” button at the export preset you want to remove.

## Export options

The options of an export:

- **Size** - Options for the most common sizing scales.
- **Suffix** - Especially useful if you are exporting at different scales.
- **File format** - PNG, JPEG, WEBP, SVG, PDF.

## Exporting multiple elements

### Make your export selection.

To export multiple elements you first have to select the elements you'd like to export. If the selected elements already have export settings those will be included in the export. You can also add new export settings for multiselections.

You can also launch the export for a page from the main menu or using the shortcut `Ctrl` + `Shift` + `E`. This option will include in the export all the export pressets set among a selection or in the page if nothing is selected.

### Configure your export selection.

Before confirming your export for multiple elements you will have the option to check their names, sizes and formats and a last chance to deselect the export settings you don't want to go on this batch.

### Check the export progress.

A popup will show the exporting progress and will show errors if any.

## Export boards to PDF

If you have a presentation made at Penpot you might want to create a document that can be shared with anyone, regardless of having a Penpot account, or just to be able to use your presentation offline (essential for talks and classes). You can easily export all the artboards of a page to a single PDF file from the file menu.

[Technical note](#export-technical) about the PDF format.

## Technical notes about exports

Exported PDF files try to leverage the capabilities of PDF vectorial format (unpixelated zoom, select & copy texts, etc.), but cannot guarantee that 100% of SVG features will be converted perfectly to PDF. You may see differences between a layer displayed inside Penpot and in the exported file. If you need an exact match, a workaround is to export the layer into PNG and convert it to PDF with some of the many tools that exist for it.

**Currently known issue:**
When exporting layers with masks, the mask does not work when opening the PDF file with some open source tools (e.g. evince or inkscape). This is not Penpot's fault, but [a bug in poppler](https://gitlab.freedesktop.org/poppler/poppler/-/issues/1210), a library used by many of the open source tools. If you open the file with an official Adobe viewer, or a tool like okular, or in a browser like Chrome or Firefox, you can see it properly.
