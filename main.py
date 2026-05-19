"""
Human Typer Application
Purpose: A desktop application to select a target Windows window and simulate human-like typing of text.
Uses CustomTkinter for UI, win32gui for window management, and keyboard/pyautogui for input simulation.
"""
import time
import threading
import win32gui
import win32con
import win32api
import pyautogui
import keyboard
import customtkinter as ctk

# Configure CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class HumanTyperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Human Typer")
        self.geometry("850x650")
        
        # Internal state
        self.windows = []
        self.filtered_windows = []
        self.is_typing = False
        
        self.setup_ui()
        self.refresh_windows()
        
    def setup_ui(self):
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- 1. Window Selection Frame ---
        self.frame_top = ctk.CTkFrame(self)
        self.frame_top.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.frame_top.grid_columnconfigure(2, weight=1)
        
        self.lbl_window = ctk.CTkLabel(self.frame_top, text="Target Window:")
        self.lbl_window.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.entry_search = ctk.CTkEntry(self.frame_top, placeholder_text="Search window...", width=140)
        self.entry_search.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="ew")
        self.entry_search.bind("<KeyRelease>", self.filter_windows)
        
        self.combo_window = ctk.CTkComboBox(self.frame_top, values=["Loading..."], state="readonly", width=300)
        self.combo_window.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        self.btn_refresh = ctk.CTkButton(self.frame_top, text="Refresh", width=80, command=self.refresh_windows)
        self.btn_refresh.grid(row=0, column=3, padx=10, pady=10)

        self.btn_target = ctk.CTkButton(self.frame_top, text="🎯 Drag to Target", width=120, fg_color="#b35b00", hover_color="#8c4700")
        self.btn_target.grid(row=0, column=4, padx=10, pady=10)
        self.btn_target.bind("<ButtonPress-1>", self.start_target_drag)
        self.btn_target.bind("<ButtonRelease-1>", self.end_target_drag)

        # --- 2. Options Frame ---
        self.frame_options = ctk.CTkFrame(self)
        self.frame_options.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.lbl_speed = ctk.CTkLabel(self.frame_options, text="Speed (sec/char):")
        self.lbl_speed.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.entry_speed = ctk.CTkEntry(self.frame_options, width=60)
        self.entry_speed.insert(0, "0.05")
        self.entry_speed.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.lbl_delay = ctk.CTkLabel(self.frame_options, text="Start Delay (sec):")
        self.lbl_delay.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        self.entry_delay = ctk.CTkEntry(self.frame_options, width=60)
        self.entry_delay.insert(0, "2.0")
        self.entry_delay.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        self.lbl_engine = ctk.CTkLabel(self.frame_options, text="Typing Mode:")
        self.lbl_engine.grid(row=0, column=4, padx=10, pady=10, sticky="w")
        
        self.combo_engine = ctk.CTkComboBox(self.frame_options, values=["Standard (Keyboard)", "VNC/Remote (Alt-Codes)"], state="readonly", width=180)
        self.combo_engine.set("Standard (Keyboard)")
        self.combo_engine.grid(row=0, column=5, padx=10, pady=10, sticky="w")

        self.chk_enter_var = ctk.BooleanVar(value=False)
        self.chk_enter = ctk.CTkCheckBox(self.frame_options, text="Press 'Enter' at the end", variable=self.chk_enter_var)
        self.chk_enter.grid(row=1, column=0, columnspan=6, padx=10, pady=(0, 10), sticky="w")

        # --- 3. Text Area Tools ---
        self.frame_text_tools = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_text_tools.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        self.lbl_text = ctk.CTkLabel(self.frame_text_tools, text="Text to type:", font=("Arial", 14, "bold"))
        self.lbl_text.pack(side="left", padx=5)
        
        self.btn_clear = ctk.CTkButton(self.frame_text_tools, text="Clear", width=60, fg_color="#6c757d", hover_color="#5a6268", command=self.clear_text)
        self.btn_clear.pack(side="right", padx=5)
        
        self.btn_paste = ctk.CTkButton(self.frame_text_tools, text="Paste", width=60, command=self.paste_text)
        self.btn_paste.pack(side="right", padx=5)

        # --- 4. Text Area ---
        self.textbox = ctk.CTkTextbox(self, wrap="word", font=("Consolas", 14))
        self.textbox.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="nsew")
        self.textbox.insert("0.0", "Enter the text to be typed here...")
        
        # --- 5. Action Button ---
        self.btn_start = ctk.CTkButton(self, text="Start Typing (Cancel with ESC)", height=50, font=("Arial", 16, "bold"), command=self.start_typing_thread)
        self.btn_start.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")
        
    def clear_text(self):
        self.textbox.delete("0.0", "end")
        
    def paste_text(self):
        try:
            text = self.clipboard_get()
            self.textbox.insert("insert", text)
        except Exception:
            pass

    def get_window_list(self):
        windows = []
        def enum_windows_proc(hwnd, lParam):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowTextLength(hwnd) > 0:
                title = win32gui.GetWindowText(hwnd)
                windows.append((hwnd, title))
        win32gui.EnumWindows(enum_windows_proc, None)
        return windows

    def refresh_windows(self):
        self.windows = self.get_window_list()
        self.windows.sort(key=lambda x: x[1])
        self.filter_windows()
        
    def filter_windows(self, event=None):
        search_term = self.entry_search.get().lower()
        
        if search_term:
            self.filtered_windows = [w for w in self.windows if search_term in w[1].lower()]
        else:
            self.filtered_windows = self.windows
            
        titles = [f"{w[1]} (ID: {w[0]})" for w in self.filtered_windows]
        
        if titles:
            self.combo_window.configure(values=titles)
            self.combo_window.set(titles[0])
        else:
            self.combo_window.configure(values=["No windows found"])
            self.combo_window.set("No windows found")

    def start_target_drag(self, event):
        self.btn_target.configure(text="🎯 Targeting...", fg_color="#cc0000")
        self.config(cursor="crosshair")
        
    def end_target_drag(self, event):
        self.btn_target.configure(text="🎯 Drag to Target", fg_color="#b35b00")
        self.config(cursor="")
        
        # Get window at mouse cursor
        x, y = win32api.GetCursorPos()
        hwnd = win32gui.WindowFromPoint((x, y))
        root_hwnd = win32gui.GetAncestor(hwnd, win32con.GA_ROOT)
        
        title = win32gui.GetWindowText(root_hwnd)
        if title:
            window_str = f"{title} (ID: {root_hwnd})"
            
            # Ensure window is in our list
            if not any(w[0] == root_hwnd for w in self.windows):
                self.refresh_windows()
                
            self.entry_search.delete(0, "end")
            self.filter_windows()
            
            try:
                self.combo_window.set(window_str)
            except Exception:
                pass

    def get_selected_hwnd(self):
        selected = self.combo_window.get()
        for w in self.windows:
            title_str = f"{w[1]} (ID: {w[0]})"
            if title_str == selected:
                return w[0]
        return None

    def start_typing_thread(self):
        if self.is_typing:
            return
            
        text = self.textbox.get("0.0", "end")
        if text.endswith('\n'):
            text = text[:-1]
            
        if not text:
            return
            
        hwnd = self.get_selected_hwnd()
        if not hwnd:
            return
            
        try:
            speed = float(self.entry_speed.get())
            delay = float(self.entry_delay.get())
        except ValueError:
            speed = 0.05
            delay = 2.0
            
        self.is_typing = True
        self.btn_start.configure(text="Typing... (Cancel with ESC)", state="disabled", fg_color="red")
        
        auto_enter = self.chk_enter_var.get()
        mode = self.combo_engine.get()
        
        threading.Thread(target=self.type_text, args=(hwnd, text, speed, delay, auto_enter, mode), daemon=True).start()

    def type_text(self, hwnd, text, speed, delay, auto_enter, mode):
        try:
            pyautogui.press('alt')
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            
            time.sleep(delay)
            
            aborted = False
            for char in text:
                if keyboard.is_pressed('esc'):
                    print("Typing aborted.")
                    aborted = True
                    break
                
                if char == '\n':
                    keyboard.send('enter')
                elif char == '\t':
                    keyboard.send('tab')
                else:
                    if "VNC" in mode:
                        # VNC Mode: Use Numpad Alt-Codes for all non-alphanumeric chars to ensure they arrive correctly
                        if not char.isalnum() and char != ' ':
                            code = ord(char)
                            if code < 256:
                                pyautogui.keyDown('alt')
                                code_str = f"0{code}"
                                for digit in code_str:
                                    pyautogui.press(f'num{digit}')
                                pyautogui.keyUp('alt')
                            else:
                                keyboard.write(char) # Fallback for unicode > 255
                        else:
                            keyboard.write(char)
                    else:
                        # Standard Mode
                        if char == '|':
                            # Keep the specific pipe workaround just in case
                            pyautogui.keyDown('alt')
                            pyautogui.press(['num1', 'num2', 'num4'])
                            pyautogui.keyUp('alt')
                        else:
                            keyboard.write(char)
                
                time.sleep(speed)
                
            if not aborted and auto_enter:
                time.sleep(speed)
                keyboard.send('enter')
                
        except Exception as e:
            print(f"Error while typing: {e}")
            
        finally:
            self.is_typing = False
            self.after(0, self.reset_ui)
            
    def reset_ui(self):
        self.btn_start.configure(text="Start Typing (Cancel with ESC)", state="normal", fg_color=["#3a7ebf", "#1f538d"])

if __name__ == "__main__":
    app = HumanTyperApp()
    app.mainloop()
