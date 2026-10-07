from django.urls import path
from .views import CreateJobView, JobStatusView, CertificateDownloadView


urlpatterns = [
    path( "jobs/", CreateJobView.as_view(), name="create-job"),
    path( "jobs/<int:job_id>/", JobStatusView.as_view(),  name="job-status" ),

    path("certificates/<int:certificate_id>/download/",CertificateDownloadView.as_view(), name="certificate-download"
),
]