"""apps/users/models.py — Custom User + Profiles"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'CLIENT', _('Client')
        PANDIT = 'PANDIT', _('Pandit')
        ADMIN  = 'ADMIN',  _('Admin')

    role  = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # Override email to make it required and unique
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.role})"

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_pandit(self):
        return self.role == self.Role.PANDIT

    @property
    def is_site_admin(self):
        return self.role == self.Role.ADMIN


class PanditProfile(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'PENDING',   _('Pending Approval')
        APPROVED  = 'APPROVED',  _('Approved')
        REJECTED  = 'REJECTED',  _('Rejected')
        SUSPENDED = 'SUSPENDED', _('Suspended')

    user               = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pandit_profile')
    city               = models.ForeignKey('core.City', on_delete=models.SET_NULL, null=True, blank=True)
    experience_years   = models.PositiveIntegerField(default=0)
    specializations    = models.ManyToManyField('core.PujaCategory', blank=True, related_name='pandits')
    languages          = models.CharField(max_length=200, default='Hindi', help_text='Comma separated: Hindi, Gujarati')
    base_price         = models.DecimalField(max_digits=8, decimal_places=2, default=1500.00)
    id_proof           = models.FileField(upload_to='id_proofs/', null=True, blank=True)
    bank_account_name  = models.CharField(max_length=100, blank=True)
    bank_account_number= models.CharField(max_length=20, blank=True)
    ifsc_code          = models.CharField(max_length=15, blank=True)
    status             = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                             help_text='Override global commission. Leave blank to use global.')
    average_rating     = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_bookings     = models.PositiveIntegerField(default=0)
    bio                = models.TextField(blank=True)
    slug               = models.SlugField(unique=True, blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pandit Profile'

    def __str__(self):
        return f"Pt. {self.user.get_full_name()} — {self.city}"

    def get_commission(self):
        from django.conf import settings
        if self.commission_percent is not None:
            return self.commission_percent
        return settings.GLOBAL_COMMISSION_PERCENT

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base = slugify(self.user.get_full_name() or self.user.email.split('@')[0])
            slug = base
            counter = 1
            while PanditProfile.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ClientProfile(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    saved_address = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Client Profile'

    def __str__(self):
        return f"Client: {self.user.get_full_name() or self.user.email}"
