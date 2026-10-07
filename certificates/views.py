from django.core.files.base import ContentFile
from django.http import FileResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import CertificateJob, Certificate
from .serializers import RecipientSerializer
from .utils import generate_certificate


class CreateJobView(APIView):

    def post(self, request):

        recipients = request.data.get("recipients")

        # Check whether recipients exists
        if recipients is None:
            return Response(
                {
                    "error": "recipients field is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check whether recipients is a list
        if not isinstance(recipients, list):
            return Response(
                {
                    "error": "recipients must be a list."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check empty list
        if len(recipients) == 0:
            return Response(
                {
                    "error": "At least one recipient is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create job
        job = CertificateJob.objects.create(
            total=len(recipients),
            status="processing"
        )

        # Process each recipient separately
        for recipient_data in recipients:

            serializer = RecipientSerializer(
                data=recipient_data
            )

           
            # INVALID RECIPIENT
         
            if not serializer.is_valid():

                errors = serializer.errors

                failure_reason = str(errors)

                name = recipient_data.get("name", "")
                email = recipient_data.get("email")

                if not isinstance(name, str):
                    name = str(name)[:100]

                if not isinstance(email, str):
                    email = None

                Certificate.objects.create(
                    job=job,
                    name=name[:100],
                    email=email,
                    status="failed",
                    failure_reason=failure_reason
                )

                job.failed += 1
                job.save()

                continue

            # VALID RECIPIENT
           
            name = serializer.validated_data["name"]
            email = serializer.validated_data["email"]

            certificate = Certificate.objects.create(
                job=job,
                name=name,
                email=email,
                status="success"
            )

            try:

                pdf_buffer = generate_certificate(
                    name,
                    email,
                    certificate.id
                )

                filename = f"certificate_{certificate.id}.pdf"

                certificate.pdf_file.save(
                    filename,
                    ContentFile(pdf_buffer.getvalue()),
                    save=True
                )

                job.succeeded += 1
                job.save()

            except Exception as e:

                certificate.status = "failed"
                certificate.failure_reason = str(e)
                certificate.save()

                job.failed += 1
                job.save()

        # Final job status
        if job.failed == 0:
            job.status = "completed"
        else:
            job.status = "completed_with_errors"

        job.save()

        return Response(
            {
                "job_id": job.id,
                "status": job.status,
                "total": job.total,
                "succeeded": job.succeeded,
                "failed": job.failed
            },
            status=status.HTTP_201_CREATED
        )


class JobStatusView(APIView):

    def get(self, request, job_id):

        try:
            job = CertificateJob.objects.get(id=job_id)

        except CertificateJob.DoesNotExist:
            return Response(
                {
                    "error": "Job not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        certificates = job.certificates.all()

        results = []

        for certificate in certificates:

            result = {
                "certificate_id": certificate.id,
                "name": certificate.name,
                "email": certificate.email,
                "status": certificate.status,
            }

            if certificate.status == "failed":
                result["failure_reason"] = certificate.failure_reason

            if certificate.status == "success":
                result["download_url"] = (
                    f"/api/certificates/"
                    f"{certificate.id}/download/"
                )

            results.append(result)

        return Response(
            {
                "job_id": job.id,
                "status": job.status,
                "total": job.total,
                "succeeded": job.succeeded,
                "failed": job.failed,
                "certificates": results
            },
            status=status.HTTP_200_OK
        )
class CertificateDownloadView(APIView):

    def get(self, request, certificate_id):

        try:
            certificate = Certificate.objects.get(
                id=certificate_id
            )

        except Certificate.DoesNotExist:
            return Response(
                {
                    "error": "Certificate not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if certificate.status != "success":
            return Response(
                {
                    "error": "Certificate was not generated successfully.",
                    "reason": certificate.failure_reason
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not certificate.pdf_file:
            return Response(
                {
                    "error": "PDF file not available."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        response = FileResponse(
            certificate.pdf_file.open("rb"),
            content_type="application/pdf"
        )

        response["Content-Disposition"] = (
            f'attachment; filename="certificate_{certificate.id}.pdf"'
        )

        return response