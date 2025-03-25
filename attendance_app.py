import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import pickle
import os
from datetime import datetime
import json

class SmartAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Attendance System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a2e")
        
        # Load Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Initialize face recognizer
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Data storage
        self.known_faces = {}  # {name: [face_images]}
        self.face_id_map = {}  # {id: name}
        self.attendance_records = {}
        self.video_capture = None
        self.is_running = False
        self.next_id = 0

        # IMPORTANT: build UI first so widgets like status_label exist before model training
        self.setup_ui()
        
        # Now load existing data and attendance (these may retrain the recognizer)
        self.load_data()
        self.load_attendance()
        
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#0f3460", height=80)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame, 
            text="🎯 Smart Attendance System",
            font=("Helvetica", 28, "bold"),
            bg="#0f3460",
            fg="#e94560"
        )
        title_label.pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg="#1a1a2e")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Video feed
        left_panel = tk.Frame(main_container, bg="#16213e", relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        video_label = tk.Label(
            left_panel,
            text="📹 Live Camera Feed",
            font=("Helvetica", 16, "bold"),
            bg="#16213e",
            fg="#e94560"
        )
        video_label.pack(pady=10)
        
        self.video_label = tk.Label(left_panel, bg="#000000")
        self.video_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Control buttons
        btn_frame = tk.Frame(left_panel, bg="#16213e")
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(
            btn_frame,
            text="▶ Start Camera",
            command=self.start_camera,
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹ Stop Camera",
            command=self.stop_camera,
            font=("Helvetica", 12, "bold"),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        # Right panel - Controls and records
        right_panel = tk.Frame(main_container, bg="#16213e", width=400, relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Registration section
        reg_label = tk.Label(
            right_panel,
            text="👤 Register New User",
            font=("Helvetica", 14, "bold"),
            bg="#16213e",
            fg="#e94560"
        )
        reg_label.pack(pady=10)
        
        name_frame = tk.Frame(right_panel, bg="#16213e")
        name_frame.pack(pady=5)
        
        tk.Label(
            name_frame,
            text="Name:",
            font=("Helvetica", 11),
            bg="#16213e",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        self.name_entry = tk.Entry(
            name_frame,
            font=("Helvetica", 11),
            width=20,
            bg="#0f3460",
            fg="white",
            insertbackground="white"
        )
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
        btn_container = tk.Frame(right_panel, bg="#16213e")
        btn_container.pack(pady=10)
        
        tk.Button(
            btn_container,
            text="📸 Upload Photo",
            command=self.register_face,
            font=("Helvetica", 11, "bold"),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_container,
            text="📷 Capture from Camera",
            command=self.capture_face,
            font=("Helvetica", 11, "bold"),
            bg="#9C27B0",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        # Registered users
        users_label = tk.Label(
            right_panel,
            text="👥 Registered Users",
            font=("Helvetica", 12, "bold"),
            bg="#16213e",
            fg="#e94560"
        )
        users_label.pack(pady=10)
        
        self.users_listbox = tk.Listbox(
            right_panel,
            font=("Helvetica", 10),
            bg="#0f3460",
            fg="white",
            height=5,
            selectbackground="#e94560"
        )
        self.users_listbox.pack(pady=5, padx=10, fill=tk.X)
        
        # Separator
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Attendance records
        records_label = tk.Label(
            right_panel,
            text="📊 Today's Attendance",
            font=("Helvetica", 14, "bold"),
            bg="#16213e",
            fg="#e94560"
        )
        records_label.pack(pady=10)
        
        # Treeview for attendance
        tree_frame = tk.Frame(right_panel, bg="#16213e")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Name", "Time"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=10
        )
        self.tree.heading("Name", text="Name")
        self.tree.heading("Time", text="Time")
        self.tree.column("Name", width=150)
        self.tree.column("Time", width=150)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Style for treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0f3460", foreground="white", fieldbackground="#0f3460")
        style.map("Treeview", background=[("selected", "#e94560")])
        
        # Export button
        tk.Button(
            right_panel,
            text="💾 Export Attendance",
            command=self.export_attendance,
            font=("Helvetica", 11, "bold"),
            bg="#FF9800",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(pady=10)
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready - OpenCV Face Recognition Loaded",
            font=("Helvetica", 10),
            bg="#0f3460",
            fg="white",
            anchor=tk.W,
            padx=10
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.update_displays()
    
    def load_data(self):
        if os.path.exists("face_data.pkl"):
            with open("face_data.pkl", "rb") as f:
                data = pickle.load(f)
                self.known_faces = data.get("faces", {})
                self.face_id_map = data.get("id_map", {})
                self.next_id = data.get("next_id", 0)
                
            # Retrain recognizer if data exists
            if self.known_faces:
                self.train_recognizer()
    
    def save_data(self):
        data = {
            "faces": self.known_faces,
            "id_map": self.face_id_map,
            "next_id": self.next_id
        }
        with open("face_data.pkl", "wb") as f:
            pickle.dump(data, f)
    
    def load_attendance(self):
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"attendance_{today}.json"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.attendance_records = json.load(f)
    
    def save_attendance(self):
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"attendance_{today}.json"
        with open(filename, "w") as f:
            json.dump(self.attendance_records, f, indent=4)
    
    def register_face(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name!")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if not file_path:
            return
        
        try:
            image = cv2.imread(file_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                messagebox.showerror("Error", "No face detected in the image!")
                return
            
            # Get the largest face
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (200, 200))
            
            # Store face data
            if name not in self.known_faces:
                self.known_faces[name] = []
                self.face_id_map[self.next_id] = name
                self.next_id += 1
            
            self.known_faces[name].append(face_img)
            self.save_data()
            self.train_recognizer()
            
            messagebox.showinfo("Success", f"{name} registered successfully!")
            self.name_entry.delete(0, tk.END)
            # Safe update of status_label
            if hasattr(self, "status_label"):
                self.status_label.config(text=f"✓ {name} registered successfully")
            self.update_displays()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register: {str(e)}")
    
    def capture_face(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name!")
            return
        
        # Open camera for capture
        cap = cv2.VideoCapture(0)
        messagebox.showinfo("Info", "Press SPACE to capture, ESC to cancel")
        
        captured = False
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            cv2.imshow('Capture Face - Press SPACE to capture', frame)
            
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE
                if len(faces) > 0:
                    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                    face_img = gray[y:y+h, x:x+w]
                    face_img = cv2.resize(face_img, (200, 200))
                    
                    if name not in self.known_faces:
                        self.known_faces[name] = []
                        self.face_id_map[self.next_id] = name
                        self.next_id += 1
                    
                    self.known_faces[name].append(face_img)
                    captured = True
                    break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if captured:
            self.save_data()
            self.train_recognizer()
            messagebox.showinfo("Success", f"{name} registered successfully!")
            self.name_entry.delete(0, tk.END)
            if hasattr(self, "status_label"):
                self.status_label.config(text=f"✓ {name} registered successfully")
            self.update_displays()
    
    def train_recognizer(self):
        faces = []
        labels = []
        
        for name, face_list in self.known_faces.items():
            # find id for this name (safe retrieval)
            ids = [k for k, v in self.face_id_map.items() if v == name]
            if not ids:
                continue
            face_id = ids[0]
            for face_img in face_list:
                faces.append(face_img)
                labels.append(face_id)
        
        if len(faces) > 0:
            try:
                self.recognizer.train(faces, np.array(labels))
                # Safe update of status_label (in case called before UI built)
                if hasattr(self, "status_label"):
                    self.status_label.config(text="✓ Model trained with registered faces")
            except Exception as e:
                # handle unexpected recognizer training errors
                if hasattr(self, "status_label"):
                    self.status_label.config(text=f"Model training failed: {e}")
                print("Recognizer training error:", e)
    
    def start_camera(self):
        if len(self.known_faces) == 0:
            messagebox.showwarning("Warning", "Please register at least one user first!")
            return
            
        self.video_capture = cv2.VideoCapture(0)
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        if hasattr(self, "status_label"):
            self.status_label.config(text="📹 Camera active - Detecting faces...")
        self.process_video()
    
    def stop_camera(self):
        self.is_running = False
        if self.video_capture:
            self.video_capture.release()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.video_label.config(image="")
        if hasattr(self, "status_label"):
            self.status_label.config(text="Camera stopped")
    
    def process_video(self):
        if not self.is_running:
            return
        
        ret, frame = self.video_capture.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))
                
                # Recognize face
                try:
                    label, confidence = self.recognizer.predict(face_img)
                except Exception:
                    label, confidence = -1, 9999
                name = "Unknown"
                
                # Lower confidence = better match (typical threshold: 50-100)
                if confidence < 70 and label in self.face_id_map:
                    name = self.face_id_map.get(label, "Unknown")
                    if name != "Unknown":
                        self.mark_attendance(name)
                
                # Draw rectangle and name
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.rectangle(frame, (x, y-35), (x+w, y), color, cv2.FILLED)
                
                text = f"{name} ({int(confidence)})" if name != "Unknown" and confidence < 1000 else "Unknown"
                cv2.putText(frame, text, (x+6, y-6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Convert to PhotoImage
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            try:
                img = img.resize((640, 480), Image.Resampling.LANCZOS)
            except Exception:
                img = img.resize((640, 480), Image.ANTIALIAS)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        self.root.after(10, self.process_video)
    
    def mark_attendance(self, name):
        today = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if name not in self.attendance_records:
            self.attendance_records[name] = current_time
            self.save_attendance()
            self.update_displays()
            if hasattr(self, "status_label"):
                self.status_label.config(text=f"✓ Attendance marked for {name} at {current_time}")
    
    def update_displays(self):
        # Update users list
        self.users_listbox.delete(0, tk.END)
        for name in sorted(self.known_faces.keys()):
            self.users_listbox.insert(tk.END, f"👤 {name}")
        
        # Update attendance tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for name, time in self.attendance_records.items():
            self.tree.insert("", tk.END, values=(name, time))
    
    def export_attendance(self):
        if not self.attendance_records:
            messagebox.showinfo("Info", "No attendance records to export!")
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"attendance_report_{today}.txt"
        
        with open(filename, "w") as f:
            f.write(f"ATTENDANCE REPORT\n")
            f.write(f"Date: {today}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Present: {len(self.attendance_records)}\n")
            f.write(f"Total Registered: {len(self.known_faces)}\n\n")
            f.write("=" * 60 + "\n")
            f.write(f"{'Name':<30} {'Time':<15}\n")
            f.write("=" * 60 + "\n")
            for name, time in sorted(self.attendance_records.items()):
                f.write(f"{name:<30} {time:<15}\n")
            f.write("=" * 60 + "\n")
        
        messagebox.showinfo("Success", f"Attendance exported to {filename}")
        if hasattr(self, "status_label"):
            self.status_label.config(text=f"✓ Exported to {filename}")
    
    def __del__(self):
        if self.video_capture:
            self.video_capture.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartAttendanceSystem(root)
    root.mainloop()
