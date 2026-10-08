package com.skit.database.repository;

import com.skit.database.entity.Scheme;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Repository
public interface SchemeRepository extends JpaRepository<Scheme, Long> {

    Optional<Scheme> findBySlug(String slug);

    List<Scheme> findByEligibilityState(String eligibilityState);

    List<Scheme> findByGender(String gender);

    List<Scheme> findByCategory(String category);

    List<Scheme> findByOccupation(String occupation);

    List<Scheme> findByEducation(String education);

    List<Scheme> findByDisability(String disability);

    List<Scheme> findByIncomeMaxLessThanEqual(BigDecimal maxIncome);

    @Query("SELECT s FROM Scheme s WHERE " +
           "(:state IS NULL OR s.eligibilityState IS NULL OR LOWER(s.eligibilityState) = LOWER(:state)) AND " +
           "(:gender IS NULL OR s.gender IS NULL OR LOWER(s.gender) = LOWER(:gender)) AND " +
           "(:category IS NULL OR s.category IS NULL OR LOWER(s.category) = LOWER(:category)) AND " +
           "(:occupation IS NULL OR s.occupation IS NULL OR LOWER(s.occupation) = LOWER(:occupation)) AND " +
           "(:age IS NULL OR ((s.ageMin IS NULL OR s.ageMin <= :age) AND (s.ageMax IS NULL OR s.ageMax >= :age))) AND " +
           "(:income IS NULL OR s.incomeMax IS NULL OR s.incomeMax >= :income)")
    List<Scheme> findMatchingSchemes(
            @Param("state") String state,
            @Param("gender") String gender,
            @Param("category") String category,
            @Param("occupation") String occupation,
            @Param("age") Integer age,
            @Param("income") BigDecimal income
    );
}
