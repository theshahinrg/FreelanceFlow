from django.conf import settings


def project_identity(_request):
    """
    Adds project author and website details to every template context.
    """
    return {
        "PROJECT_AUTHOR": getattr(settings, "PROJECT_AUTHOR", "TheShahinRG"),
        "PROJECT_SITE": getattr(settings, "PROJECT_SITE", "shahindev.com"),
        "PROJECT_SITE_URL": getattr(
            settings,
            "PROJECT_SITE_URL",
            f"https://{getattr(settings, 'PROJECT_SITE', 'shahindev.com')}",
        ),
    }
