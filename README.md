# Windows Virtual Folder (Rust)

This project is a minimal implementation of a Windows Shell Namespace Extension written in Rust. It allows you to create a "virtual folder" that appears directly in your Windows File Explorer, just like any other system folder.

## What is this?

This is a foundational project for developers looking to integrate custom virtual directories into the Windows operating system. It provides the necessary components to register a new folder location within File Explorer, which can then be programmed to display dynamic content (e.g., a list of network resources, application-specific items, or generated files) without them physically existing on the disk.

Currently, this project serves as a *skeleton*. It successfully sets up the core infrastructure for the virtual folder but does not yet populate it with any content. It's a starting point for more complex applications.

## Features

-   Creates a basic virtual folder entry in Windows File Explorer.
-   Uses modern Rust with `windows-rs` for safe and efficient Windows API interactions.
-   Provides a template for implementing custom `IShellFolder` functionality.

## How to Build

To build this project, you will need the Rust toolchain installed.

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd my_uuid_folder
    ```
2.  **Build the project**:
    Navigate to the project root directory in your terminal and run:
    ```bash
    cargo build --release
    ```
    This command will compile the project and generate a dynamic-link library (DLL) file. You will find the DLL in the `target/release/` directory (e.g., `my_uuid_folder.dll`).

## How to Use (Installation)

Using a Windows Shell Namespace Extension involves registering the generated DLL with the operating system.

**Important Note**: This project currently creates an *empty* virtual folder. After registration, you will see the folder in File Explorer, but it will not contain any items until further development.

### Registration Steps (General - placeholder for future specific instructions):

1.  **Locate the DLL**: After building, find your `my_uuid_folder.dll` in the `target/release/` directory.
2.  **Register the COM Server**: Typically, you would use `regsvr32.exe` for this, or programmatically register it.
    ```bash
    # Example (DO NOT RUN WITHOUT UNDERSTANDING)
    # regsvr32.exe path\to\my_uuid_folder.dll
    ```
    *Note: Specific registration steps might vary and will be detailed as the project develops.*
3.  **Restart Explorer**: You might need to restart `explorer.exe` for the changes to take effect.

## Future Development

The primary next step for this project is to implement the logic within the `IShellFolder` interface to dynamically generate and display items within the virtual folder. This will involve:

-   Populating the folder with custom items (e.g., files, subfolders).
-   Handling item properties, context menus, and drag-and-drop operations.
-   Responding to user interactions within the virtual folder.