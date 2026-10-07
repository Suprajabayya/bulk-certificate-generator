from django.db import models


class CertificateJob(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('completed_with_errors', 'Completed with Errors'),
    ]

    total = models.IntegerField(default=0)

    succeeded = models.IntegerField(default=0)

    failed = models.IntegerField(default=0)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Job {self.id}"


class Certificate(models.Model):

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    job = models.ForeignKey(
        CertificateJob,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    name = models.CharField(max_length=100)

    email = models.EmailField(blank=True,null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    failure_reason = models.TextField(
        blank=True,
        null=True
    )

    pdf_file = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"
