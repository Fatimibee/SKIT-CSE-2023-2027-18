package com.skit.database.repository;

import com.skit.database.entity.RecommendationHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RecommendationHistoryRepository extends JpaRepository<RecommendationHistory, Long> {

    List<RecommendationHistory> findByUserUserId(Long userId);

    List<RecommendationHistory> findBySchemeSchemeId(Long schemeId);
}
