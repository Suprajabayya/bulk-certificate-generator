from rest_framework import serializers


class RecipientSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=100
    )

    email = serializers.EmailField(
        required=True
    )