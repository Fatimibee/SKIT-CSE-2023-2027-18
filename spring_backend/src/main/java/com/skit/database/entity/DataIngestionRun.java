package com.skit.database.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "data_ingestion_runs")
public class DataIngestionRun {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "run_id")
    private Long runId;

    @Column(name = "run_timestamp", updatable = false)
    private LocalDateTime runTimestamp;

    @Column(name = "source_file", length = 255)
    private String sourceFile;

    @Column(name = "records_read")
    private Integer recordsRead;

    @Column(name = "records_inserted")
    private Integer recordsInserted;

    @Column(name = "records_updated")
    private Integer recordsUpdated;

    @Column(name = "records_rejected")
    private Integer recordsRejected;

    @Column(name = "status", length = 50)
    private String status;

    @PrePersist
    protected void onCreate() {
        runTimestamp = LocalDateTime.now();
    }

    public DataIngestionRun() {}

    public DataIngestionRun(String sourceFile, Integer recordsRead, Integer recordsInserted, String status) {
        this.sourceFile = sourceFile;
        this.recordsRead = recordsRead;
        this.recordsInserted = recordsInserted;
        this.status = status;
    }

    public Long getRunId() { return runId; }
    public void setRunId(Long runId) { this.runId = runId; }

    public LocalDateTime getRunTimestamp() { return runTimestamp; }
    public void setRunTimestamp(LocalDateTime runTimestamp) { this.runTimestamp = runTimestamp; }

    public String getSourceFile() { return sourceFile; }
    public void setSourceFile(String sourceFile) { this.sourceFile = sourceFile; }

    public Integer getRecordsRead() { return recordsRead; }
    public void setRecordsRead(Integer recordsRead) { this.recordsRead = recordsRead; }

    public Integer getRecordsInserted() { return recordsInserted; }
    public void setRecordsInserted(Integer recordsInserted) { this.recordsInserted = recordsInserted; }

    public Integer getRecordsUpdated() { return recordsUpdated; }
    public void setRecordsUpdated(Integer recordsUpdated) { this.recordsUpdated = recordsUpdated; }

    public Integer getRecordsRejected() { return recordsRejected; }
    public void setRecordsRejected(Integer recordsRejected) { this.recordsRejected = recordsRejected; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
