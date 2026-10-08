package com.skit.database.repository;

import com.skit.database.entity.DataIngestionRun;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface DataIngestionRunRepository extends JpaRepository<DataIngestionRun, Long> {

    Optional<DataIngestionRun> findTopByOrderByRunTimestampDesc();
}
