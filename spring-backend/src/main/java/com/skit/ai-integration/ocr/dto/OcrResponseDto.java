package com.skit.ocr.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OcrResponseDto {

    private String status;
    private String message;

    @JsonProperty("extracted_fields")
    private ExtractedFieldsDto extractedFields;

    private VerificationDto verification;
}
