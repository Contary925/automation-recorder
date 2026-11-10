import csv
import qscript

INPUT_CSV = "input.csv"

def main():
    with open(INPUT_CSV, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(
            csv_file,
            delimiter=";",
            quotechar='"',
        )

        for row in reader:
            video_path = qscript.CaptureVideo_Magento(
                url=row["URL"],
                company_name=row["Company Name"],
                language=row["Language"],
                country=row["Country"],
                postcode=row["Postcode"],
                city=row["City"],
                street=row["Street"],
                house_no=row["HouseNo"],
            )

            if video_path:
                print(f"Saved video: {video_path}")
            else:
                print(f"Failed to record video for: {row['Company Name']}")

if __name__ == "__main__":
    main()