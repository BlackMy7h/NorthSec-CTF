package com.example.ctf.Controllers;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.web.bind.annotation.*;

@RestController
public class Endpoints {

    private static final Logger logger = LogManager.getLogger(Endpoints.class);


    @GetMapping("/search")
    public String search(@RequestParam String q) {
        logger.error("User search query: " + q);
        return "Searching for: " + q;
    }

    /**
     * Secondary sink (lower severity)
     */
    @GetMapping("/login")
    public String login(@RequestParam String user) {
        logger.info("Login attempt: " + user);
        return "Login logged for: " + user;
    }

    /**
     * Recon endpoint
     */
    @GetMapping("/health")
    public String health() {
        return "SandwishPicnic v1.0.0-VULNERABLE";
    }
}
