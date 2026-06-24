package com.notepad;

import javafx.application.Application;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SpringBootApp {
    public static void main(String[] args) {
        // Iniciar la aplicación JavaFX en el classpath
        Application.launch(NotepadFXApplication.class, args);
    }
}
