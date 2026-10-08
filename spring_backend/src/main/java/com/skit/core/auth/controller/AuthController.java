package com.skit.core.auth.controller;

import com.google.api.client.googleapis.auth.oauth2.GoogleIdToken;
import com.skit.core.auth.dto.AuthResponse;
import com.skit.core.auth.dto.GoogleAuthRequest;
import com.skit.core.auth.service.GoogleAuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "http://localhost:5173")
public class AuthController {

    @Autowired
    private GoogleAuthService googleAuthService;

    @PostMapping("/google")
    public ResponseEntity<?> authenticateWithGoogle(@RequestBody GoogleAuthRequest request) {
        try {
            // Verify the ID token from the frontend
            GoogleIdToken.Payload payload = googleAuthService.verifyToken(request.getCredential());
            
            // Generate or fetch your application's token
            // As a placeholder, we are returning a dummy token containing the user's email
            String customToken = "dummy-jwt-for-" + payload.getEmail();
            
            return ResponseEntity.ok(new AuthResponse(customToken));
            
        } catch (Exception e) {
            return ResponseEntity.status(401).body("Authentication failed: " + e.getMessage());
        }
    }
}
