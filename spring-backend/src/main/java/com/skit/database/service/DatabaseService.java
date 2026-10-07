package com.skit.database.service;

import com.skit.database.entity.DataIngestionRun;
import com.skit.database.entity.RecommendationHistory;
import com.skit.database.entity.Scheme;
import com.skit.database.entity.User;
import com.skit.database.repository.DataIngestionRunRepository;
import com.skit.database.repository.RecommendationHistoryRepository;
import com.skit.database.repository.SchemeRepository;
import com.skit.database.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Service
public class DatabaseService {

    private final UserRepository userRepository;
    private final SchemeRepository schemeRepository;
    private final RecommendationHistoryRepository recommendationHistoryRepository;
    private final DataIngestionRunRepository dataIngestionRunRepository;

    @Autowired
    public DatabaseService(
            UserRepository userRepository,
            SchemeRepository schemeRepository,
            RecommendationHistoryRepository recommendationHistoryRepository,
            DataIngestionRunRepository dataIngestionRunRepository
    ) {
        this.userRepository = userRepository;
        this.schemeRepository = schemeRepository;
        this.recommendationHistoryRepository = recommendationHistoryRepository;
        this.dataIngestionRunRepository = dataIngestionRunRepository;
    }

    public User saveUser(User user) {
        return userRepository.save(user);
    }

    public Optional<User> findUserByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    public Optional<User> findUserById(Long userId) {
        return userRepository.findById(userId);
    }

    public Scheme saveScheme(Scheme scheme) {
        return schemeRepository.save(scheme);
    }

    public List<Scheme> getAllSchemes() {
        return schemeRepository.findAll();
    }

    public Optional<Scheme> findSchemeBySlug(String slug) {
        return schemeRepository.findBySlug(slug);
    }

    public List<Scheme> findSchemesByState(String state) {
        return schemeRepository.findByEligibilityState(state);
    }

    public RecommendationHistory recordRecommendation(User user, Scheme scheme, BigDecimal score, String explanation) {
        RecommendationHistory history = new RecommendationHistory(user, scheme, score, explanation);
        return recommendationHistoryRepository.save(history);
    }

    public List<RecommendationHistory> getUserRecommendationHistory(Long userId) {
        return recommendationHistoryRepository.findByUserUserId(userId);
    }

    public DataIngestionRun recordIngestionRun(String sourceFile, int recordsRead, int inserted, String status) {
        DataIngestionRun run = new DataIngestionRun(sourceFile, recordsRead, inserted, status);
        return dataIngestionRunRepository.save(run);
    }

    public Optional<DataIngestionRun> getLatestIngestionRun() {
        return dataIngestionRunRepository.findTopByOrderByRunTimestampDesc();
    }
}
