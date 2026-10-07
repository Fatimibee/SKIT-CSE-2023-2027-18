package com.skit.ocr;

import com.skit.database.dto.SchemeMatchResultDto;
import com.skit.database.entity.User;
import com.skit.database.service.SchemeMatchingService;
import com.skit.ocr.dto.ExtractedFieldsDto;
import com.skit.ocr.dto.OcrResponseDto;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.Period;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Controller for handling Frontend Document Uploads.
 * Integrates Python OCR Backend extraction with Database Scheme Eligibility Matching.
 * Maintained by Disha Toshniwal.
 */
@RestController
@RequestMapping("/api/ocr")
@CrossOrigin(origins = "*")
public class OcrController {

    private final OcrService ocrService;
    private final SchemeMatchingService schemeMatchingService;

    @Autowired
    public OcrController(OcrService ocrService, SchemeMatchingService schemeMatchingService) {
        this.ocrService = ocrService;
        this.schemeMatchingService = schemeMatchingService;
    }

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Map<String, Object>> uploadAndExtractDocument(@RequestParam("file") MultipartFile file) {
        Map<String, Object> response = new HashMap<>();
        try {
            if (file == null || file.isEmpty()) {
                response.put("success", false);
                response.put("error", "No file uploaded.");
                return ResponseEntity.badRequest().body(response);
            }

            // Step 1: Call Python OCR Backend via OcrService
            OcrResponseDto ocrResult = ocrService.extractFieldsAndVerify(file);

            response.put("success", true);
            response.put("filename", file.getOriginalFilename());
            response.put("ocr_result", ocrResult);

            ExtractedFieldsDto fields = ocrResult != null ? ocrResult.getExtractedFields() : null;

            // Step 2: Build transient User entity for Scheme Eligibility Evaluation
            User tempUser = new User();
            if (fields != null) {
                tempUser.setFullName(fields.getName());
                tempUser.setGender(fields.getGender());
                tempUser.setCategory(fields.getCategory());
                tempUser.setState(fields.getState());

                if (fields.getIncome() != null) {
                    tempUser.setAnnualIncome(BigDecimal.valueOf(fields.getIncome()));
                }

                if (fields.getDob() != null) {
                    try {
                        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy");
                        LocalDate dob = LocalDate.parse(fields.getDob(), formatter);
                        int age = Period.between(dob, LocalDate.now()).getYears();
                        tempUser.setAge(age);
                    } catch (Exception ignored) {
                    }
                }
            }

            // Step 3: Match Schemes against extracted details
            List<SchemeMatchResultDto> recommendedSchemes = schemeMatchingService.findRecommendedSchemesForUser(tempUser);
            response.put("recommended_schemes", recommendedSchemes);

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            response.put("success", false);
            response.put("error", "Error processing document: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
}
