# MVC Architecture

The application implements a clean Model-View-Controller architecture to separate concerns and maintain code organization.

## Architecture Flow

```
User Input → View → Controller → Model → Controller → View → User Display
```

## Layer Responsibilities

### Model Layer (`src/models/`)
- **Data Management**: Loading graphs from files (TSV, CYS, GEXF)
- **Business Logic**: Centrality analysis and graph processing
- **Caching**: Layout and computation result caching
- **Graph Generation**: Random graph creation

### View Layer (`src/gui/`)
- **User Interface**: Tkinter-based GUI components
- **Data Presentation**: Tables, plots, and interactive elements
- **User Input**: File selection, parameter configuration
- **Visual Feedback**: Status updates and progress indication

### Controller Layer (`src/controllers/`)
- **Event Handling**: Coordinating user actions with business logic
- **Data Flow**: Managing communication between views and models
- **State Management**: Maintaining application state and user preferences

## Key Design Patterns

- **Dependency Injection**: Controller receives model instances via constructor
- **Observer Pattern**: Views update automatically when data changes
- **Command Pattern**: User actions are encapsulated as controller methods
- **Factory Pattern**: Graph loading supports multiple file formats