import qrcode
import cv2
from pyzbar.pyzbar import decode
import csv
import os
import pyqrcode
import datetime

today = datetime.date.today().strftime("%Y-%m-%d")

# ---------------- Teacher + Class Selection ----------------
teacher = input("Enter teacher name: ").strip().lower()
class_name = input("Enter class name: ").strip().lower()

# Attendance CSV path
base_path = f"attendance/{teacher}/{class_name}"
os.makedirs(base_path, exist_ok=True)
filePath = f"{base_path}/{class_name}.csv"

# QR folder per class (outside attendance)
qr_folder = os.path.join("qrcodes", class_name)
os.makedirs(qr_folder, exist_ok=True)

# ---------------- Main Menu ----------------
a = input("Type 'attend' for Attendance OR 'reg' to Register new student: ")

# ---------------- Register Student ----------------
if a.lower() == "reg":
    name = input("Enter Name of Student: ").strip()
    regNo = input("Enter Registration No of student: ").strip()

    # Create CSV with headers if not exists
    if not os.path.exists(filePath):
        with open(filePath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["S.No", "Name", "Registration NO"])  # headers

    # Find next serial number
    with open(filePath, 'r') as file:
        rows = list(csv.reader(file))
        serial_no = len(rows)  # since first row is header

    # Write student details
    with open(filePath, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([serial_no, name, regNo])

    # Create QR Code
    data = f"name: {name} regNO: {regNo} class: {class_name}"
    url = pyqrcode.create(data)
    qr_file = os.path.join(qr_folder, f"{regNo}.png")
    url.png(qr_file, scale=8)

    print(f"Student registered and QR saved at {qr_file}")


# ---------------- Attendance Marking ----------------
elif a.lower() == "attend":
    regNo_input = input("Enter Registration Number of Student: ").strip()
    qrFile = os.path.join("qrcodes", class_name, f"{regNo_input}.png")

    try:
        image = cv2.imread(qrFile)

        if image is None:
            print(f"Error: Could not read image from {qrFile}")

        decoded_objects = decode(image)

        if decoded_objects:
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                regNo = qr_data.split("regNO: ")[1].split(" class:")[0]

                print(f"✅ QR Code Data: {qr_data}")

                # Read CSV data
                with open(filePath, 'r', newline='') as file:
                    reader = list(csv.DictReader(file))
                    headers = reader[0].keys() if reader else []

                # If today's column not exists → add it
                if today not in headers:
                    for row in reader:
                        row[today] = "A"  # default Absent
                    headers = list(headers) + [today]

                # Mark student as Present
                for row in reader:
                    if row["Registration NO"] == regNo:
                        row[today] = "P"

                # Rewrite CSV
                with open(filePath, 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(reader)

                print(f"✅ Attendance marked for {regNo}")

        else:
            print("No QR code found in the image.")

    except Exception as e:
        print(f"An error occurred: {e}")
