package com.skit.ocr;

import com.skit.ocr.dto.OcrResponseDto;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

/**
 * Service client for calling the Python OCR Backend API (Port 5000 / 8001).
 * Maintained by Disha Toshniwal.
 */
@Service
public class OcrService {

    private final RestTemplate restTemplate;

    @Value("${ocr.service.url:http://localhost:5000}")
    private String ocrServiceUrl;

    public OcrService() {
        this.restTemplate = new RestTemplate();
    }

    /**
     * Sends an uploaded document (Image or PDF) to the Python OCR Backend for field extraction & verification.
     *
     * @param file uploaded MultipartFile
     * @return OcrResponseDto containing extracted fields and verification results
     */
    public OcrResponseDto extractFieldsAndVerify(MultipartFile file) throws IOException {
        String url = ocrServiceUrl + "/ocr/extract-fields";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        ByteArrayResource fileResource = new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename() != null ? file.getOriginalFilename() : "document";
            }
        };
        body.add("file", fileResource);

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        ResponseEntity<OcrResponseDto> response = restTemplate.postForEntity(url, requestEntity, OcrResponseDto.class);
        return response.getBody();
    }

    /**
     * Sends multiple uploaded documents to the Python OCR Backend for batch field extraction & verification.
     *
     * @param files List of uploaded MultipartFile objects
     * @return String JSON response with aggregated student details and document verification reports
     */
    public String extractBatchFieldsAndVerify(List<MultipartFile> files) throws IOException {
        String url = ocrServiceUrl + "/ocr/extract-batch";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        for (MultipartFile file : files) {
            ByteArrayResource fileResource = new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename() != null ? file.getOriginalFilename() : "document";
                }
            };
            body.add("files", fileResource);
        }

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        ResponseEntity<String> response = restTemplate.postForEntity(url, requestEntity, String.class);
        return response.getBody();
    }
}
