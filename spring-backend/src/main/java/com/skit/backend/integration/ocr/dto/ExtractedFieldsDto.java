package com.skit.backend.integration.ocr.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExtractedFieldsDto {

    private String name;
    private String dob;
    private String gender;
    private String category;
    private Integer income;
    private String state;
    private String district;

    @JsonProperty("document_type")
    private String documentType;

    private String address;
}
