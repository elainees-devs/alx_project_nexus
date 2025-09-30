from django.db import models
from django.conf import settings


# ---------------------------------------------------------
# Skill Model
# ---------------------------------------------------------
# Represents a specific skill (e.g., Python, Project Management).
# - Used to tag jobs with required skills.
# - Skills are unique and ordered alphabetically by name.
class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'Skills'
        ordering = ["name"]

    def __str__(self):
        return self.name
  

# ---------------------------------------------------------
# Job Model
# ---------------------------------------------------------
# Represents a job posting created by a company.
# - Includes job details like title, description, location, salary, and status.
# - Supports classification by employment type, work location, and experience level.
# - Linked to a company and associated with required skills (via JobSkill).
# - Tracks metadata such as creator, posting date, and closing date.
# - Indexed for efficient querying by company, status, and posted date.
class Job(models.Model):
    # Enum choices
    EMPLOYMENT_TYPE_CHOICES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
        ("temporary", "Temporary"),
    ]

    WORK_LOCATION_TYPE_CHOICES = [
        ("onsite", "Onsite"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ("entry", "Entry"),
        ("mid", "Mid"),
        ("senior", "Senior"),
        ("lead", "Lead"),
    ]

    JOB_STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("draft", "Draft"),
    ]

    title = models.CharField(max_length=255)
    description = models.JSONField(default=list, blank=True, null=True)
    location = models.CharField(max_length=255)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    work_location_type = models.CharField(max_length=20, choices=WORK_LOCATION_TYPE_CHOICES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=JOB_STATUS_CHOICES)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name="jobs"
    )
    skills = models.ManyToManyField(
        "Skill",
        related_name="jobs",
        through="JobSkill"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_jobs"
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=['company'], name='idx_jobs_company'),
            models.Index(fields=['status'], name='idx_jobs_status'),
            models.Index(fields=['posted_date'], name='idx_jobs_posted_date'),
        ]


# ---------------------------------------------------------
# JobSkill Model
# ---------------------------------------------------------
# Represents the many-to-many relationship between jobs and skills.
# - Each record links one job with one required skill.
# - Enforces uniqueness so the same skill cannot be added twice to a job.
# - Indexed for efficient querying by job and skill.
class JobSkill(models.Model):
    job = models.ForeignKey(
        'Job',
        on_delete=models.CASCADE,
        related_name='job_skills'
    )
    skill = models.ForeignKey(
        'Skill',
        on_delete=models.CASCADE,
        related_name='job_skills'
    )

    class Meta:
        unique_together = ('job', 'skill')
        ordering = ["id"]
        indexes = [
            models.Index(fields=['job'], name='idx_job_skills_job'),
            models.Index(fields=['skill'], name='idx_job_skills_skill'),
        ]

    def __str__(self):
        return f"{self.job.title} - {self.skill.name}"
