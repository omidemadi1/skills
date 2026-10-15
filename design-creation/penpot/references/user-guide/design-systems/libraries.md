# Libraries

Libraries may include components, colors and typographies. Learn how to create and manage them to better organize the pieces of your designs and speed your workflow.

### File libraries

Each file has its own file library which is where the assets that belong to this file are stored.

You have two ways to access the file library from the file [workspace](/user-guide/first-steps/the-interface/#interface-workspace):

- Click the assets tab icon at the left sidebar.
- Press `Alt/⌥` + `i`.

### Shared libraries

#### Publish as shared library

You can publish any regular file as a shared library. This means that the file library of this file will be available to be connected to other files that exist in the same team, so its library assets can be reused.

There are two ways to publish a library:

- Using the file main menu.
- From the libraries panel, that you can launch by clicking on the "Libraries" button that is found at the assets tab.

#### Unpublish a shared library

You can unpublish any library anytime the same way you can publish it, both from the file menu and the libraries panel.

Unpublishing a library will disconnect it from the files where it was connected. The assets that have already been used in other files will remain, but no longer linked with the now unpublished library.

#### Library updates

#### Connect shared libraries

To add a Shared Library from another file, launch the libraries panel, then search and select the available libraries. If you see the message "There are no Shared Libraries available", start by [publishing other files as a shared library](/user-guide/design-systems/libraries/#shared-libraries) or add from our [Libraries & templates](https://penpot.app/libraries-templates).

#### Disconnect shared library

You can disconnect any library anytime from the libraries panel just by clicking on the disconnect button.

#### Use shared libraries

Shared libraries will be listed at the assets panel, at the workspace left sidebar. You can expand and collapse them to access the assets of each connected shared library.

#### Open shared library file

Click on the arrow icon at the right of a shared library name to go to the file where the library is and edit its contents.

#### Import tokens from a connected library

If a shared library you have connected includes design tokens, you can copy them into the current file from the **Libraries** modal.

The **Import tokens** button appears only next to connected libraries that define tokens. Libraries without tokens do not show this control.

1. Open the **Libraries** panel from the assets tab.
2. Under **Libraries in this file**, find the connected library that includes tokens and click **Import tokens** (beside the disconnect control).
3. Review the confirmation dialog. Importing brings in the library's full token data, including sets and themes when the library defines them.
4. Click **Import tokens** to apply, or **Cancel** to go back without changes.

Importing tokens from a library replaces all tokens, sets and themes in the current file. Export your tokens first (from the Tokens tab → Tools → Export) if you need to keep a backup.

This is separate from connecting the library for components, colors and typographies. You can use shared assets without importing tokens, and import tokens only when you want the file's token setup to match the library.
