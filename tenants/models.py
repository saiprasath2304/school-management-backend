# ─────────────────────────────────────────────────────────────────
# tenants/models.py  — The School (tenant) root model
# ─────────────────────────────────────────────────────────────────
from django.db import models


class School(models.Model):
    """
    Each School is an isolated tenant.
    All data in the system is scoped to a School.
    """
    class Plan(models.TextChoices):
        TRIAL   = "trial",   "Free Trial"
        BASIC   = "basic",   "Basic"
        PREMIUM = "premium", "Premium"

    # Identity
    name      = models.CharField(max_length=200)
    subdomain = models.SlugField(
        max_length=100, unique=True,
        help_text="Unique slug, e.g. 'greenfield' → greenfield.eduverse.com"
    )

    # Contact
    address   = models.TextField(blank=True)
    phone     = models.CharField(max_length=30, blank=True)
    email     = models.EmailField(blank=True)
    website   = models.URLField(blank=True)

    # Branding
    logo      = models.ImageField(upload_to="school_logos/", null=True, blank=True)
    tagline   = models.CharField(max_length=200, blank=True)

    # Locale
    country   = models.CharField(max_length=100, default="Kenya")
    currency  = models.CharField(max_length=10, default="KES",
                                  help_text="ISO currency: KES, NGN, GHS, UGX…")
    timezone  = models.CharField(max_length=50, default="Africa/Nairobi")

    # Subscription
    plan          = models.CharField(max_length=10, choices=Plan.choices, default=Plan.TRIAL)
    is_active     = models.BooleanField(default=True)
    trial_ends_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.subdomain})"

    @property
    def api_base(self):
        return f"https://{self.subdomain}.eduverse.com/api"
