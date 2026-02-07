from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
import pandas as pd
from .models import UploadSummary

# ... (Previous code)

class ReportView(APIView):
    def get(self, request):
        try:
            summary = UploadSummary.objects.order_by('-uploaded_at').first()
            if not summary:
                return Response({'error': 'No data available'}, status=status.HTTP_404_NOT_FOUND)

            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.setTitle(f"Report - {summary.file_name}")

            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, 750, "Chemical Equipment Parameter Report")
            
            p.setFont("Helvetica", 12)
            p.drawString(100, 730, f"File: {summary.file_name}")
            p.drawString(100, 715, f"Date: {summary.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")

            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, 680, "Summary Statistics")
            
            p.setFont("Helvetica", 12)
            p.drawString(120, 660, f"Total Equipment: {summary.total_equipment}")
            p.drawString(120, 645, f"Avg Flowrate: {summary.avg_flowrate}")
            p.drawString(120, 630, f"Avg Pressure: {summary.avg_pressure}")
            p.drawString(120, 615, f"Avg Temperature: {summary.avg_temperature}")

            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, 580, "Type Distribution")
            
            p.setFont("Helvetica", 12)
            y = 560
            # Check if type_distribution is dict (it should be)
            if isinstance(summary.type_distribution, dict):
                for type_name, count in summary.type_distribution.items():
                    p.drawString(120, y, f"{type_name}: {count}")
                    y -= 20
            else:
                 p.drawString(120, y, "No distribution data available")

            p.showPage()
            p.save()

            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{summary.id}.pdf"'
            return response
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UploadCSVView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.FILES['file']
        try:
            # Read CSV
            df = pd.read_csv(file_obj)
        except Exception as e:
            return Response({'error': f'Invalid CSV file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate Columns
        required_columns = {'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'}
        if not required_columns.issubset(df.columns):
            missing = ", ".join(required_columns - set(df.columns))
            return Response({'error': f'Missing columns: {missing}'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate Numeric Types
        for col in ['Flowrate', 'Pressure', 'Temperature']:
            try:
                # Attempt to convert to numeric, raising error if fails on any value
                # Note: 'coerce' produces NaNs, 'raise' raises error. 
                # If we want to catch non-numeric strings, 'raise' is good.
                pd.to_numeric(df[col], errors='raise') 
                # Ensure it's used as numeric in calculation
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                 return Response({'error': f'Column {col} must be numeric'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                 return Response({'error': f'Error processing column {col}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        if df.empty:
             return Response({'error': 'File is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Compute Statistics
        total_count = len(df)
        avg_flowrate = df['Flowrate'].mean()
        avg_pressure = df['Pressure'].mean()
        avg_temperature = df['Temperature'].mean()

        type_distribution = df['Type'].value_counts().to_dict()

        # Save summary to DB (logic in model handles keeping last 5)
        UploadSummary.objects.create(
            file_name=file_obj.name,
            total_equipment=total_count,
            avg_flowrate=avg_flowrate,
            avg_pressure=avg_pressure,
            avg_temperature=avg_temperature,
            type_distribution=type_distribution
        )

        # Return JSON response
        return Response({
            "total_count": int(total_count),
            "avg_flowrate": round(float(avg_flowrate), 2),
            "avg_pressure": round(float(avg_pressure), 2),
            "avg_temperature": round(float(avg_temperature), 2),
            "type_distribution": type_distribution
        }, status=status.HTTP_201_CREATED)

class HistoryView(APIView):
    def get(self, request):
        # Model logic ensures only last 5 exist, but we order by uploaded_at desc
        summaries = UploadSummary.objects.order_by('-uploaded_at')
        data = []
        for s in summaries:
            data.append({
                "file_name": s.file_name,
                "uploaded_at": s.uploaded_at,
                "total_equipment": s.total_equipment,
                "avg_flowrate": s.avg_flowrate,
                "avg_pressure": s.avg_pressure,
                "avg_temperature": s.avg_temperature
            })
        return Response(data)
