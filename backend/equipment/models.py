from django.db import models

class UploadSummary(models.Model):
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_equipment = models.IntegerField()
    avg_flowrate = models.FloatField()
    avg_pressure = models.FloatField()
    avg_temperature = models.FloatField()
    type_distribution = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Keep only last 5 uploads
        # We fetch the IDs of the newest 5 records
        keep_ids = list(UploadSummary.objects.order_by('-uploaded_at').values_list('id', flat=True)[:5])
        # Delete any records that are not in the top 5
        if keep_ids:
            UploadSummary.objects.exclude(id__in=keep_ids).delete()

    def __str__(self):
        return f"{self.file_name} ({self.uploaded_at})"
