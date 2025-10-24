from io import BytesIO
from django.http import HttpResponse
from rest_framework.views import APIView

from usersystem.permissions import ActiveUserPermission

from .serializer import ExportTableSerializer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


import pandas as pd

class ExportExcelView(APIView):
    permission_classes = [ActiveUserPermission]

    def post(self, request):
        ser = ExportTableSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        title = ser.validated_data['title']
        data  = ser.validated_data['data']

        columns = list(data.keys())
        if 'index' in columns:
            columns.remove('index')
            columns = ['index'] + columns

        df = pd.DataFrame({col: data[col] for col in columns})

        bio = BytesIO()
        with pd.ExcelWriter(bio, engine='openpyxl') as writer:
            sheet_name = 'Sheet1'
            df.to_excel(writer, index=False, sheet_name=sheet_name, startrow=1)

            ws = writer.sheets[sheet_name]
            max_col = df.shape[1]
            from openpyxl.styles import Alignment, Font
            ws.merge_cells(
                start_row=1,
                start_column=1,
                end_row=1,
                end_column=max_col if max_col else 1,
            )
            cell = ws.cell(row=1, column=1, value=title)
            cell.font = Font(size=14, bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')

            for idx, col in enumerate(df.columns, start=1):
                value_lengths = [len(str(x)) if x is not None else 0 for x in df[col]]
                max_len = max(value_lengths + [len(col), 4])
                ws.column_dimensions[chr(64 + idx)].width = min(max_len + 2, 60)

        bio.seek(0)
        filename = f"{title}.xlsx".replace('/', '_')
        resp = HttpResponse(
            bio.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp


class ExportPDFView(APIView):
    permission_classes = [ActiveUserPermission]
    def post(self, request):
        ser = ExportTableSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        title = ser.validated_data['title']
        data  = ser.validated_data['data']

        # Arrange columns (index first if exists)
        columns = list(data.keys())
        if 'index' in columns:
            columns.remove('index')
            columns = ['index'] + columns

        header = columns
        rows = []
        num_rows = len(next(iter(data.values())))
        for i in range(num_rows):
            rows.append([str(data[col][i]) if i < len(data[col]) else '' for col in columns])

        # Setup landscape A4
        pagesize = landscape(A4)
        bio = BytesIO()
        doc = SimpleDocTemplate(
            bio,
            pagesize=pagesize,
            leftMargin=24,
            rightMargin=24,
            topMargin=28,
            bottomMargin=24,
        )

        # Use default English style
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        title_style.fontName = 'Times-Roman'  # Use Times New Roman
        story = [Paragraph(title, title_style), Spacer(1, 12)]

        # Build table
        table_data = [header] + rows
        tbl = Table(table_data, repeatRows=1)
        tbl.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),  # header bold
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F7FA')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#303133')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#D7D7D7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FAFAFA')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(tbl)
        doc.build(story)
        bio.seek(0)

        filename = f"{title}.pdf".replace('/', '_')
        resp = HttpResponse(bio.getvalue(), content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp
