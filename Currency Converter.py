# coding=utf-8
#######################################################
# Программа Конвертер валют (с выбором валют и историей)
# python 3.x
# WebForMySelf - Денис Новокщенов, 2026
# Модернизация: выбор валют, история конвертаций, валидация
#######################################################

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import urllib.request
import json
import os
from datetime import datetime

#================================
#  К Л А С С Ы
#================================
class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title('Конвертер валют - PrivatBank')
        self.root.geometry("500x550+700+200")
        self.root.resizable(False, False)
        
        # Иконка (если файл существует)
        try:
            self.root.iconbitmap('nt.ico')
        except:
            pass
        
        self.START_AMOUNT = 100
        self.JSON_object = None
        self.currencies = []  # Список доступных валют
        self.history_file = "conversion_history.json"
        self.history = []  # История конвертаций
        
        # Загрузка истории при старте
        self.load_history()
        
        # Получение курсов валют
        self.get_exchange_rates()
        
        # Создание интерфейса
        self.create_widgets()
        
    def get_exchange_rates(self):
        """Получение курсов валют из API PrivatBank"""
        try:
            # Безнал (cards)
            html = urllib.request.urlopen('https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=11')
            data = html.read()
            self.JSON_object = json.loads(data)
            
            # Формируем список доступных валют
            self.currencies = []
            for currency in self.JSON_object:
                self.currencies.append(currency['ccy'])
                
        except Exception as e:
            messagebox.showerror("Ошибка", 
                               'Ошибка получения курсов валют.\n'
                               'Нет подключения к интернету или проблема с API.\n'
                               f'Детали: {str(e)}')
            self.JSON_object = None
            self.currencies = ['USD', 'EUR']  # Значения по умолчанию
            
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        
        #================================
        #  H E A D E R   F R A M E
        #================================
        header_frame = Frame(self.root)
        header_frame.pack(fill=X, padx=10, pady=5)
        
        # Равномерное размещение колонок
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)
        
        # Заголовки
        h_currency = Label(header_frame, text="Валюта", bg="#000", fg="#fff", 
                          font="Arial 12 bold")
        h_currency.grid(row=0, column=0, sticky=EW)
        h_buy = Label(header_frame, text="Покупка", bg="orange", fg="white", 
                     font="Arial 12 bold")
        h_buy.grid(row=0, column=1, sticky=EW)
        h_sale = Label(header_frame, text="Продажа", bg="blue", fg="white", 
                      font="Arial 12 bold")
        h_sale.grid(row=0, column=2, sticky=EW)
        
        # Отображение курсов валют
        if self.JSON_object:
            for i, currency in enumerate(self.JSON_object, 1):
                bg_color = "#ccc" if i % 2 == 1 else "#eee"
                
                curr_label = Label(header_frame, text=currency['ccy'], 
                                  bg=bg_color, font="Arial 10")
                curr_label.grid(row=i, column=0, sticky=EW)
                
                buy_label = Label(header_frame, text=currency['buy'], 
                                 bg=bg_color, font="Arial 10")
                buy_label.grid(row=i, column=1, sticky=EW)
                
                sale_label = Label(header_frame, text=currency['sale'], 
                                  bg=bg_color, font="Arial 10")
                sale_label.grid(row=i, column=2, sticky=EW)
        
        #================================
        #  C O N V E R T   F R A M E
        #================================
        convert_frame = LabelFrame(self.root, text="Конвертация валют", 
                                   font="Arial 10 bold", padx=10, pady=10)
        convert_frame.pack(fill=X, padx=10, pady=5)
        
        # Выбор валюты
        Label(convert_frame, text="Выберите валюту:", font="Arial 10").grid(row=0, column=0, sticky=W)
        
        self.selected_currency = StringVar()
        if self.currencies:
            self.selected_currency.set(self.currencies[0])
        
        self.currency_combo = ttk.Combobox(convert_frame, textvariable=self.selected_currency,
                                          values=self.currencies, state="readonly", width=10)
        self.currency_combo.grid(row=0, column=1, padx=10, sticky=W)
        self.currency_combo.bind('<<ComboboxSelected>>', self.on_currency_change)
        
        # Сумма для конвертации
        Label(convert_frame, text="Сумма:", font="Arial 10").grid(row=1, column=0, sticky=W, pady=10)
        
        self.amount_entry = ttk.Entry(convert_frame, justify=CENTER, font="Arial 10", width=20)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=10, sticky=W)
        self.amount_entry.insert(0, str(self.START_AMOUNT))
        
        # Привязываем валидацию
        vcmd = (self.root.register(self.validate_amount), '%P')
        self.amount_entry.config(validate="key", validatecommand=vcmd)
        
        # Кнопка конвертации
        convert_btn = Button(convert_frame, text="Конвертировать", 
                            font=("Arial", 10, "bold"), fg="white", 
                            bg="green", command=self.convert_currency)
        convert_btn.grid(row=2, column=0, columnspan=2, sticky=EW, pady=5)
        
        #================================
        #  R E S U L T   F R A M E
        #================================
        result_frame = LabelFrame(self.root, text="Результат", 
                                  font="Arial 10 bold", padx=10, pady=10)
        result_frame.pack(fill=X, padx=10, pady=5)
        
        Label(result_frame, text="UAH:", font="Arial 10 bold").grid(row=0, column=0, sticky=W)
        self.result_entry = ttk.Entry(result_frame, justify=CENTER, font="Arial 10", 
                                      state="readonly", width=20)
        self.result_entry.grid(row=0, column=1, padx=10, sticky=W)
        
        #================================
        #  H I S T O R Y   F R A M E
        #================================
        history_frame = LabelFrame(self.root, text="История конвертаций", 
                                   font="Arial 10 bold", padx=5, pady=5)
        history_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Создаем Treeview для истории
        columns = ('datetime', 'from_currency', 'amount', 'to_currency', 'result', 'rate')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=8)
        
        # Определяем заголовки
        self.history_tree.heading('datetime', text='Дата/Время')
        self.history_tree.heading('from_currency', text='Из')
        self.history_tree.heading('amount', text='Сумма')
        self.history_tree.heading('to_currency', text='В')
        self.history_tree.heading('result', text='Результат')
        self.history_tree.heading('rate', text='Курс')
        
        # Настройка ширины колонок
        self.history_tree.column('datetime', width=130)
        self.history_tree.column('from_currency', width=50)
        self.history_tree.column('amount', width=80)
        self.history_tree.column('to_currency', width=50)
        self.history_tree.column('result', width=80)
        self.history_tree.column('rate', width=80)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient=VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Кнопки управления историей
        history_buttons_frame = Frame(self.root)
        history_buttons_frame.pack(fill=X, padx=10, pady=5)
        
        clear_history_btn = Button(history_buttons_frame, text="Очистить историю", 
                                  font=("Arial", 9), command=self.clear_history)
        clear_history_btn.pack(side=LEFT, padx=5)
        
        # Загружаем историю в таблицу
        self.update_history_display()
        
    def validate_amount(self, value):
        """Валидация вводимой суммы"""
        if value == "":
            return True
        
        try:
            # Проверяем, что это число
            num = float(value)
            # Проверяем, что число положительное
            if num <= 0:
                return False
            return True
        except ValueError:
            return False
    
    def on_currency_change(self, event):
        """Обработчик изменения выбранной валюты"""
        # Очищаем результат при смене валюты
        self.result_entry.config(state="normal")
        self.result_entry.delete(0, END)
        self.result_entry.config(state="readonly")
    
    def convert_currency(self):
        """Конвертация валюты в гривны"""
        if not self.JSON_object:
            messagebox.showerror("Ошибка", "Нет данных о курсах валют. Проверьте подключение к интернету.")
            return
        
        # Проверяем введенную сумму
        amount_str = self.amount_entry.get()
        if not amount_str:
            messagebox.showwarning("Предупреждение", "Введите сумму для конвертации")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Предупреждение", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showwarning("Предупреждение", "Введите корректное число (например: 100 или 100.50)")
            return
        
        # Получаем выбранную валюту
        selected_ccy = self.selected_currency.get()
        
        # Находим курс продажи для выбранной валюты
        rate = None
        for currency in self.JSON_object:
            if currency['ccy'] == selected_ccy:
                rate = float(currency['sale'])
                break
        
        if rate is None:
            messagebox.showerror("Ошибка", f"Курс для валюты {selected_ccy} не найден")
            return
        
        # Выполняем конвертацию
        result = round(amount * rate, 2)
        
        # Отображаем результат
        self.result_entry.config(state="normal")
        self.result_entry.delete(0, END)
        self.result_entry.insert(0, f"{result:.2f}")
        self.result_entry.config(state="readonly")
        
        # Сохраняем в историю
        self.save_to_history(selected_ccy, amount, result, rate)
        
        # Показываем сообщение об успешной конвертации
        messagebox.showinfo("Успешно", 
                           f"Конвертация выполнена!\n"
                           f"{amount:.2f} {selected_ccy} = {result:.2f} UAH\n"
                           f"Курс: 1 {selected_ccy} = {rate:.4f} UAH")
        
    def save_to_history(self, currency, amount, result, rate):
        """Сохранение конвертации в историю"""
        history_entry = {
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'from_currency': currency,
            'amount': amount,
            'to_currency': 'UAH',
            'result': result,
            'rate': rate
        }
        
        self.history.append(history_entry)
        
        # Сохраняем в JSON файл
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")
        
        # Обновляем отображение истории
        self.update_history_display()
    
    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                messagebox.showwarning("Предупреждение", 
                                      f"Не удалось загрузить историю: {str(e)}\n"
                                      "Будет создана новая история.")
                self.history = []
        else:
            self.history = []
    
    def update_history_display(self):
        """Обновление отображения истории в таблице"""
        # Очищаем текущие данные
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Добавляем записи из истории
        for entry in reversed(self.history):  # Показываем последние сверху
            self.history_tree.insert('', 'end', values=(
                entry['datetime'],
                entry['from_currency'],
                f"{entry['amount']:.2f}",
                entry['to_currency'],
                f"{entry['result']:.2f}",
                f"{entry['rate']:.4f}"
            ))
    
    def clear_history(self):
        """Очистка истории конвертаций"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            
            # Удаляем файл истории
            try:
                if os.path.exists(self.history_file):
                    os.remove(self.history_file)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить файл истории: {str(e)}")
            
            # Обновляем отображение
            self.update_history_display()
            messagebox.showinfo("Успешно", "История конвертаций очищена")


#================================
#  З А П У С К   П Р О Г Р А М М Ы
#================================
if __name__ == "__main__":
    root = Tk()
    app = CurrencyConverter(root)
    root.mainloop()
