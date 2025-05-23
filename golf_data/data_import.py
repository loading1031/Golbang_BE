'''
MVP demo ver 0.0.2
2024.10.31
golf_data/data_import.py

역할: admin 페이지에 업로드한 엑셀 파일을 sql로 변환
'''
# golf_data/data_import.py

import pandas as pd
import requests
from io import BytesIO
from .models import GolfClub, GolfCourse, Tee

def import_excel_data(file_url):
    response = requests.get(file_url)
    response.raise_for_status()

    excel_file = BytesIO(response.content)

    # 각 시트를 데이터프레임으로 로드하고 `~` 값을 None으로 변환
    clubs_df = pd.read_excel(excel_file, sheet_name='Golf Clubs').replace('~', None)
    courses_df = pd.read_excel(excel_file, sheet_name='Golf Courses').replace('~', None)
    tees_df = pd.read_excel(excel_file, sheet_name='Tees').replace('~', None)

    # GolfClub 데이터를 데이터베이스에 저장
    for _, row in clubs_df.iterrows():
        print("import clubs")
        GolfClub.objects.update_or_create(
            club_name=row['Club Name'],
            defaults={
                'address': row['Address'] or '',
                'longitude': row.get('Longitude'),
                'latitude': row.get('Latitude')
            }
        )

    for _, row in courses_df.iterrows():
        print(f"import courses, {row}")
        club = GolfClub.objects.get(club_name=row['Club Name'])
        GolfCourse.objects.update_or_create(
            club=club,
            course_name=row['Course Name'],
            defaults={
                'holes': row['Holes'] or 0,
                'par': row['Par'] or 0
            }
        )

    # Tee 데이터를 데이터베이스에 저장
    for _, row in tees_df.iterrows():
        print(f"Processing Tee for Club Name: {row['Club Name']}, Course Name: {row['Course Name']}")

        # GolfCourse 확인
        try:
            course = GolfCourse.objects.get(club__club_name=row['Club Name'], course_name=row['Course Name'])
        except GolfCourse.DoesNotExist:
            print(f"GolfCourse not found for Club Name: {row['Club Name']}, Course Name: {row['Course Name']}")
            continue

        # Tee 데이터 업데이트 또는 생성
        tee, created = Tee.objects.update_or_create(
            course=course,
            tee_name=row['Tee Name'],
            defaults={**{
                f'hole_{i}_par': "0" if row.get(f'Hole{i} Par') in [None, '~', 'N/D'] else row.get(f'Hole{i} Par', "0")
                for i in range(1, 19)
            }, **{
                f'hole_{i}_handicap': "0" if row.get(f'Hole{i} Handicap') in [None, '~', 'N/D'] else row.get(
                    f'Hole{i} Handicap', "0")
                for i in range(1, 19)
            }}
        )

        if created:
            print(f"Created new Tee for Club Name: {row['Club Name']}, Course Name: {row['Course Name']}")
        else:
            print(f"Updated existing Tee for Club Name: {row['Club Name']}, Course Name: {row['Course Name']}")