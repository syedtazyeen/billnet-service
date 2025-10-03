"""
Agents API v1 URLs
"""

from django.urls import path
from apps.agents.api.v1.views import (
    ConversationView,
    ConversationDetailView,
    MessageView,
)

CONVERSATION_ID = "<uuid:conversation_id>"

urlpatterns = [
    path("", ConversationView.as_view(), name="conversation-list-create"),
    path(
        CONVERSATION_ID,
        ConversationDetailView.as_view(),
        name="conversation-detail",
    ),
    path(
        f"{CONVERSATION_ID}/messages/",
        MessageView.as_view(),
        name="conversation-messages",
    ),
]

__all__ = ["urlpatterns"]
