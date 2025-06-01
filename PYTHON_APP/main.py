import tkinter as tk
from tkinter import messagebox
from crud import update_activity
from crud import delete_activity
from account import register_user, login_user
from account import ensure_admin_exists
from crud import write_activity, get_all_activities, get_user_activities
import uuid
from tkcalendar import DateEntry
from thoitiet import fetch_weather_data
import requests
import datetime

class DailyApp:
    def __init__(self, root):
        ensure_admin_exists()
        self.root = root
        self.root.title("Ứng dụng Quản lý Sinh hoạt Hằng ngày")
        self.root.geometry("500x400")
        
        self.create_widgets()
        self.current_user = None
        self.current_role = None
        

    def create_widgets(self):
        title = tk.Label(self.root, text="Chào mừng đến với Ứng dụng Quản lý Sinh hoạt", font=("Arial", 14))
        title.pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        self.btn_add = tk.Button(btn_frame, text="➕ Thêm mới", width=20, command=self.add_activity)
        self.btn_view = tk.Button(btn_frame, text="📄 Xem dữ liệu", width=20, command=self.view_activities)
        self.btn_edit = tk.Button(btn_frame, text="✏️ Sửa dữ liệu", width=20, command=self.edit_activity)
        self.btn_delete = tk.Button(btn_frame, text="🗑️ Xoá dữ liệu", width=20, command=self.delete_activity)
        
        self.btn_login = tk.Button(btn_frame, text="🔐 Đăng nhập", width=20, command=self.login_user)
        self.btn_logout = tk.Button(btn_frame, text="🚪 Đăng xuất", width=20, command=self.logout_user)
        

        
        self.hide_all_function_buttons()
        self.btn_login.pack(pady=5)
    
    def hide_all_function_buttons(self):
        for btn in (self.btn_add, self.btn_view, self.btn_edit, self.btn_delete, self.btn_logout):
            btn.pack_forget()
        
    def update_ui_permissions(self):
        self.hide_all_function_buttons()
        
        self.btn_logout.pack(pady=5)
        self.btn_add.pack(pady=5)
        self.btn_view.pack(pady=5)
        
        if self.current_role == "admin":
            self.btn_edit.pack(pady=5)
            self.btn_delete.pack(pady=5)



   
    def add_activity(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Thêm hoạt động")
        add_window.geometry("400x400")
    
        tk.Label(add_window, text="Tên hoạt động:").pack(pady=5)
        entry_title = tk.Entry(add_window, width=40)
        entry_title.pack()
    
        tk.Label(add_window, text="Chọn ngày:").pack(pady=5)
        date_entry = DateEntry(add_window, date_pattern="yyyy-mm-dd")
        date_entry.pack()
    
        tk.Label(add_window, text="Thời gian (ví dụ: 14:00):").pack(pady=5)
        entry_time = tk.Entry(add_window, width=40)
        entry_time.pack()
    
        tk.Label(add_window, text="Ghi chú:").pack(pady=5)
        entry_notes = tk.Entry(add_window, width=40)
        entry_notes.pack()
    
        def submit():
            title = entry_title.get().strip()
            date = date_entry.get_date().strftime("%Y-%m-%d")
            time = entry_time.get().strip()
            notes = entry_notes.get().strip()
    
            if not title or not time:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ tên hoạt động và thời gian.")
                return
    
            activity_id = str(uuid.uuid4())
            write_activity(self.current_user, date, title, time, notes, activity_id)
            messagebox.showinfo("Thành công", "Đã thêm hoạt động.")
            add_window.destroy()
    
        tk.Button(add_window, text="Thêm", command=submit).pack(pady=10)





    def view_activities(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Danh sách hoạt động")
        view_window.geometry("550x500")

        if self.current_role == "admin":
            data = get_all_activities()
        else:
            data = get_user_activities(self.current_user)
    
        if not data:
            tk.Label(view_window, text="Không có dữ liệu nào.").pack(pady=10)
            return
    
        canvas = tk.Canvas(view_window)
        scrollbar = tk.Scrollbar(view_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for act in data:
            frame = tk.Frame(scrollable_frame, bd=1, relief="solid", padx=5, pady=5)
            frame.pack(fill="x", padx=10, pady=5)

            msg = (
                f"📝 {act.get('title', '')}\n"
                f"📅 {act['date']} | ⏰ {act.get('time', '')}\n"
                f"👤 {act['username']}\n"
                f"🗒️ Nội dung: {act.get('notes', '')}"
            )
            lbl = tk.Label(frame, text=msg, anchor="w", justify="left")
            lbl.pack(side="left", fill="x", expand=True)

            btn_weather = tk.Button(frame, text="🌤️ Xem thời tiết", command=lambda a=act: self.view_weather(a))
            btn_weather.pack(side="right", padx=5, pady=5)

    def view_weather(self, activity):
        date_str = activity.get("date", "")
        time_str = activity.get("time", "").strip()

        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Lỗi", f"Ngày không hợp lệ: {date_str}")
            return

        hour = None
        if time_str:
            try:
                hour = int(time_str.split(":")[0])
                if not (0 <= hour <= 23):
                    raise ValueError()
            except:
                hour = None
       
        latitude= 10.8231
        longitude= 106.6297

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date_obj.strftime("%Y-%m-%d"),
            "end_date": date_obj.strftime("%Y-%m-%d"),
            "hourly": "temperature_2m,relativehumidity_2m,precipitation",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "Asia/Ho_Chi_Minh"

        }

        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            messagebox.showerror("Lỗi", f"Không thể lấy dữ liệu thời tiết:\n{e}")
            return

        info_date = date_obj.strftime("%Y-%m-%d")
        info_time = "Không có dữ liệu giờ cụ thể"
        info_temp = ""
        info_humidity = ""
        info_rain = ""

        if hour is not None:
            target_time_str = f"{info_date}T{hour:02d}:00"
            times = data.get("hourly", {}).get("time", [])
            try:
                idx = times.index(target_time_str)
                temp = data["hourly"]["temperature_2m"][idx]
                humidity = data["hourly"]["relativehumidity_2m"][idx]
                precipitation = data["hourly"]["precipitation"][idx]

                info_time = f"{hour:02d}:00"
                info_temp = f"{temp}°C"
                info_humidity = f"{humidity}%"
                info_rain = "Có mưa" if precipitation > 0 else "Không mưa"
            except ValueError:
                hour = None

        if hour is None:
            daily = data.get("daily", {})
            try:
                temp_max = daily["temperature_2m_max"][0]
                temp_min = daily["temperature_2m_min"][0]
                rain_sum = daily["precipitation_sum"][0]

                info_time = "Dữ liệu cả ngày"
                info_temp = f"T_max: {temp_max}°C | T_min: {temp_min}°C"
                info_humidity = "Không có dữ liệu độ ẩm cả ngày"
                info_rain = "Có mưa" if rain_sum > 0 else "Không mưa"
            except (IndexError, KeyError):
                messagebox.showerror("Lỗi", "Không có dữ liệu thời tiết cho ngày này.")
                return

        msg = (
            f"📅 Ngày: {info_date}\n"
            f"⏰ Giờ: {info_time}\n"
            f"🌡️ Nhiệt độ: {info_temp}\n"
            f"💧 Độ ẩm: {info_humidity}\n"
            f"☔️ Dự báo mưa: {info_rain}"
        )
        messagebox.showinfo("Thông tin Thời tiết", msg)


 
    def edit_activity(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Sửa hoạt động")
        edit_window.geometry("400x400")
    
        activities = get_all_activities()
        tk.Label(edit_window, text="Chọn hoạt động:").pack()
    
        var = tk.StringVar()
        choices = [f"{act['id']}: {act.get('title', '')}" for act in activities]
        if not choices:
            tk.Label(edit_window, text="Không có hoạt động để sửa.").pack()
            return
    
        var.set(choices[0])
        option_menu = tk.OptionMenu(edit_window, var, *choices)
        option_menu.pack(pady=10)
    
        tk.Label(edit_window, text="Tên hoạt động mới:").pack()
        entry_title = tk.Entry(edit_window, width=40)
        entry_title.pack()
    
        tk.Label(edit_window, text="Ngày mới (yyyy-mm-dd):").pack()
        entry_date = tk.Entry(edit_window, width=40)
        entry_date.pack()
    
        tk.Label(edit_window, text="Thời gian mới:").pack()
        entry_time = tk.Entry(edit_window, width=40)
        entry_time.pack()
    
        tk.Label(edit_window, text="Ghi chú mới:").pack()
        entry_notes = tk.Entry(edit_window, width=40)
        entry_notes.pack()
    
        def submit():
            selected_id = var.get().split(":")[0]
            new_title = entry_title.get().strip()
            new_date = entry_date.get().strip()
            new_time = entry_time.get().strip()
            new_notes = entry_notes.get().strip()
    
            if not new_title or not new_date or not new_time:
                messagebox.showerror("Lỗi", "Điền đầy đủ thông tin.")
                return
    
            new_data = {
                "title": new_title,
                "date": new_date,
                "time": new_time,
                "notes": new_notes
            }
    
            try:
                update_activity(selected_id, new_data)
                messagebox.showinfo("Thành công", "Đã cập nhật hoạt động.")
                edit_window.destroy()
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e))
    
        tk.Button(edit_window, text="Cập nhật", command=submit).pack(pady=10)




    def delete_activity(self):
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Xoá hoạt động")
        delete_window.geometry("400x250")
    
        activities = get_all_activities()
    
        if not activities:
            tk.Label(delete_window, text="Không có hoạt động nào để xoá.").pack(pady=10)
            return
    
        choices = [
            f"{act['id']}: {act.get('title', act.get('content', ''))} - {act['date']}"
            for act in activities
            if 'id' in act
        ]
    
        if not choices:
            tk.Label(delete_window, text="Không có hoạt động hợp lệ để xoá.").pack(pady=10)
            return
    
        tk.Label(delete_window, text="Chọn hoạt động để xoá:").pack(pady=5)
    
        var = tk.StringVar()
        var.set(choices[0])
    
        option_menu = tk.OptionMenu(delete_window, var, *choices)
        option_menu.pack(pady=10)
    
        def confirm_delete():
            selected_id = var.get().split(":")[0]
            try:
                delete_activity(selected_id)
                messagebox.showinfo("Đã xoá", "Hoạt động đã được xoá.")
                delete_window.destroy()
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e))
    
        tk.Button(delete_window, text="Xoá", command=confirm_delete).pack(pady=10)

    def update_weather(self):
        fetch_weather_data()
        messagebox.showinfo("Thông báo", "Đã cập nhật dữ liệu thời tiết thành công!")


    def login_user(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Đăng nhập")
        login_window.geometry("300x200")
    
        tk.Label(login_window, text="Tên người dùng:").pack()
        entry_user = tk.Entry(login_window)
        entry_user.pack()
    
        tk.Label(login_window, text="Mật khẩu:").pack()
        entry_pass = tk.Entry(login_window, show="*")
        entry_pass.pack()
    
        def submit_login():
            user = entry_user.get()
            pw = entry_pass.get()
            success, role = login_user(user, pw)
            if success:
                messagebox.showinfo("Thành công", f"Đăng nhập thành công với vai trò: {role}")
                self.current_user = user
                self.current_role = role
                login_window.destroy()
                
                self.btn_login.pack_forget()
                self.update_ui_permissions()
                
                if self.current_role == "admin":
                    self.btn_edit.pack(pady=5)
                    self.btn_delete.pack(pady=5)

        
            else:
                messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu.")
                
        tk.Button(login_window, text="Đăng nhập", command=submit_login).pack(pady=10)
        tk.Button(login_window, text="Chưa có tài khoản? Đăng ký", command=self.register_user).pack()
    
    def register_user(self):
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Đăng ký")
        reg_window.geometry("300x220")
    
        tk.Label(reg_window, text="Tên người dùng:").pack()
        entry_user = tk.Entry(reg_window)
        entry_user.pack()
    
        tk.Label(reg_window, text="Mật khẩu:").pack()
        entry_pass = tk.Entry(reg_window, show="*")
        entry_pass.pack()
    
        tk.Label(reg_window, text="Vai trò (admin/user):").pack()
        entry_role = tk.Entry(reg_window)
        entry_role.insert(0, "user")
        entry_role.pack()
    
        def submit_register():
            user = entry_user.get()
            pw = entry_pass.get()
            role = entry_role.get()
            success, msg = register_user(user, pw, role)
            if success:
                messagebox.showinfo("Thành công", msg)
                reg_window.destroy()
            else:
                messagebox.showerror("Lỗi", msg)
    
        tk.Button(reg_window, text="Đăng ký", command=submit_register).pack(pady=10)
        
    def logout_user(self):
        self.current_user = None
        self.current_role = None
    
        self.hide_all_function_buttons()
        self.btn_login.pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = DailyApp(root)
    root.mainloop()
