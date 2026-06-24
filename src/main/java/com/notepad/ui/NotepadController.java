package com.notepad.ui;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.control.*;
import javafx.scene.input.KeyCombination;
import javafx.scene.layout.*;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import org.springframework.stereotype.Component;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

@Component
public class NotepadController {

    private final BorderPane root;
    private final TextArea textArea;
    
    // Elementos de la Barra de Estado
    private final Label cursorLabel;
    private final Label zoomLabel;
    private HBox statusBar;

    private Stage primaryStage;
    private File currentFile = null;

    // Estado del estilo y zoom
    private boolean isBold = false;
    private double zoomFactor = 1.0;
    private final double baseFontSize = 12.0; // 12pt como base para Consolas
    private final String fontColor = "#ffffff"; // Blanco puro para modo oscuro

    // Idioma seleccionado (true = Español, false = Inglés)
    private boolean isSpanish = true;

    // Referencias a los componentes de menú para cambio de idioma dinámico
    private Menu menuFile, menuEdit, menuFormat, menuView, menuLanguage, menuHelp;
    private MenuItem itemNew, itemOpen, itemSave, itemSaveAs, itemExit;
    private MenuItem itemUndo, itemRedo, itemCut, itemCopy, itemPaste, itemSelectAll;
    private CheckMenuItem itemWordWrap, itemBold;
    private Menu menuZoom;
    private MenuItem itemZoomIn, itemZoomOut, itemResetZoom;
    private CheckMenuItem itemStatusBar;
    private RadioMenuItem itemLangEs, itemLangEn;
    private MenuItem itemAbout;

    public NotepadController() {
        this.root = new BorderPane();
        this.textArea = new TextArea();
        this.cursorLabel = new Label("Ln 1, Col 1");
        this.zoomLabel = new Label("100%");

        buildUI();
    }

    public Parent getRoot() {
        return root;
    }

    public void setPrimaryStage(Stage stage) {
        this.primaryStage = stage;
        updateTitle();
    }

    private void buildUI() {
        // 1. Barra de Menú Superior (Menu Bar)
        MenuBar menuBar = new MenuBar();
        
        // Inicializar menús
        menuFile = new Menu();
        menuEdit = new Menu();
        menuFormat = new Menu();
        menuView = new Menu();
        menuLanguage = new Menu();
        menuHelp = new Menu();

        // --- MENÚ ARCHIVO (FILE) ---
        itemNew = new MenuItem();
        itemNew.setAccelerator(KeyCombination.keyCombination("Shortcut+N"));
        itemNew.setOnAction(e -> newFile());

        itemOpen = new MenuItem();
        itemOpen.setAccelerator(KeyCombination.keyCombination("Shortcut+O"));
        itemOpen.setOnAction(e -> openFile());

        itemSave = new MenuItem();
        itemSave.setAccelerator(KeyCombination.keyCombination("Shortcut+S"));
        itemSave.setOnAction(e -> saveFile());

        itemSaveAs = new MenuItem();
        itemSaveAs.setAccelerator(KeyCombination.keyCombination("Shortcut+Shift+S"));
        itemSaveAs.setOnAction(e -> saveFileAs());

        itemExit = new MenuItem();
        itemExit.setAccelerator(KeyCombination.keyCombination("Shortcut+Q"));
        itemExit.setOnAction(e -> {
            if (primaryStage != null) {
                primaryStage.close();
            }
        });

        menuFile.getItems().addAll(itemNew, itemOpen, itemSave, itemSaveAs, new SeparatorMenuItem(), itemExit);

        // --- MENÚ EDICIÓN (EDIT) ---
        itemUndo = new MenuItem();
        itemUndo.setAccelerator(KeyCombination.keyCombination("Shortcut+Z"));
        itemUndo.setOnAction(e -> textArea.undo());

        itemRedo = new MenuItem();
        itemRedo.setAccelerator(KeyCombination.keyCombination("Shortcut+Y"));
        itemRedo.setOnAction(e -> textArea.redo());

        itemCut = new MenuItem();
        itemCut.setAccelerator(KeyCombination.keyCombination("Shortcut+X"));
        itemCut.setOnAction(e -> textArea.cut());

        itemCopy = new MenuItem();
        itemCopy.setAccelerator(KeyCombination.keyCombination("Shortcut+C"));
        itemCopy.setOnAction(e -> textArea.copy());

        itemPaste = new MenuItem();
        itemPaste.setAccelerator(KeyCombination.keyCombination("Shortcut+V"));
        itemPaste.setOnAction(e -> textArea.paste());

        itemSelectAll = new MenuItem();
        itemSelectAll.setAccelerator(KeyCombination.keyCombination("Shortcut+A"));
        itemSelectAll.setOnAction(e -> textArea.selectAll());

        menuEdit.getItems().addAll(
            itemUndo, itemRedo, new SeparatorMenuItem(),
            itemCut, itemCopy, itemPaste, new SeparatorMenuItem(),
            itemSelectAll
        );

        // --- MENÚ FORMATO (FORMAT) ---
        itemWordWrap = new CheckMenuItem();
        itemWordWrap.setSelected(true); // Ajuste de línea activo por defecto
        itemWordWrap.setOnAction(e -> textArea.setWrapText(itemWordWrap.isSelected()));

        itemBold = new CheckMenuItem();
        itemBold.setOnAction(e -> {
            isBold = itemBold.isSelected();
            updateTextAreaStyle();
        });

        menuFormat.getItems().addAll(itemWordWrap, itemBold);

        // --- MENÚ VER (VIEW) ---
        menuZoom = new Menu();
        itemZoomIn = new MenuItem();
        itemZoomIn.setAccelerator(KeyCombination.keyCombination("Shortcut+Equals")); // Ctrl + =
        itemZoomIn.setOnAction(e -> zoomIn());

        itemZoomOut = new MenuItem();
        itemZoomOut.setAccelerator(KeyCombination.keyCombination("Shortcut+Minus")); // Ctrl + -
        itemZoomOut.setOnAction(e -> zoomOut());

        itemResetZoom = new MenuItem();
        itemResetZoom.setAccelerator(KeyCombination.keyCombination("Shortcut+Digit0")); // Ctrl + 0
        itemResetZoom.setOnAction(e -> resetZoom());

        menuZoom.getItems().addAll(itemZoomIn, itemZoomOut, itemResetZoom);

        itemStatusBar = new CheckMenuItem();
        itemStatusBar.setSelected(true);
        itemStatusBar.setOnAction(e -> {
            if (itemStatusBar.isSelected()) {
                root.setBottom(statusBar);
            } else {
                root.setBottom(null);
            }
        });

        menuView.getItems().addAll(menuZoom, itemStatusBar);

        // --- MENÚ IDIOMA (LANGUAGE) ---
        ToggleGroup langGroup = new ToggleGroup();
        itemLangEs = new RadioMenuItem();
        itemLangEs.setSelected(true);
        itemLangEs.setToggleGroup(langGroup);
        itemLangEs.setOnAction(e -> {
            isSpanish = true;
            updateLanguage();
        });

        itemLangEn = new RadioMenuItem();
        itemLangEn.setToggleGroup(langGroup);
        itemLangEn.setOnAction(e -> {
            isSpanish = false;
            updateLanguage();
        });

        menuLanguage.getItems().addAll(itemLangEs, itemLangEn);

        // --- MENÚ AYUDA (HELP) ---
        itemAbout = new MenuItem();
        itemAbout.setOnAction(e -> showAboutAlert());

        menuHelp.getItems().addAll(itemAbout);

        // Añadir menús a la barra
        menuBar.getMenus().addAll(menuFile, menuEdit, menuFormat, menuView, menuLanguage, menuHelp);
        root.setTop(menuBar);

        // Configurar los textos iniciales (Español)
        updateLanguage();

        // 2. Área de Texto Principal (Text Area)
        textArea.getStyleClass().add("editor-textarea");
        textArea.setWrapText(true); // Ajuste de línea activo
        VBox.setVgrow(textArea, Priority.ALWAYS);
        root.setCenter(textArea);

        // Escuchas para actualizar la posición del cursor en tiempo real
        textArea.caretPositionProperty().addListener((obs, oldVal, newVal) -> updateCursorPosition());
        textArea.textProperty().addListener((obs, oldVal, newVal) -> updateCursorPosition());

        // 3. Barra de Estado (Status Bar)
        this.statusBar = new HBox(20);
        statusBar.getStyleClass().add("status-bar");
        statusBar.setPadding(new Insets(3, 15, 3, 15));
        statusBar.setAlignment(Pos.CENTER_LEFT);

        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);

        Label lineEndingLabel = new Label("Windows (CRLF)");
        Label encodingLabel = new Label("UTF-8");

        statusBar.getChildren().addAll(
            cursorLabel, 
            spacer, 
            zoomLabel, 
            new Separator(javafx.geometry.Orientation.VERTICAL), 
            lineEndingLabel, 
            new Separator(javafx.geometry.Orientation.VERTICAL), 
            encodingLabel
        );
        root.setBottom(statusBar);

        // Configurar estilos iniciales de fuente
        updateTextAreaStyle();
    }

    private void updateTextAreaStyle() {
        String fontWeight = isBold ? "bold" : "normal";
        double currentFontSize = baseFontSize * zoomFactor;
        
        textArea.setStyle(
                "-fx-font-weight: " + fontWeight + ";" +
                "-fx-font-size: " + currentFontSize + "pt;" +
                "-fx-text-fill: " + fontColor + ";"
        );
    }

    private void updateCursorPosition() {
        int caretPos = textArea.getCaretPosition();
        var paragraphs = textArea.getParagraphs();
        int line = 1;
        int col = 1;
        int accumulated = 0;
        for (int i = 0; i < paragraphs.size(); i++) {
            int len = paragraphs.get(i).length();
            if (caretPos <= accumulated + len) {
                line = i + 1;
                col = caretPos - accumulated + 1;
                break;
            }
            accumulated += len + 1;
        }
        cursorLabel.setText("Ln " + line + ", Col " + col);
    }

    private void zoomIn() {
        zoomFactor = Math.min(3.0, zoomFactor + 0.1);
        updateZoomLabel();
        updateTextAreaStyle();
    }

    private void zoomOut() {
        zoomFactor = Math.max(0.5, zoomFactor - 0.1);
        updateZoomLabel();
        updateTextAreaStyle();
    }

    private void resetZoom() {
        zoomFactor = 1.0;
        updateZoomLabel();
        updateTextAreaStyle();
    }

    private void updateZoomLabel() {
        zoomLabel.setText(String.format("%d%%", (int)(zoomFactor * 100)));
    }

    private void newFile() {
        textArea.clear();
        currentFile = null;
        updateTitle();
    }

    private void openFile() {
        if (primaryStage == null) return;
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle(isSpanish ? "Abrir archivo" : "Open file");
        fileChooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter(isSpanish ? "Archivos de texto (*.txt)" : "Text files (*.txt)", "*.txt")
        );
        File file = fileChooser.showOpenDialog(primaryStage);
        if (file != null) {
            try {
                String content = Files.readString(file.toPath(), StandardCharsets.UTF_8);
                textArea.setText(content);
                currentFile = file;
                updateTitle();
            } catch (IOException e) {
                showErrorAlert(
                    isSpanish ? "Error al abrir" : "Error opening file", 
                    (isSpanish ? "No se pudo abrir el archivo:\n" : "Could not open file:\n") + e.getMessage()
                );
            }
        }
    }

    private void saveFile() {
        if (currentFile == null) {
            saveFileAs();
        } else {
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(currentFile, StandardCharsets.UTF_8))) {
                writer.write(textArea.getText());
            } catch (IOException e) {
                showErrorAlert(
                    isSpanish ? "Error al guardar" : "Error saving file", 
                    (isSpanish ? "No se pudo escribir en el archivo:\n" : "Could not write to file:\n") + e.getMessage()
                );
            }
        }
    }

    private void saveFileAs() {
        if (primaryStage == null) return;
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle(isSpanish ? "Guardar como..." : "Save As...");
        fileChooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter(isSpanish ? "Archivos de texto (*.txt)" : "Text files (*.txt)", "*.txt")
        );
        File file = fileChooser.showSaveDialog(primaryStage);
        if (file != null) {
            currentFile = file;
            saveFile();
            updateTitle();
        }
    }

    private void updateTitle() {
        if (primaryStage != null) {
            String fileName = (currentFile != null) ? currentFile.getName() : (isSpanish ? "Sin título" : "Untitled");
            primaryStage.setTitle(fileName + " - " + (isSpanish ? "Bloc de Notas" : "Notepad"));
        }
    }

    private void updateLanguage() {
        if (isSpanish) {
            menuFile.setText("Archivo");
            itemNew.setText("Nuevo");
            itemOpen.setText("Abrir...");
            itemSave.setText("Guardar");
            itemSaveAs.setText("Guardar como...");
            itemExit.setText("Salir");

            menuEdit.setText("Edición");
            itemUndo.setText("Deshacer");
            itemRedo.setText("Rehacer");
            itemCut.setText("Cortar");
            itemCopy.setText("Copiar");
            itemPaste.setText("Pegar");
            itemSelectAll.setText("Seleccionar todo");

            menuFormat.setText("Formato");
            itemWordWrap.setText("Ajuste de línea");
            itemBold.setText("Fuente en negrita");

            menuView.setText("Ver");
            menuZoom.setText("Zoom");
            itemZoomIn.setText("Acercar");
            itemZoomOut.setText("Alejar");
            itemResetZoom.setText("Restablecer zoom");
            itemStatusBar.setText("Barra de estado");

            menuLanguage.setText("Idioma");
            itemLangEs.setText("Español");
            itemLangEn.setText("English");

            menuHelp.setText("Ayuda");
            itemAbout.setText("Acerca de");
        } else {
            menuFile.setText("File");
            itemNew.setText("New");
            itemOpen.setText("Open...");
            itemSave.setText("Save");
            itemSaveAs.setText("Save As...");
            itemExit.setText("Exit");

            menuEdit.setText("Edit");
            itemUndo.setText("Undo");
            itemRedo.setText("Redo");
            itemCut.setText("Cut");
            itemCopy.setText("Copy");
            itemPaste.setText("Paste");
            itemSelectAll.setText("Select All");

            menuFormat.setText("Format");
            itemWordWrap.setText("Word Wrap");
            itemBold.setText("Bold Font");

            menuView.setText("View");
            menuZoom.setText("Zoom");
            itemZoomIn.setText("Zoom In");
            itemZoomOut.setText("Zoom Out");
            itemResetZoom.setText("Restore Default Zoom");
            itemStatusBar.setText("Status Bar");

            menuLanguage.setText("Language");
            itemLangEs.setText("Español");
            itemLangEn.setText("English");

            menuHelp.setText("Help");
            itemAbout.setText("About Notepad");
        }
        updateTitle();
    }

    private void showAboutAlert() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle(isSpanish ? "Acerca de Bloc de Notas" : "About Notepad");
        alert.setHeaderText(isSpanish ? "Bloc de Notas - Windows Dark Mode Style" : "Notepad - Windows Dark Mode Style");
        alert.setContentText(isSpanish 
            ? "Una aplicación réplica de Notepad en Modo Oscuro con Spring Boot y JavaFX.\nCreada con amor y precisión."
            : "A replica of Notepad in Dark Mode with Spring Boot and JavaFX.\nCreated with love and precision."
        );
        alert.showAndWait();
    }

    private void showErrorAlert(String title, String content) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }
}
