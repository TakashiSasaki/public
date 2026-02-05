# Project Configuration for AI Agents and Developers

This document outlines the configuration and key characteristics of the current project, intended for reference by other developers and AI coding agents.

## Project Type

-   **Language**: Rust
-   **Output Type**: `cdylib` (C-compatible dynamic-link library)
-   **Target Platform**: Windows
-   **Purpose**: Implements a Windows Shell Namespace Extension to create a virtual folder within Windows Explorer.

## Core Technologies and Concepts

-   **COM (Component Object Model)**: The project functions as a COM server, exposing interfaces for Windows system interaction.
-   **Windows Shell Programming**: Specifically, it implements the `IShellFolder` interface to define the behavior of the virtual folder.
-   **`IClassFactory`**: Used for instantiating the virtual folder objects.

## Key Dependencies

-   `windows-rs`: Provides Rust bindings for Windows APIs, crucial for COM and Shell development.

## Build Instructions (Conceptual)

This is a standard Rust project. To build:

```bash
cargo build --release
```

The output will be a `.dll` file located in `target/release/`. This DLL needs to be registered with the Windows operating system for the Shell Namespace Extension to function.

## Current Implementation Status

-   The project provides a functional skeleton for a Windows Shell Namespace Extension.
-   It successfully sets up the COM server and the virtual folder structure.
-   **Note**: As of its current state, the virtual folder does not implement functionality to populate its view with items (e.g., files or subfolders). This is the next phase of development.

## Detailed Project Overview and Architecture

This repository contains a minimal Rust implementation of a Windows Shell Namespace Extension. Its primary purpose is to create a "virtual folder" that can be seamlessly integrated into the Windows Explorer shell.

### Architecture

-   **Type**: C-compatible dynamic-link library (`cdylib`), designed to be loaded by Windows system processes (e.g., `explorer.exe`).
-   **Technology**: Implements a COM (Component Object Model) server, which is the standard mechanism for interoperable components on Windows.
-   **Core Interface**: The central logic implements the `IShellFolder` interface, defining the behavior of a folder-like object within the Windows Shell.
-   **Instantiation**: Includes a standard `IClassFactory` for creating instances of the virtual folder object, along with the necessary `DllGetClassObject` entry point for COM activation.

### Dependencies

-   The project relies solely on the `windows-rs` crate (`windows` and `windows-core`), which provides robust Rust bindings for essential Windows APIs, particularly for COM and Shell services.

### Structure

-   **Self-Contained**: The entire implementation resides within a single source file: `src/lib.rs`. There are no additional modules or complex directory hierarchies, emphasizing its focused, single-purpose nature.
-   **Current Status**: The codebase currently serves as a foundational skeleton. It successfully establishes the COM server and the virtual folder infrastructure but does not yet include functionality for populating the folder view with items (e.g., files or subfolders).

This project provides a clear starting point for developing custom virtual folders within the Windows operating system using modern Rust.