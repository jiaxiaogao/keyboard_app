import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import keyboard
import threading
import time
import json
from datetime import datetime
import os


class KeyboardRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("键盘记录回放工具")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 记录状态变量
        self.is_recording = False
        self.is_playing = False
        self.recorded_events = []
        self.record_thread = None
        self.play_thread = None
        
        self.setup_ui()

        self.setup_shortcuts()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="键盘记录回放工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 记录控制区域
        record_frame = ttk.LabelFrame(main_frame, text="记录控制", padding="10")
        record_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.record_button = ttk.Button(record_frame, text="开始记录", 
                                       command=self.toggle_recording)
        self.record_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_record_button = ttk.Button(record_frame, text="按ESC停止记录", 
                                           command=self.stop_recording, state="disabled")
        self.stop_record_button.grid(row=0, column=1, padx=(0, 10))
        
        self.record_status = ttk.Label(record_frame, text="状态: 未记录", foreground="red")
        self.record_status.grid(row=0, column=2)
        
        # 回放控制区域
        play_frame = ttk.LabelFrame(main_frame, text="回放控制", padding="10")
        play_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(play_frame, text="回放次数:").grid(row=0, column=0, padx=(0, 5))
        
        self.replay_count = tk.StringVar(value="1")
        replay_count_spinbox = ttk.Spinbox(play_frame, from_=1, to=100, width=3,
                                    textvariable=self.replay_count)
        replay_count_spinbox.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(play_frame, text="回放速度:").grid(row=0, column=2, padx=(0, 5))
        
        self.replay_speed = tk.StringVar(value="1")
        replay_speed_spinbox = ttk.Spinbox(play_frame, from_=1, to=100, width=3,
                                    textvariable=self.replay_speed)
        replay_speed_spinbox.grid(row=0, column=3, padx=(0, 10))

        # ttk.Label(play_frame, text="档").grid(row=0, column=4, padx=(0, 5))
        
        self.play_button = ttk.Button(play_frame, text="开始回放", 
                                     command=self.start_playback)
        self.play_button.grid(row=0, column=5, padx=(0, 10))
        
        self.stop_play_button = ttk.Button(play_frame, text="停止回放", 
                                          command=self.stop_playback, state="disabled")
        self.stop_play_button.grid(row=0, column=6, padx=(0, 10))
        
        self.play_status = ttk.Label(play_frame, text="状态: 未回放", foreground="red")
        self.play_status.grid(row=0, column=7, padx=(20, 0))
        
        # 记录信息显示
        info_frame = ttk.LabelFrame(main_frame, text="记录信息", padding="10")
        info_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=8, width=70)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 文件操作区域
        file_frame = ttk.LabelFrame(main_frame, text="文件操作", padding="10")
        file_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="保存记录", command=self.save_recording).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(file_frame, text="加载记录", command=self.load_recording).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(file_frame, text="清空记录", command=self.clear_recording).grid(row=0, column=2)
        
        # 状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="就绪")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        print("setup_shortcuts called")
        # 使用keyboard库监听全局快捷键
        # keyboard.add_hotkey('ctrl+shift+r', self.toggle_recording)
        keyboard.add_hotkey('f9', self.start_playback)
        keyboard.add_hotkey('f10', self.stop_playback)
        # keyboard.add_hotkey('ctrl+shift+l', self.load_recording)
        # keyboard.add_hotkey('ctrl+shift+w', self.save_recording)
        # keyboard.add_hotkey('ctrl+shift+c', self.clear_recording)

    def toggle_recording(self):
        """开始或停止记录"""
        print("toggle_recording called")
        print(self.is_recording)

        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """开始记录键盘事件"""
        print("start_recording called")
        if self.is_playing:
            messagebox.showwarning("警告", "请先停止回放")
            return
            
        self.is_recording = True
        self.recorded_events = []
        
        # 更新UI
        self.record_button.config(state="disabled")
        self.stop_record_button.config(state="normal")
        self.record_status.config(text="状态: 记录中...", foreground="green")
        self.play_button.config(state="disabled")
        self.status_label.config(text="记录中... 按ESC键停止记录")
        
        # 在后台线程中记录
        self.record_thread = threading.Thread(target=self._record_thread)
        self.record_thread.daemon = True
        self.record_thread.start()
        
        self.update_info("开始记录键盘输入...\n")
    
    def _record_thread(self):
        """记录线程"""
        print("_record_thread called")
        try:
            # 开始记录，按ESC停止
            self.recorded_events = keyboard.record(until='esc')
            self.root.after(0, self._on_recording_finished)
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._on_recording_error(error_msg))
    
    def _on_recording_finished(self):
        """记录完成回调"""
        print("_on_recording_finished called")
        self.is_recording = False
        
        # 更新UI
        self.record_button.config(state="normal")
        self.stop_record_button.config(state="disabled")
        self.record_status.config(text="状态: 记录完成", foreground="blue")
        self.play_button.config(state="normal")
        self.status_label.config(text=f"记录完成！共记录 {len(self.recorded_events)} 个按键事件")
        
        # 显示记录信息
        self.update_info(f"记录完成！\n")
        self.update_info(f"总按键事件数: {len(self.recorded_events)}\n")
        
        # 分析记录内容
        key_counts = {}
        for event in self.recorded_events:
            if event.event_type == keyboard.KEY_DOWN:
                key_name = event.name
                key_counts[key_name] = key_counts.get(key_name, 0) + 1
        
        self.update_info("按键统计:\n")
        for key, count in key_counts.items():
            self.update_info(f"  {key}: {count}次\n")
    
    def _on_recording_error(self, error_msg):
        """记录错误回调"""
        print("_on_recording_error called")
        self.is_recording = False
        
        # 更新UI
        self.record_button.config(state="normal")
        self.stop_record_button.config(state="disabled")
        self.record_status.config(text="状态: 记录错误", foreground="red")
        self.play_button.config(state="normal")
        self.status_label.config(text=f"记录错误: {error_msg}")
        
        messagebox.showerror("记录错误", f"记录过程中发生错误:\n{error_msg}")
    
    def stop_recording(self):
        """停止记录"""
        print("stop_recording called")
        print(self.is_recording)


        if self.is_recording:
            # 模拟按下ESC键来停止记录
            try:
                # keyboard.send('esc') #send也不行，还是没反应
                # print("sent esc")

                # time.sleep(3) #延时一会，方便我切换到其他窗口来测试这个esc是否被按下（切换到win应用程序页面，能识别到esc）
                keyboard.press('esc') #经测试，这里esc确实是被按下了，电脑系统也识别到了，但是就是_record_thread中的record函数没有结束
                print("pressed esc")
                time.sleep(0.3)
                keyboard.release('esc')
                print("released esc")

                # time.sleep(3)
                # keyboard.write("test")
                # keyboard.press("ctrl")
                # keyboard.press('esc') #ctrl+esc == windows键 ——这里电脑是识别到了，但是监听线程没有识别到


                # time.sleep(2)
                # keyboard.press('esc') #按一次不行？多按几次？ ——还是不行，就是监听的线程没有捕捉到
                # print("pressed esc")
                # time.sleep(0.3)
                # keyboard.release('esc')
                # print("released esc")
            except Exception as e:
                print(f"停止记录时发生错误: {e}")
    
    def start_playback(self):
        """开始回放"""
        print("start_playback called")
        if not self.recorded_events:
            messagebox.showwarning("警告", "没有可回放的记录")
            return
            
        if self.is_recording:
            messagebox.showwarning("警告", "请先停止记录")
            return
            
        try:
            replay_count = int(self.replay_count.get())
            replay_speed = int(self.replay_speed.get())
            if replay_count <= 0:
                raise ValueError("回放次数必须大于0")
            if replay_speed <= 0 or replay_speed > 3:
                raise ValueError("回放速度只有1、2、3")
        except ValueError as e:
            messagebox.showerror("错误", f"{e}")
            return
        
        self.is_playing = True
        
        # 更新UI
        self.play_button.config(state="disabled")
        self.stop_play_button.config(state="normal")
        self.record_button.config(state="disabled")
        current_count = 0
        total_count = replay_count
        self.play_status.config(text=f"状态: 回放中 ({current_count}/{total_count})", foreground="green")
        self.status_label.config(text=f"开始回放，共 {replay_count} 次...")
        
        # 在后台线程中回放
        self.play_thread = threading.Thread(target=self._playback_thread, args=(replay_count, replay_speed,))
        self.play_thread.daemon = True
        self.play_thread.start()
    
    def _playback_thread(self, replay_count, replay_speed):
        """回放线程"""
        print("_playback_thread called")
        try:
            time.sleep(5)  # 等待5秒以便用户准备

            #每次回放前会检测一下is_playing状态，如果被设为False就停止回放，所以停止回放也是要等当前这一轮回放结束才真正停止
            user_stop_playback_flag = 0
            for i in range(replay_count):
                if not self.is_playing:
                    user_stop_playback_flag = 1 #表示是被用户停止的
                    break
                    
                current_iteration = i + 1
                # 更新回放状态
                self.root.after(0, lambda iter=current_iteration: self._update_playback_status(iter, replay_count))
                
                # 清除记录的时间戳
                t = 1.0
                t1 = 0.1 * (4 - replay_speed)  #根据回放速度调整时间间隔，速度档位越大，间隔越小，越快
                for my_event in self.recorded_events:
                    print(my_event)
                    print(my_event.time)
                    # print(my_event.scan_code)
                    # print(my_event.name)
                    # print(my_event.scan_code or my_event.name) 
                    # # or返回第一个非零参数，但是好像没有scan_code是0的情况啊？没搞懂
                    my_event.time = t  # 重置时间戳，避免时间间隔过大影响回放速度
                    t += t1 #重置时间间隔为t1秒
                    print(my_event.time)
                

                # 回放记录
                #第二个参数0表示以系统允许的最快速度回放，输入文本还行，录成绩就不行了，切换窗口反应不过来
                # keyboard.play(self.recorded_events, 0) 
                keyboard.play(self.recorded_events)
                
                # 等待0.3秒，间隔开多轮回放
                time.sleep(0.3)
            
            self.root.after(0, self._on_playback_finished(user_stop_playback_flag))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._on_playback_error(error_msg))
    
    def _update_playback_status(self, current, total):
        """更新回放状态"""
        print("_update_playback_status called")
        self.play_status.config(text=f"状态: 回放中 ({current}/{total})")
        self.status_label.config(text=f"回放第 {current}/{total} 次...")
    
    def _on_playback_finished(self, user_stop_playback_flag=0):
        """回放完成回调"""
        print("_on_playback_finished called")
        self.is_playing = False
        
        # 更新UI
        self.play_button.config(state="normal")
        self.stop_play_button.config(state="disabled")
        self.record_button.config(state="normal")
        self.play_status.config(text="状态: 回放完成", foreground="blue")
        self.status_label.config(text="回放完成！")

        if user_stop_playback_flag == 1:
            self.play_status.config(text="状态: 回放停止", foreground="red")
            self.status_label.config(text="回放已停止！")
            self.update_info("回放被用户停止！\n")
        else:
            self.update_info("回放完成！\n")
    
    def _on_playback_error(self, error_msg):
        """回放错误回调"""
        print("_on_playback_error called")
        self.is_playing = False
        
        # 更新UI
        self.play_button.config(state="normal")
        self.stop_play_button.config(state="disabled")
        self.record_button.config(state="normal")
        self.play_status.config(text="状态: 回放错误", foreground="red")
        self.status_label.config(text=f"回放错误: {error_msg}")
        
        messagebox.showerror("回放错误", f"回放过程中发生错误:\n{error_msg}")
    
    def stop_playback(self):
        """停止回放"""
        print("stop_playback called")
        self.is_playing = False
        self.status_label.config(text="回放已停止")
    
    def save_recording(self):
        """保存记录到文件"""
        print("save_recording called")
        if not self.recorded_events:
            messagebox.showwarning("警告", "没有可保存的记录")
            return
        print("recorded_events:(before saving)")
        print("--------------------")
        print(self.recorded_events)
        print("--------------------")
        try:
            # 转换为可序列化的格式
            events_data = []
            for event in self.recorded_events:
                events_data.append({
                    'name': event.name,
                    'event_type': event.event_type,
                    'scan_code': event.scan_code,
                    'time': event.time
                })
            
            filename = f"keyboard_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, indent=2)
            
            self.status_label.config(text=f"记录已保存到: {filename}")
            messagebox.showinfo("成功", f"记录已保存到: {filename}")
            
        except Exception as e:
            messagebox.showerror("保存错误", f"保存记录时发生错误:\n{e}")
    
    def load_recording(self):
        """从文件加载记录"""
        print("load_recording called")
        try:
            filename = filedialog.askopenfilename(
                title="选择记录文件",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not filename:
                return
                
            with open(filename, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
            
            # 转换回keyboard事件对象
            self.recorded_events = []
            for event_data in events_data:
                # # 创建类似keyboard事件的对象
                # class SimpleEvent:
                #     pass
                # event = SimpleEvent()
                # event.name = event_data['name']
                # event.event_type = event_data['event_type']
                # event.scan_code = event_data['scan_code']
                # event.time = event_data['time']

                # 直接创建keyboard.KeyboardEvent对象就行了，不用自己造个类SimpleEvent
                event = keyboard.KeyboardEvent(name = event_data['name'],
                                               event_type = event_data['event_type'],
                                               scan_code = event_data['scan_code'],
                                               time = event_data['time'])
                self.recorded_events.append(event)
            
            print("recorded_events:(after loading)")
            print("--------------------")
            print(self.recorded_events)
            print("--------------------")


            self.status_label.config(text=f"已加载记录: {os.path.basename(filename)}")
            self.update_info(f"已从文件加载记录: {filename}\n")
            self.update_info(f"加载了 {len(self.recorded_events)} 个按键事件\n")
            
            messagebox.showinfo("成功", f"记录加载成功！\n共加载 {len(self.recorded_events)} 个按键事件")
            
        except Exception as e:
            messagebox.showerror("加载错误", f"加载记录时发生错误:\n{e}")
    
    def clear_recording(self):
        """清空记录"""
        print("clear_recording called")
        if self.recorded_events and not self.is_recording and not self.is_playing:
            self.recorded_events = []
            self.info_text.delete(1.0, tk.END)
            self.status_label.config(text="记录已清空")
            self.record_status.config(text="状态: 未记录", foreground="red")
        else:
            messagebox.showwarning("警告", "无法清空记录：请先停止记录和回放")
    
    def update_info(self, message):
        """更新信息文本框"""
        print("update_info called")
        self.info_text.insert(tk.END, message)
        self.info_text.see(tk.END)
        self.root.update_idletasks()

def main():
    print("main called")
    root = tk.Tk()
    app = KeyboardRecorderApp(root)
    root.mainloop()
    print("end of main")

if __name__ == "__main__":
    main()