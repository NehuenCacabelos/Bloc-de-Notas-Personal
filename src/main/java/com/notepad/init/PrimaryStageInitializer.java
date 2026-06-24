package com.notepad.init;

import com.notepad.event.StageReadyEvent;
import com.notepad.ui.NotepadController;
import javafx.scene.Scene;
import javafx.stage.Stage;
import org.springframework.context.ApplicationListener;
import org.springframework.stereotype.Component;

@Component
public class PrimaryStageInitializer implements ApplicationListener<StageReadyEvent> {

    private final NotepadController notepadController;

    public PrimaryStageInitializer(NotepadController notepadController) {
        this.notepadController = notepadController;
    }

    @Override
    public void onApplicationEvent(StageReadyEvent event) {
        Stage stage = event.getStage();
        
        // Asignar la ventana principal al controlador para diálogos de archivos
        notepadController.setPrimaryStage(stage);
        
        // Crear la escena principal a partir del root del controlador
        Scene scene = new Scene(notepadController.getRoot(), 900, 650);
        
        // Cargar los estilos CSS
        scene.getStylesheets().add(getClass().getResource("/styles/style.css").toExternalForm());
        
        stage.setScene(scene);
        stage.setTitle("Bloc de Notas Profesional");
        stage.show();
    }
}
