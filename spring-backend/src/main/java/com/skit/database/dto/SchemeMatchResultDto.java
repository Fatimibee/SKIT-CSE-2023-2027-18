package com.skit.database.dto;

import com.skit.database.entity.Scheme;
import java.util.List;

public class SchemeMatchResultDto {

    private Scheme scheme;
    private double matchPercentage;
    private List<String> matchedCriteria;
    private List<String> unmatchedCriteria;
    private String explanation;

    public SchemeMatchResultDto() {}

    public SchemeMatchResultDto(Scheme scheme, double matchPercentage, List<String> matchedCriteria, List<String> unmatchedCriteria, String explanation) {
        this.scheme = scheme;
        this.matchPercentage = matchPercentage;
        this.matchedCriteria = matchedCriteria;
        this.unmatchedCriteria = unmatchedCriteria;
        this.explanation = explanation;
    }

    public Scheme getScheme() { return scheme; }
    public void setScheme(Scheme scheme) { this.scheme = scheme; }

    public double getMatchPercentage() { return matchPercentage; }
    public void setMatchPercentage(double matchPercentage) { this.matchPercentage = matchPercentage; }

    public List<String> getMatchedCriteria() { return matchedCriteria; }
    public void setMatchedCriteria(List<String> matchedCriteria) { this.matchedCriteria = matchedCriteria; }

    public List<String> getUnmatchedCriteria() { return unmatchedCriteria; }
    public void setUnmatchedCriteria(List<String> unmatchedCriteria) { this.unmatchedCriteria = unmatchedCriteria; }

    public String getExplanation() { return explanation; }
    public void setExplanation(String explanation) { this.explanation = explanation; }
}
