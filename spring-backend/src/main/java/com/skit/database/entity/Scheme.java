package com.skit.database.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "schemes")
public class Scheme {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "scheme_id")
    private Long schemeId;

    @Column(name = "title", nullable = false, length = 255)
    private String title;

    @Column(name = "slug", nullable = false, unique = true, length = 255)
    private String slug;

    @Column(name = "ministry", length = 255)
    private String ministry;

    @Column(name = "scheme_category", columnDefinition = "TEXT")
    private String schemeCategory;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "beneficiary_state", length = 100)
    private String beneficiaryState;

    @Column(name = "npi_ministry", length = 255)
    private String npiMinistry;

    @Column(name = "tags", columnDefinition = "TEXT")
    private String tags;

    @Column(name = "typename", length = 50)
    private String typename;

    @Column(name = "categories_normalized", columnDefinition = "TEXT")
    private String categoriesNormalized;

    @Column(name = "tags_normalized", columnDefinition = "TEXT")
    private String tagsNormalized;

    @Column(name = "eligibility", columnDefinition = "TEXT")
    private String eligibility;

    @Column(name = "beneficiaries", columnDefinition = "TEXT")
    private String beneficiaries;

    @Column(name = "benefits", columnDefinition = "TEXT")
    private String benefits;

    @Column(name = "documents_required", columnDefinition = "TEXT")
    private String documentsRequired;

    @Column(name = "application_process", columnDefinition = "TEXT")
    private String applicationProcess;

    @Column(name = "application_mode", length = 50)
    private String applicationMode;

    @Column(name = "state", length = 100)
    private String state;

    @Column(name = "department", length = 255)
    private String department;

    @Column(name = "eligibility_raw", columnDefinition = "TEXT")
    private String eligibilityRaw;

    @Column(name = "beneficiaries_raw", columnDefinition = "TEXT")
    private String beneficiariesRaw;

    @Column(name = "benefits_raw", columnDefinition = "TEXT")
    private String benefitsRaw;

    @Column(name = "documents_required_raw", columnDefinition = "TEXT")
    private String documentsRequiredRaw;

    @Column(name = "age_min")
    private Integer ageMin;

    @Column(name = "age_max")
    private Integer ageMax;

    @Column(name = "gender", length = 20)
    private String gender;

    @Column(name = "income_max", precision = 12, scale = 2)
    private BigDecimal incomeMax;

    @Column(name = "category", length = 50)
    private String category;

    @Column(name = "occupation", length = 100)
    private String occupation;

    @Column(name = "eligibility_state", length = 100)
    private String eligibilityState;

    @Column(name = "education", length = 100)
    private String education;

    @Column(name = "disability", length = 50)
    private String disability;

    @Column(name = "source_url", columnDefinition = "TEXT")
    private String sourceUrl;

    @Column(name = "official_url", columnDefinition = "TEXT")
    private String officialUrl;

    @Column(name = "last_updated", length = 50)
    private String lastUpdated;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public Scheme() {}

    public Scheme(String title, String slug) {
        this.title = title;
        this.slug = slug;
    }

    public Long getSchemeId() { return schemeId; }
    public void setSchemeId(Long schemeId) { this.schemeId = schemeId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getSlug() { return slug; }
    public void setSlug(String slug) { this.slug = slug; }

    public String getMinistry() { return ministry; }
    public void setMinistry(String ministry) { this.ministry = ministry; }

    public String getSchemeCategory() { return schemeCategory; }
    public void setSchemeCategory(String schemeCategory) { this.schemeCategory = schemeCategory; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getBeneficiaryState() { return beneficiaryState; }
    public void setBeneficiaryState(String beneficiaryState) { this.beneficiaryState = beneficiaryState; }

    public String getNpiMinistry() { return npiMinistry; }
    public void setNpiMinistry(String npiMinistry) { this.npiMinistry = npiMinistry; }

    public String getTags() { return tags; }
    public void setTags(String tags) { this.tags = tags; }

    public String getTypename() { return typename; }
    public void setTypename(String typename) { this.typename = typename; }

    public String getCategoriesNormalized() { return categoriesNormalized; }
    public void setCategoriesNormalized(String categoriesNormalized) { this.categoriesNormalized = categoriesNormalized; }

    public String getTagsNormalized() { return tagsNormalized; }
    public void setTagsNormalized(String tagsNormalized) { this.tagsNormalized = tagsNormalized; }

    public String getEligibility() { return eligibility; }
    public void setEligibility(String eligibility) { this.eligibility = eligibility; }

    public String getBeneficiaries() { return beneficiaries; }
    public void setBeneficiaries(String beneficiaries) { this.beneficiaries = beneficiaries; }

    public String getBenefits() { return benefits; }
    public void setBenefits(String benefits) { this.benefits = benefits; }

    public String getDocumentsRequired() { return documentsRequired; }
    public void setDocumentsRequired(String documentsRequired) { this.documentsRequired = documentsRequired; }

    public String getApplicationProcess() { return applicationProcess; }
    public void setApplicationProcess(String applicationProcess) { this.applicationProcess = applicationProcess; }

    public String getApplicationMode() { return applicationMode; }
    public void setApplicationMode(String applicationMode) { this.applicationMode = applicationMode; }

    public String getState() { return state; }
    public void setState(String state) { this.state = state; }

    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }

    public String getEligibilityRaw() { return eligibilityRaw; }
    public void setEligibilityRaw(String eligibilityRaw) { this.eligibilityRaw = eligibilityRaw; }

    public String getBeneficiariesRaw() { return beneficiariesRaw; }
    public void setBeneficiariesRaw(String beneficiariesRaw) { this.beneficiariesRaw = beneficiariesRaw; }

    public String getBenefitsRaw() { return benefitsRaw; }
    public void setBenefitsRaw(String benefitsRaw) { this.benefitsRaw = benefitsRaw; }

    public String getDocumentsRequiredRaw() { return documentsRequiredRaw; }
    public void setDocumentsRequiredRaw(String documentsRequiredRaw) { this.documentsRequiredRaw = documentsRequiredRaw; }

    public Integer getAgeMin() { return ageMin; }
    public void setAgeMin(Integer ageMin) { this.ageMin = ageMin; }

    public Integer getAgeMax() { return ageMax; }
    public void setAgeMax(Integer ageMax) { this.ageMax = ageMax; }

    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }

    public BigDecimal getIncomeMax() { return incomeMax; }
    public void setIncomeMax(BigDecimal incomeMax) { this.incomeMax = incomeMax; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getOccupation() { return occupation; }
    public void setOccupation(String occupation) { this.occupation = occupation; }

    public String getEligibilityState() { return eligibilityState; }
    public void setEligibilityState(String eligibilityState) { this.eligibilityState = eligibilityState; }

    public String getEducation() { return education; }
    public void setEducation(String education) { this.education = education; }

    public String getDisability() { return disability; }
    public void setDisability(String disability) { this.disability = disability; }

    public String getSourceUrl() { return sourceUrl; }
    public void setSourceUrl(String sourceUrl) { this.sourceUrl = sourceUrl; }

    public String getOfficialUrl() { return officialUrl; }
    public void setOfficialUrl(String officialUrl) { this.officialUrl = officialUrl; }

    public String getLastUpdated() { return lastUpdated; }
    public void setLastUpdated(String lastUpdated) { this.lastUpdated = lastUpdated; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
