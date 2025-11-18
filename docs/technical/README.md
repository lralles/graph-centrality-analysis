# Technical Documentation

This folder contains technical documentation for the Graph Centrality Analysis application.

## Architecture Overview

The application follows the Model-View-Controller (MVC) pattern:

- **Models** (`src/models/`): Data layer handling graph loading, analysis, and caching
- **Views** (`src/gui/`): User interface components built with Tkinter
- **Controllers** (`src/controllers/`): Business logic coordinating between models and views
- **Application** (`src/application/`): Entry point and main application setup

## Documentation Files

- [MVC Architecture](mvc-architecture.md) - Overview of the MVC pattern implementation
- [Models](models.md) - Data layer classes and services
- [Views](views.md) - GUI components and user interface
- [Controllers](controllers.md) - Business logic and event handling
- [Dependencies](dependencies.md) - External libraries and requirements
- [Compilation](compilation.md) - Building executables and automated builds