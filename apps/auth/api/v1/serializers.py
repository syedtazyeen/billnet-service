"""
Auth API v1 serializers
"""

from rest_framework import serializers
from apps.core.utils.identifier import is_valid_identifier


class IdentifierSerializer(serializers.Serializer):
    """
    Serializer for identifier.
    """

    identifier = serializers.CharField(required=True)

    def validate_identifier(self, value):
        """
        Validate the identifier.
        """
        if not is_valid_identifier(value):
            raise serializers.ValidationError(detail="Invalid identifier")
        return value


class SendCodeSerializer(IdentifierSerializer):
    """
    Serializer for sending a code to the user.
    """


class VerifyCodeSerializer(IdentifierSerializer):
    """
    Serializer for verifying a code.
    """

    request_id = serializers.CharField(required=True)
    code = serializers.CharField(required=True)


class RefreshTokenSerializer(serializers.Serializer):
    """
    Serializer for refresh token.
    """

    refresh = serializers.CharField(required=True)


__all__ = ["SendCodeSerializer", "VerifyCodeSerializer", "RefreshTokenSerializer"]
