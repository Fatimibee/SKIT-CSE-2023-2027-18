package com.skit.database.service;

import com.skit.database.dto.SchemeMatchResultDto;
import com.skit.database.entity.Scheme;
import com.skit.database.entity.User;
import com.skit.database.repository.SchemeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class SchemeMatchingService {

    private final SchemeRepository schemeRepository;

    @Autowired
    public SchemeMatchingService(SchemeRepository schemeRepository) {
        this.schemeRepository = schemeRepository;
    }

    public List<SchemeMatchResultDto> findRecommendedSchemesForUser(User user) {
        List<Scheme> allSchemes = schemeRepository.findAll();
        return allSchemes.stream()
                .map(scheme -> evaluateUserEligibility(user, scheme))
                .filter(result -> result.getMatchPercentage() >= 40.0)
                .sorted(Comparator.comparingDouble(SchemeMatchResultDto::getMatchPercentage).reversed())
                .collect(Collectors.toList());
    }

    public SchemeMatchResultDto evaluateUserEligibility(User user, Scheme scheme) {
        List<String> matched = new ArrayList<>();
        List<String> unmatched = new ArrayList<>();
        double totalCriteria = 0;
        double matchedCriteriaCount = 0;

        if (scheme.getEligibilityState() != null && !scheme.getEligibilityState().trim().isEmpty()) {
            totalCriteria++;
            if (user.getState() != null && user.getState().equalsIgnoreCase(scheme.getEligibilityState())) {
                matchedCriteriaCount++;
                matched.add("State: " + user.getState());
            } else {
                unmatched.add("State required: " + scheme.getEligibilityState() + " (User: " + user.getState() + ")");
            }
        }

        if (scheme.getAgeMin() != null || scheme.getAgeMax() != null) {
            totalCriteria++;
            boolean ageOk = true;
            if (user.getAge() != null) {
                if (scheme.getAgeMin() != null && user.getAge() < scheme.getAgeMin()) ageOk = false;
                if (scheme.getAgeMax() != null && user.getAge() > scheme.getAgeMax()) ageOk = false;
            } else {
                ageOk = false;
            }

            if (ageOk) {
                matchedCriteriaCount++;
                matched.add("Age: " + user.getAge() + " years");
            } else {
                unmatched.add("Age limits: " + (scheme.getAgeMin() != null ? scheme.getAgeMin() : 0) +
                              "-" + (scheme.getAgeMax() != null ? scheme.getAgeMax() : 120) + " years");
            }
        }

        if (scheme.getGender() != null && !scheme.getGender().trim().isEmpty()) {
            totalCriteria++;
            if (user.getGender() != null && user.getGender().equalsIgnoreCase(scheme.getGender())) {
                matchedCriteriaCount++;
                matched.add("Gender: " + user.getGender());
            } else {
                unmatched.add("Gender restriction: " + scheme.getGender());
            }
        }

        if (scheme.getCategory() != null && !scheme.getCategory().trim().isEmpty()) {
            totalCriteria++;
            if (user.getCategory() != null && user.getCategory().equalsIgnoreCase(scheme.getCategory())) {
                matchedCriteriaCount++;
                matched.add("Category: " + user.getCategory());
            } else {
                unmatched.add("Category required: " + scheme.getCategory());
            }
        }

        if (scheme.getOccupation() != null && !scheme.getOccupation().trim().isEmpty()) {
            totalCriteria++;
            if (user.getOccupation() != null && user.getOccupation().equalsIgnoreCase(scheme.getOccupation())) {
                matchedCriteriaCount++;
                matched.add("Occupation: " + user.getOccupation());
            } else {
                unmatched.add("Occupation required: " + scheme.getOccupation());
            }
        }

        if (scheme.getIncomeMax() != null && scheme.getIncomeMax().compareTo(BigDecimal.ZERO) > 0) {
            totalCriteria++;
            if (user.getAnnualIncome() != null && user.getAnnualIncome().compareTo(scheme.getIncomeMax()) <= 0) {
                matchedCriteriaCount++;
                matched.add("Income under Rs " + scheme.getIncomeMax());
            } else {
                unmatched.add("Income cap: Rs " + scheme.getIncomeMax());
            }
        }

        if (scheme.getEducation() != null && !scheme.getEducation().trim().isEmpty()) {
            totalCriteria++;
            if (user.getEducation() != null && user.getEducation().equalsIgnoreCase(scheme.getEducation())) {
                matchedCriteriaCount++;
                matched.add("Education: " + user.getEducation());
            } else {
                unmatched.add("Education required: " + scheme.getEducation());
            }
        }

        if (scheme.getDisability() != null && !scheme.getDisability().trim().isEmpty()) {
            totalCriteria++;
            if (user.getDisability() != null && user.getDisability().equalsIgnoreCase(scheme.getDisability())) {
                matchedCriteriaCount++;
                matched.add("Disability: " + user.getDisability());
            } else {
                unmatched.add("Disability status required: " + scheme.getDisability());
            }
        }

        double score = totalCriteria == 0 ? 100.0 : Math.round((matchedCriteriaCount / totalCriteria) * 100.0 * 100.0) / 100.0;
        String explanation = String.format("Scheme '%s' matches %.1f%% of specified eligibility criteria (%d/%d matched).",
                scheme.getTitle(), score, (int) matchedCriteriaCount, (int) totalCriteria);

        return new SchemeMatchResultDto(scheme, score, matched, unmatched, explanation);
    }
}
