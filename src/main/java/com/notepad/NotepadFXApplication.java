package com.notepad;

import com.notepad.event.StageReadyEvent;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.stage.Stage;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.context.ConfigurableApplicationContext;

public class NotepadFXApplication extends Application {
    private ConfigurableApplicationContext context;

    @Override
    public void init() {
        // Inicializar el contexto de Spring en el inicio de JavaFX
        this.context = new SpringApplicationBuilder()
                .sources(SpringBootApp.class)
                .run(getParameters().getRaw().toArray(new String[0]));
    }

    @Override
    public void start(Stage stage) {
        // Publicar el evento indicando que la ventana principal está lista
        this.context.publishEvent(new StageReadyEvent(stage));
    }

    @Override
    public void stop() {
        // Asegurar el cierre del contexto de Spring al salir de JavaFX
        this.context.close();
        Platform.exit();
    }
}
