# Smart-Attendance-System
 This includes facial recognition, real-time processing, and attendance management.
 
📌 Smart Attendance System
A modern, powerful, and user-friendly Face Recognition Attendance Management system built using Python, OpenCV, LBPH, and Tkinter.
The app allows users to register faces, capture faces via webcam, auto-mark attendance, and export daily reports — all inside a clean desktop dashboard.

🚀 Features
✅ Face Registration

Upload image from device
OR capture face directly from webcam
Detects face using Haar Cascade
Stores multiple face samples per user
Automatically retrains the model

🎥 Live Camera Recognition
Real-time face detection
LBPH face recognition
Auto-attendance marking
Confidence score display
Recognizes multiple users

📊 Attendance Management
Automatically stores daily attendance
Displays today's recorded attendance
Exports attendance reports as .txt
Tracks timestamp (HH:MM:SS)

🗂 Data Persistence
Face data saved in face_data.pkl
Daily attendance saved in attendance_YYYY-MM-DD.json

🖥 Modern Tkinter Interface
Dark themed elegant UI
Live video feed preview
Registration panel
Attendance viewer
Status bar notifications

🛠 Tech Stack Used
Component	Technology
GUI	Tkinter
Face Detection	Haar Cascade
Face Recognition	LBPH (OpenCV)
Storage	Pickle, JSON
Image Processing	OpenCV, Pillow
Programming Language	Python 3
📦 Project Structure
Smart-Attendance-System/
│
├── attendance_app.py
├── face_data.pkl
├── attendance_2025-03-25.json
├── README.md
└── requirements.txt (optional)

🔧 How It Works
1️⃣ Register User
Enter a name
Upload photo or capture from webcam
System extracts and stores face samples
LBPH model retrains automatically

2️⃣ Start Camera
Recognizes registered users live
Displays name + confidence score
Marks attendance once per day

3️⃣ View Attendance
Shows all users present today
Displays time of detection

4️⃣ Export Report
Exports a formatted report:

ATTENDANCE REPORT
Date: YYYY-MM-DD
--------------------------------------------
Total Present: X
Total Registered: Y
--------------------------------------------
Name                           Time
--------------------------------------------
Person 1                       09:30:12
Person 2                       10:11:55

📥 Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/HrithikWadile/Smart-Attendance-System.git
cd Smart-Attendance-System

2️⃣ Install dependencies
pip install opencv-python opencv-contrib-python pillow numpy

3️⃣ Run the app
python attendance_app.py

📷 Screenshots
<img width="1472" height="1000" alt="image" src="https://github.com/user-attachments/assets/f5fe4f72-795d-4007-ad8d-edb29e2d618b" />


🧠 Future Enhancements
Add CSV / Excel export
Add GUI theme switcher
Add user deletion feature
Add student profile panel
Add admin login system

❤️ Contributions
Feel free to contribute! Fork this repo → improve → submit a PR.

📄 License
This project is open-source and available under the MIT License.
