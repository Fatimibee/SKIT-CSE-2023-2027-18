package com.skit.backend.integration.ocr.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class VerificationDto {

    @JsonProperty("is_valid")
    private Boolean isValid;

    @JsonProperty("qr_verified")
    private Boolean qrVerified;

    private List<String> issues;
}
