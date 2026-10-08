package com.skit.database;

import com.skit.database.dto.SchemeMatchResultDto;
import com.skit.database.entity.Scheme;
import com.skit.database.entity.User;
import com.skit.database.repository.SchemeRepository;
import com.skit.database.service.SchemeMatchingService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class SchemeMatchingServiceTest {

    private SchemeRepository schemeRepository;
    private SchemeMatchingService schemeMatchingService;

    @BeforeEach
    public void setUp() {
        schemeRepository = mock(SchemeRepository.class);
        schemeMatchingService = new SchemeMatchingService(schemeRepository);
    }

    @Test
    public void testEvaluateUserEligibilityFullMatch() {
        User user = new User("Divyansh Khinchi", "divyansh@example.com", "hash123");
        user.setState("Rajasthan");
        user.setAge(25);
        user.setGender("Male");
        user.setCategory("General");
        user.setOccupation("Farmer");
        user.setAnnualIncome(new BigDecimal("200000"));

        Scheme scheme = new Scheme("Kisan Subsidy", "kisan-subsidy");
        scheme.setEligibilityState("Rajasthan");
        scheme.setAgeMin(18);
        scheme.setAgeMax(60);
        scheme.setGender("Male");
        scheme.setCategory("General");
        scheme.setOccupation("Farmer");
        scheme.setIncomeMax(new BigDecimal("300000"));

        SchemeMatchResultDto result = schemeMatchingService.evaluateUserEligibility(user, scheme);

        assertEquals(100.0, result.getMatchPercentage());
        assertTrue(result.getUnmatchedCriteria().isEmpty());
    }

    @Test
    public void testEvaluateUserEligibilityPartialMatch() {
        User user = new User("Test User", "test@example.com", "hash123");
        user.setState("Gujarat");
        user.setAge(25);
        user.setGender("Female");

        Scheme scheme = new Scheme("Rajasthan Girl Scheme", "raj-girl-scheme");
        scheme.setEligibilityState("Rajasthan");
        scheme.setGender("Female");
        scheme.setAgeMin(18);
        scheme.setAgeMax(30);

        SchemeMatchResultDto result = schemeMatchingService.evaluateUserEligibility(user, scheme);

        assertTrue(result.getMatchPercentage() > 0);
        assertTrue(result.getMatchPercentage() < 100);
        assertFalse(result.getUnmatchedCriteria().isEmpty());
    }
}
