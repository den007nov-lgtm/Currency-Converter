# coding=utf-8
#######################################################
# Программа Training Planner (Планировщик тренировок)
# python 3.x
# Автор: Денис Новокщенов / sgiman, 2026
#######################################################

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import json
import os
from datetime import datetime

#================================
#  К Л А С С Ы
#================================
class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title('Training Planner - Планировщик тренировок')
        self.root.geometry("800x600+400+200")
        self.root.resizable(True, True)
        
        # Иконка (если файл существует)
        try:
            self.root.iconbitmap('training.ico')
        except:
            pass
        
        # Типы тренировок
        self.training_types = [
            "Кардио", "Силовая", "Йога", "Пилатес", 
            "Растяжка", "Плаванье", "Велоспорт", "Бег", "Другое"
        ]
        
        self.data_file = "trainings.json"
        self.trainings = []  # Список тренировок
        
        # Загрузка данных при старте
        self.load_trainings()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.update_table()
        
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        
        #================================
        #  ВЕРХНЯЯ ПАНЕЛЬ (ДОБАВЛЕНИЕ)
        #================================
        input_frame = LabelFrame(self.root, text="Добавить тренировку", 
                                 font="Arial 10 bold", padx=10, pady=10)
        input_frame.pack(fill=X, padx=10, pady=5)
        
        # Дата (ряд 0)
        Label(input_frame, text="Дата:", font="Arial 10").grid(row=0, column=0, sticky=W, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=20, font="Arial 10")
        self.date_entry.grid(row=0, column=1, padx=10, pady=5, sticky=W)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Подсказка по формату даты
        date_hint = Label(input_frame, text="(YYYY-MM-DD)", font="Arial 8", fg="gray")
        date_hint.grid(row=0, column=2, sticky=W)
        
        # Привязываем валидацию даты
        date_vcmd = (self.root.register(self.validate_date_input), '%P')
        self.date_entry.config(validate="key", validatecommand=date_vcmd)
        
        # Тип тренировки (ряд 1)
        Label(input_frame, text="Тип тренировки:", font="Arial 10").grid(row=1, column=0, sticky=W, pady=5)
        self.training_type = StringVar()
        self.training_type.set(self.training_types[0])
        
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.training_type,
                                       values=self.training_types, state="readonly", width=20)
        self.type_combo.grid(row=1, column=1, padx=10, pady=5, sticky=W)
        
        # Длительность (ряд 2)
        Label(input_frame, text="Длительность (мин):", font="Arial 10").grid(row=2, column=0, sticky=W, pady=5)
        self.duration_entry = ttk.Entry(input_frame, width=20, font="Arial 10")
        self.duration_entry.grid(row=2, column=1, padx=10, pady=5, sticky=W)
        
        # Привязываем валидацию длительности
        duration_vcmd = (self.root.register(self.validate_duration_input), '%P')
        self.duration_entry.config(validate="key", validatecommand=duration_vcmd)
        
        # Кнопка "Добавить тренировку"
        add_btn = Button(input_frame, text="Добавить тренировку", 
                        font=("Arial", 10, "bold"), fg="white", 
                        bg="green", command=self.add_training, width=20)
        add_btn.grid(row=3, column=0, columnspan=3, pady=10)
        
        #================================
        #  ПАНЕЛЬ ФИЛЬТРАЦИИ
        #================================
        filter_frame = LabelFrame(self.root, text="Фильтрация", 
                                  font="Arial 10 bold", padx=10, pady=5)
        filter_frame.pack(fill=X, padx=10, pady=5)
        
        # Фильтр по дате
        Label(filter_frame, text="Дата (с):", font="Arial 9").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_from = ttk.Entry(filter_frame, width=12, font="Arial 9")
        self.filter_date_from.grid(row=0, column=1, padx=5, pady=5)
        
        Label(filter_frame, text="по:", font="Arial 9").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_to = ttk.Entry(filter_frame, width=12, font="Arial 9")
        self.filter_date_to.grid(row=0, column=3, padx=5, pady=5)
        
        # Фильтр по типу тренировки
        Label(filter_frame, text="Тип тренировки:", font="Arial 9").grid(row=1, column=0, padx=5, pady=5)
        self.filter_type = StringVar()
        self.filter_type.set("Все")
        
        filter_types = ["Все"] + self.training_types
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type,
                                         values=filter_types, state="readonly", width=15)
        self.filter_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Кнопка "Применить фильтр"
        apply_filter_btn = Button(filter_frame, text="Применить фильтр", 
                                 font=("Arial", 9), command=self.update_table)
        apply_filter_btn.grid(row=1, column=2, padx=10, pady=5)
        
        # Кнопка "Сбросить фильтр"
        reset_filter_btn = Button(filter_frame, text="Сбросить фильтр", 
                                 font=("Arial", 9), command=self.reset_filter)
        reset_filter_btn.grid(row=1, column=3, padx=10, pady=5)
        
        #================================
        #  ТАБЛИЦА ТРЕНИРОВОК
        #================================
        table_frame = LabelFrame(self.root, text="Список тренировок", 
                                 font="Arial 10 bold", padx=5, pady=5)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Создаем Treeview для таблицы тренировок
        columns = ('id', 'date', 'type', 'duration')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Определяем заголовки
        self.tree.heading('id', text='ID')
        self.tree.heading('date', text='Дата')
        self.tree.heading('type', text='Тип тренировки')
        self.tree.heading('duration', text='Длительность (мин)')
        
        # Настройка ширины колонок
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('date', width=120, anchor='center')
        self.tree.column('type', width=200)
        self.tree.column('duration', width=120, anchor='center')
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        #================================
        #  НИЖНЯЯ ПАНЕЛЬ (УПРАВЛЕНИЕ)
        #================================
        bottom_frame = Frame(self.root)
        bottom_frame.pack(fill=X, padx=10, pady=5)
        
        # Кнопка "Удалить выбранную"
        delete_btn = Button(bottom_frame, text="Удалить выбранную тренировку", 
                           font=("Arial", 9), bg="red", fg="white", 
                           command=self.delete_training)
        delete_btn.pack(side=LEFT, padx=5)
        
        # Кнопка "Редактировать выбранную"
        edit_btn = Button(bottom_frame, text="Редактировать тренировку", 
                         font=("Arial", 9), bg="orange", fg="white",
                         command=self.edit_training)
        edit_btn.pack(side=LEFT, padx=5)
        
        # Кнопка "Экспорт в CSV"
        export_btn = Button(bottom_frame, text="Экспорт в CSV", 
                           font=("Arial", 9), bg="blue", fg="white",
                           command=self.export_csv)
        export_btn.pack(side=LEFT, padx=5)
        
        # Статистика
        stats_label = Label(bottom_frame, text="", font="Arial 9", fg="gray")
        stats_label.pack(side=RIGHT, padx=10)
        self.stats_label = stats_label
        
    #================================
    #  ВАЛИДАЦИЯ ВВОДА
    #================================
    def validate_date_input(self, value):
        """Валидация ввода даты"""
        if value == "":
            return True
        
        # Разрешаем только цифры и дефисы
        for char in value:
            if char not in "0123456789-":
                return False
        
        # Проверка формата при полном вводе
        if len(value) == 10:
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return True
            except ValueError:
                return False
        
        # Ограничиваем длину
        if len(value) > 10:
            return False
            
        return True
    
    def validate_duration_input(self, value):
        """Валидация ввода длительности"""
        if value == "":
            return True
        
        # Разрешаем только цифры
        if not value.isdigit():
            return False
        
        # Проверяем положительность
        if int(value) <= 0:
            return False
            
        return True
    
    #================================
    #  РАБОТА С ТРЕНИРОВКАМИ
    #================================
    def add_training(self):
        """Добавление новой тренировки"""
        # Получаем данные
        date = self.date_entry.get().strip()
        training_type = self.training_type.get()
        duration = self.duration_entry.get().strip()
        
        # Валидация
        if not date:
            messagebox.showwarning("Предупреждение", "Введите дату тренировки")
            return
        
        if not duration:
            messagebox.showwarning("Предупреждение", "Введите длительность тренировки")
            return
        
        # Проверка формата даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Предупреждение", 
                                  "Неверный формат даты!\nИспользуйте YYYY-MM-DD (например, 2026-05-04)")
            return
        
        # Проверка длительности
        try:
            duration_int = int(duration)
            if duration_int <= 0:
                messagebox.showwarning("Предупреждение", "Длительность должна быть положительным числом")
                return
        except ValueError:
            messagebox.showwarning("Предупреждение", "Длительность должна быть целым положительным числом")
            return
        
        # Создаем ID (автоинкремент)
        new_id = max([t['id'] for t in self.trainings], default=0) + 1
        
        # Добавляем тренировку
        training = {
            'id': new_id,
            'date': date,
            'type': training_type,
            'duration': duration_int
        }
        
        self.trainings.append(training)
        
        # Сохраняем в JSON
        self.save_trainings()
        
        # Обновляем таблицу
        self.update_table()
        
        # Очищаем поля (опционально)
        self.duration_entry.delete(0, END)
        
        messagebox.showinfo("Успешно", f"Тренировка добавлена!\n{date} - {training_type} ({duration_int} мин)")
    
    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления")
            return
        
        # Получаем ID выбранной тренировки
        item = self.tree.item(selected[0])
        training_id = item['values'][0]
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту тренировку?"):
            # Удаляем из списка
            self.trainings = [t for t in self.trainings if t['id'] != training_id]
            
            # Сохраняем в JSON
            self.save_trainings()
            
            # Обновляем таблицу
            self.update_table()
            
            messagebox.showinfo("Успешно", "Тренировка удалена")
    
    def edit_training(self):
        """Редактирование выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для редактирования")
            return
        
        # Получаем данные тренировки
        item = self.tree.item(selected[0])
        training_id = item['values'][0]
        training = next((t for t in self.trainings if t['id'] == training_id), None)
        
        if training:
            # Создаем окно редактирования
            edit_window = Toplevel(self.root)
            edit_window.title("Редактирование тренировки")
            edit_window.geometry("400x250+500+300")
            edit_window.resizable(False, False)
            
            # Поля редактирования
            Label(edit_window, text="Дата (YYYY-MM-DD):", font="Arial 10").pack(pady=5)
            date_entry = Entry(edit_window, font="Arial 10", width=20)
            date_entry.insert(0, training['date'])
            date_entry.pack(pady=5)
            
            Label(edit_window, text="Тип тренировки:", font="Arial 10").pack(pady=5)
            type_var = StringVar()
            type_var.set(training['type'])
            type_combo = ttk.Combobox(edit_window, textvariable=type_var,
                                      values=self.training_types, state="readonly", width=20)
            type_combo.pack(pady=5)
            
            Label(edit_window, text="Длительность (мин):", font="Arial 10").pack(pady=5)
            duration_entry = Entry(edit_window, font="Arial 10", width=20)
            duration_entry.insert(0, training['duration'])
            duration_entry.pack(pady=5)
            
            def save_edit():
                # Валидация изменений
                new_date = date_entry.get().strip()
                new_type = type_var.get()
                new_duration = duration_entry.get().strip()
                
                if not new_date:
                    messagebox.showwarning("Предупреждение", "Введите дату")
                    return
                
                try:
                    datetime.strptime(new_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("Предупреждение", "Неверный формат даты")
                    return
                
                if not new_duration.isdigit() or int(new_duration) <= 0:
                    messagebox.showwarning("Предупреждение", "Длительность должна быть положительным целым числом")
                    return
                
                # Обновляем данные
                training['date'] = new_date
                training['type'] = new_type
                training['duration'] = int(new_duration)
                
                self.save_trainings()
                self.update_table()
                edit_window.destroy()
                messagebox.showinfo("Успешно", "Тренировка обновлена")
            
            Button(edit_window, text="Сохранить", font=("Arial", 10, "bold"),
                  bg="green", fg="white", command=save_edit).pack(pady=10)
    
    def export_csv(self):
        """Экспорт тренировок в CSV файл"""
        if not self.trainings:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
        
        try:
            filename = f"trainings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("ID,Дата,Тип тренировки,Длительность (мин)\n")
                for training in self.trainings:
                    f.write(f"{training['id']},{training['date']},{training['type']},{training['duration']}\n")
            
            messagebox.showinfo("Успешно", f"Данные экспортированы в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")
    
    #================================
    #  ФИЛЬТРАЦИЯ
    #================================
    def apply_filters(self):
        """Применение фильтров к списку тренировок"""
        filtered = self.trainings.copy()
        
        # Фильтр по дате (с)
        date_from = self.filter_date_from.get().strip()
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
                filtered = [t for t in filtered if datetime.strptime(t['date'], "%Y-%m-%d") >= date_from_obj]
            except ValueError:
                pass
        
        # Фильтр по дате (по)
        date_to = self.filter_date_to.get().strip()
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
                filtered = [t for t in filtered if datetime.strptime(t['date'], "%Y-%m-%d") <= date_to_obj]
            except ValueError:
                pass
        
        # Фильтр по типу
        filter_type = self.filter_type.get()
        if filter_type != "Все":
            filtered = [t for t in filtered if t['type'] == filter_type]
        
        return filtered
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_date_from.delete(0, END)
        self.filter_date_to.delete(0, END)
        self.filter_type.set("Все")
        self.update_table()
    
    #================================
    #  ОБНОВЛЕНИЕ ДАННЫХ
    #================================
    def update_table(self):
        """Обновление таблицы с учетом фильтров"""
        # Очищаем текущие данные
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получаем отфильтрованные данные
        filtered_trainings = self.apply_filters()
        
        # Сортируем по дате (новые сверху)
        filtered_trainings.sort(key=lambda x: x['date'], reverse=True)
        
        # Добавляем записи в таблицу
        for training in filtered_trainings:
            self.tree.insert('', 'end', values=(
                training['id'],
                training['date'],
                training['type'],
                training['duration']
            ))
        
        # Обновляем статистику
        total_trainings = len(filtered_trainings)
        total_duration = sum(t['duration'] for t in filtered_trainings)
        
        self.stats_label.config(text=f"Всего тренировок: {total_trainings} | Общая длительность: {total_duration} мин")
    
    #================================
    #  РАБОТА С JSON
    #================================
    def save_trainings(self):
        """Сохранение тренировок в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def load_trainings(self):
        """Загрузка тренировок из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
            except Exception as e:
                messagebox.showwarning("Предупреждение", 
                                      f"Не удалось загрузить данные: {str(e)}\nБудет создан новый файл.")
                self.trainings = []
        else:
            # Добавляем примеры тренировок для демонстрации
            self.trainings = [
                {'id': 1, 'date': '2026-05-01', 'type': 'Кардио', 'duration': 45},
                {'id': 2, 'date': '2026-05-02', 'type': 'Силовая', 'duration': 60},
                {'id': 3, 'date': '2026-05-03', 'type': 'Йога', 'duration': 30},
                {'id': 4, 'date': '2026-05-04', 'type': 'Бег', 'duration': 50},
            ]

#================================
#  З А П У С К   П Р О Г Р А М М Ы
#================================
if __name__ == "__main__":
    root = Tk()
    app = TrainingPlanner(root)
    root.mainloop()
