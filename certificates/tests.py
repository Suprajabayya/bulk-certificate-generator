from django.test import TestCase
from django.core.files.base import ContentFile

from rest_framework.test import APIClient

from .models import CertificateJob, Certificate
from .utils import generate_certificate


class CertificateAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()


    # TEST 1: Creating a generation job


    def test_create_generation_job(self):

        data = {
            "recipients": [
                {
                    "name": "Supraja",
                    "email": "supraja@gmail.com"
                },
                {
                    "name": "Rahul",
                    "email": "rahul@gmail.com"
                }
            ]
        }

        response = self.client.post(
            "/api/jobs/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.data["total"],
            2
        )

        self.assertEqual(
            response.data["succeeded"],
            2
        )

        self.assertEqual(
            response.data["failed"],
            0
        )

        self.assertTrue(
            CertificateJob.objects.filter(
                id=response.data["job_id"]
            ).exists()
        )


    # TEST 2: Input validation
    

    def test_input_validation(self):

        data = {
            "recipients": [
                {
                    "name": "",
                    "email": "wrong"
                }
            ]
        }

        response = self.client.post(
            "/api/jobs/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.data["total"],
            1
        )

        self.assertEqual(
            response.data["failed"],
            1
        )


    # TEST 3: Certificate generation
    

    def test_certificate_generation(self):

        data = {
            "recipients": [
                {
                    "name": "Supraja",
                    "email": "supraja@gmail.com"
                }
            ]
        }

        response = self.client.post(
            "/api/jobs/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        certificate = Certificate.objects.get(
        job_id=response.data["job_id"]
        
        )

        self.assertEqual(
            certificate.status,
            "success"
        )

        self.assertTrue(
            certificate.pdf_file
        )

    # TEST 4: Job status/progress
   

    def test_job_status(self):

        data = {
            "recipients": [
                {
                    "name": "Supraja",
                    "email": "supraja@gmail.com"
                }
            ]
        }

        create_response = self.client.post(
            "/api/jobs/",
            data,
            format="json"
        )

        job_id = create_response.data["job_id"]

        response = self.client.get(
            f"/api/jobs/{job_id}/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["job_id"],
            job_id
        )

        self.assertEqual(
            response.data["total"],
            1
        )

        self.assertEqual(
            response.data["succeeded"],
            1
        )


    # TEST 5: Individual certificate failure


    def test_individual_certificate_failure(self):

        data = {
            "recipients": [
                {
                    "name": "Supraja",
                    "email": "supraja@gmail.com"
                },
                {
                    "name": "",
                    "email": "invalid"
                },
                {
                    "name": "Priya",
                    "email": "priya@gmail.com"
                }
            ]
        }

        response = self.client.post(
            "/api/jobs/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["total"],
            3
        )

        self.assertEqual(
            response.data["succeeded"],
            2
        )

        self.assertEqual(
            response.data["failed"],
            1
        )

        job = CertificateJob.objects.get(
            id=response.data["job_id"]
        )

        failed_certificate = job.certificates.get(
            status="failed"
        )

        self.assertTrue(
            failed_certificate.failure_reason
        )

        # Make sure valid recipients still succeeded
        successful_count = job.certificates.filter(
            status="success"
        ).count()

        self.assertEqual(
            successful_count,
            2
        )

    # TEST 6: Retrieving generated certificate


    def test_retrieve_generated_certificate(self):

        data = {
            "recipients": [
                {
                    "name": "Supraja",
                    "email": "supraja@gmail.com"
                }
            ]
        }

        create_response = self.client.post(
            "/api/jobs/",
            data,
            format="json"
        )

        job_id = create_response.data["job_id"]

        certificate = Certificate.objects.get(
            job_id=job_id
        )

        response = self.client.get(
            f"/api/certificates/"
            f"{certificate.id}/download/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response["Content-Type"],
            "application/pdf"
        )
