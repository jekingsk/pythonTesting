import qrcode
import cv2
from pyzbar.pyzbar import decode
import csv
import os
import pyqrcode
from datetime import date

a = input("type 'attend' for Attendance and 'reg' to register new student: ")

filePath = "attendence.csv"
today = date.today().strftime("%d-%m-%Y")   # column name for today's date

# ---------------- Register student ----------------
if a.lower() == "reg":
    name = input("Enter Name of Student: ")
    regNo = input("Enter Registration No of student: ")
    entData = [name, regNo]
    data = "name: " + name + " regNO: " + regNo

    if os.path.exists(filePath):
        with open(filePath, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(entData)
    else:
        # create file with headers
        new = ["Name", "Registration NO"]
        with open(filePath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new)
            writer.writerow(entData)

    # create QR code
    url = pyqrcode.create(data)
    url.png(f"{regNo}.png", scale=8)
    print("Student registered and QR generated ✅")

# ---------------- Attendance ----------------
elif a.lower() == "attend":
    qrFile = input("Enter Registration Number of Student: ") + ".png"
    qrFile = qrFile.strip()

    try:
        image = cv2.imread(qrFile)

        if image is None:
            print(f"Error: Could not read image from {qrFile}")
        else:
            decoded_objects = decode(image)

            if decoded_objects:
                for obj in decoded_objects:
                    regNo = obj.data.decode('utf-8').split("regNO: ")[1]
                    print(f"Scanned Registration No: {regNo}")

                    # Read existing CSV
                    with open(filePath, 'r', newline='') as file:
                        reader = list(csv.reader(file))

                    headers = reader[0]

                    # check if today's date column exists
                    if today not in headers:
                        headers.append(today)
                        date_col_index = len(headers) - 1

                        # mark "A" for all students by default
                        for row in reader[1:]:
                            while len(row) <= date_col_index:
                                row.append("")
                            row[date_col_index] = "A"
                    else:
                        date_col_index = headers.index(today)

                    # Mark "P" for the scanned student
                    for row in reader[1:]:
                        if row[1] == regNo:  # regNo column = index 1
                            while len(row) <= date_col_index:
                                row.append("")

                            # Only update if not already "P"
                            if row[date_col_index] != "P":
                                row[date_col_index] = "P"

                    # Save updated CSV
                    with open(filePath, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerows(reader)

                    print("Attendance updated ✅")

            else:
                print("No QR code found in the image.")

    except Exception as e:
        print(f"An error occurred: {e}")
