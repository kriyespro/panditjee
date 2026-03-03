from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='review')
    pandit = models.ForeignKey('users.PanditProfile', on_delete=models.CASCADE, related_name='reviews')
    client = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='given_reviews')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ by {self.client.first_name} for {self.pandit.user.first_name}"
