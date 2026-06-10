import tkinter as tk
from tkinter import messagebox


class Checkers2D:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Шашки")
        self.window.resizable(False, False)

        # Размеры
        self.board_size = 800
        self.square_size = self.board_size // 8
        self.piece_radius = self.square_size // 2 - 10

        # Игровое поле
        self.board = []
        self.current_player = 'W'
        self.selected_piece = None
        self.valid_moves = []
        self.must_capture = False
        self.game_over = False
        self.multi_capture_chain = False  # Флаг для цепочки взятий
        self.multi_capture_piece = None  # Шашка, которая делает цепочку взятий
        self.captured_pieces = []  # Список уже съеденных шашек в текущем ходе

        # Цвета
        self.colors = {
            'light': '#F0D9B5',
            'dark': '#B58863',
            'highlight': '#FFFF00',
            'valid_move': '#90EE90',
            'capture_move': '#FF6347',
            'multi_capture': '#FFA500'  # Оранжевый для продолжения цепочки взятий
        }

        # Создание Canvas
        self.canvas = tk.Canvas(self.window,
                                width=self.board_size,
                                height=self.board_size,
                                bg='white')
        self.canvas.pack()

        # Информационная панель
        self.info_frame = tk.Frame(self.window)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.player_label = tk.Label(self.info_frame,
                                     text="Ход: Белые",
                                     font=('Arial', 14, 'bold'))
        self.player_label.pack(side=tk.LEFT)

        self.status_label = tk.Label(self.info_frame,
                                     text="",
                                     font=('Arial', 12))
        self.status_label.pack(side=tk.RIGHT)

        # Кнопка сброса
        tk.Button(self.window,
                  text="Новая игра",
                  command=self.reset_game,
                  font=('Arial', 10)).pack(pady=5)

        # Инициализация
        self.initialize_board()
        self.draw_board()
        self.canvas.bind('<Button-1>', self.on_square_click)

        # Правила игры
        self.show_rules()

    def show_rules(self):
        """Показать правила игры"""
        rules = """
        ПРАВИЛА ИГРЫ В ШАШКИ:
        1. Ходят по очереди: белые начинают
        2. Кликните на свою шашку, чтобы выбрать её
        3. Зелёные клетки - возможные ходы
        4. Красные клетки - обязательные взятия
        5. Оранжевые клетки - продолжение цепочки взятий
        6. Взятие обязательно, если есть возможность
        7. Можно рубить назад
        8. Дамки могут ходить на любое расстояние по диагонали
        9. МНОЖЕСТВЕННЫЕ ВЗЯТИЯ: можно рубить несколько шашек за один ход,
           если после взятия есть возможность взять ещё

        Для победы нужно съесть все шашки противника
        или лишить его возможности хода.
        """
        messagebox.showinfo("Правила шашек", rules)

    def initialize_board(self):
        """Инициализация игрового поля"""
        self.board = [
            ['0', 'B', '0', 'B', '0', 'B', '0', 'B'],
            ['B', '0', 'B', '0', 'B', '0', 'B', '0'],
            ['0', 'B', '0', 'B', '0', 'B', '0', 'B'],
            ['0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0'],
            ['W', '0', 'W', '0', 'W', '0', 'W', '0'],
            ['0', 'W', '0', 'W', '0', 'W', '0', 'W'],
            ['W', '0', 'W', '0', 'W', '0', 'W', '0']
        ]

    def draw_board(self):
        """Отрисовка игровой доски"""
        self.canvas.delete("all")

        # Рисуем клетки
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                color = self.colors['light'] if (row + col) % 2 == 0 else self.colors['dark']
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=color,
                                             outline=color)

        # Рисуем шашки
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != '0':
                    self.draw_piece(row, col, piece)

        # Подсвечиваем выбранную шашку
        if self.selected_piece:
            row, col = self.selected_piece
            self.highlight_square(row, col, self.colors['highlight'])

        # Показываем возможные ходы
        for move in self.valid_moves:
            if len(move) == 3:  # Простой ход
                move_row, move_col, is_capture = move
            else:  # Взятие
                move_row, move_col, is_capture, _, _ = move

            if self.multi_capture_chain:
                color = self.colors['multi_capture']
            else:
                color = self.colors['capture_move'] if is_capture else self.colors['valid_move']
            self.highlight_square(move_row, move_col, color, alpha=0.7)

    def draw_piece(self, row, col, piece):
        """Рисуем шашку на доске"""
        x = col * self.square_size + self.square_size // 2
        y = row * self.square_size + self.square_size // 2

        if piece in ['W', 'WK']:
            color = 'white'
            outline = 'black'
        else:
            color = 'black'
            outline = 'white'

        # Рисуем основу шашки
        self.canvas.create_oval(x - self.piece_radius,
                                y - self.piece_radius,
                                x + self.piece_radius,
                                y + self.piece_radius,
                                fill=color,
                                outline=outline,
                                width=2)

        # Рисуем корону для дамки
        if piece in ['WK', 'BK']:
            crown_size = self.piece_radius * 0.7
            self.canvas.create_text(x, y,
                                    text="♔" if piece == 'WK' else "♚",
                                    font=('Arial', int(crown_size), 'bold'),
                                    fill='gold')

    def highlight_square(self, row, col, color, alpha=0.5):
        """Подсветка клетки"""
        x1 = col * self.square_size
        y1 = row * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size

        self.canvas.create_rectangle(x1, y1, x2, y2,
                                     fill="",
                                     outline=color,
                                     width=4)

    def get_valid_moves_for_piece(self, row, col, piece, check_captures_only=False, ignore_captured=None):
        """Получение всех возможных ходов для конкретной шашки"""
        moves = []
        captures = []

        if piece == '0':
            return [], []

        # Для обычных шашек
        if piece in ['W', 'B']:
            return self.get_regular_moves(row, col, piece, check_captures_only, ignore_captured)

        # Для дамок
        return self.get_king_moves(row, col, piece, check_captures_only, ignore_captured)

    def get_regular_moves(self, row, col, piece, check_captures_only=False, ignore_captured=None):
        """Ходы для обычных шашек с поддержкой множественных взятий"""
        moves = []
        captures = []

        if ignore_captured is None:
            ignore_captured = []

        # Все направления для взятий (и вперед, и назад)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        # Проверяем все направления на возможность взятия
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = self.board[new_row][new_col]
                target_pos = (new_row, new_col)

                # Проверяем, что на соседней клетке шашка противника и её ещё не брали в этом ходе
                if (((piece == 'W' and target_piece in ['B', 'BK']) or
                     (piece == 'B' and target_piece in ['W', 'WK'])) and
                        target_pos not in ignore_captured):

                    jump_row, jump_col = new_row + dr, new_col + dc
                    # Проверяем, что за шашкой противника есть пустая клетка
                    if 0 <= jump_row < 8 and 0 <= jump_col < 8:
                        if self.board[jump_row][jump_col] == '0':
                            captures.append((jump_row, jump_col, True, new_row, new_col))

        # Если есть взятия и мы их ищем, возвращаем только их
        if captures and check_captures_only:
            return [], captures

        # Если есть взятия, простые ходы не разрешены
        if captures:
            return [], captures

        # Если нет взятий, проверяем простые ходы
        if not check_captures_only:
            # Направления для обычных ходов (только вперед)
            if piece == 'W':  # Белые ходят вверх
                move_directions = [(-1, -1), (-1, 1)]
            else:  # Черные ходят вниз
                move_directions = [(1, -1), (1, 1)]

            for dr, dc in move_directions:
                new_row, new_col = row + dr, col + dc

                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if self.board[new_row][new_col] == '0':
                        moves.append((new_row, new_col, False))

        return moves, captures

    def get_king_moves(self, row, col, piece, check_captures_only=False, ignore_captured=None):
        """Ходы для дамки с поддержкой множественных взятий"""
        moves = []
        captures = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        if ignore_captured is None:
            ignore_captured = []

        # Сначала проверяем все возможные взятия
        for dr, dc in directions:
            # Ищем шашку противника в этом направлении
            found_opponent = False
            opponent_row, opponent_col = -1, -1
            opponent_pos = None

            for distance in range(1, 8):
                check_row, check_col = row + dr * distance, col + dc * distance

                if not (0 <= check_row < 8 and 0 <= check_col < 8):
                    break

                target_piece = self.board[check_row][check_col]
                target_pos = (check_row, check_col)

                # Если нашли пустую клетку до шашки противника
                if target_piece == '0' and not found_opponent:
                    continue

                # Если нашли шашку противника
                if (((piece == 'WK' and target_piece in ['B', 'BK']) or
                     (piece == 'BK' and target_piece in ['W', 'WK'])) and
                        target_pos not in ignore_captured):

                    if not found_opponent:
                        found_opponent = True
                        opponent_row, opponent_col = check_row, check_col
                        opponent_pos = target_pos
                    else:
                        break  # Нельзя перепрыгивать через две шашки

                # Если нашли свою шашку
                elif ((piece == 'WK' and target_piece in ['W', 'WK']) or
                      (piece == 'BK' and target_piece in ['B', 'BK'])):
                    break

                # Если нашли пустую клетку после шашки противника
                elif target_piece == '0' and found_opponent:
                    captures.append((check_row, check_col, True, opponent_row, opponent_col))
                    # Проверяем возможность дальнейших взятий из этой позиции
                    # (для цепочки взятий дамкой)

        # Если есть взятия и мы их ищем, возвращаем только их
        if captures and check_captures_only:
            return [], captures

        # Если есть взятия, простые ходы не разрешены
        if captures:
            return [], captures

        # Если нет взятий, проверяем простые ходы
        if not check_captures_only:
            for dr, dc in directions:
                for distance in range(1, 8):
                    new_row, new_col = row + dr * distance, col + dc * distance

                    if not (0 <= new_row < 8 and 0 <= new_col < 8):
                        break

                    if self.board[new_row][new_col] != '0':
                        break

                    moves.append((new_row, new_col, False))

        return moves, captures

    def check_multi_capture_continuation(self, from_row, from_col, piece):
        """Проверка возможности продолжения цепочки взятий из новой позиции"""
        # Проверяем, есть ли взятия из новой позиции, игнорируя уже съеденные шашки
        _, captures = self.get_valid_moves_for_piece(from_row, from_col, piece, True, self.captured_pieces)
        return captures

    def check_any_captures(self, player, ignore_captured=None):
        """Проверка, есть ли у игрока обязательные взятия"""
        if ignore_captured is None:
            ignore_captured = []

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (player == 'W' and piece in ['W', 'WK']) or (player == 'B' and piece in ['B', 'BK']):
                    _, captures = self.get_valid_moves_for_piece(row, col, piece, True, ignore_captured)
                    if captures:
                        return True
        return False

    def on_square_click(self, event):
        """Обработка клика по клетке"""
        if self.game_over:
            return

        col = event.x // self.square_size
        row = event.y // self.square_size

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        piece = self.board[row][col]

        # Если уже идет цепочка множественных взятий
        if self.multi_capture_chain:
            # Проверяем, является ли клик по допустимому продолжению взятия
            for i, move_info in enumerate(self.valid_moves):
                if len(move_info) == 3:  # Простой ход (не должно быть в цепочке)
                    continue
                else:  # Взятие
                    move_row, move_col, is_capture, cap_row, cap_col = move_info

                if move_row == row and move_col == col:
                    self.continue_multi_capture(i)
                    return

            # Если кликнули на ту же самую шашку, которая делает цепочку
            if (row, col) == self.multi_capture_piece:
                return

            # Если кликнули на другую шашку - игнорируем
            self.update_status("Продолжите цепочку взятий или завершите ход кликом на текущую шашку")
            return

        # Если уже выбрана шашка, пытаемся сделать ход
        if self.selected_piece:
            # Проверяем, является ли клик по допустимому ходу
            for i, move_info in enumerate(self.valid_moves):
                if len(move_info) == 3:  # Простой ход
                    move_row, move_col, is_capture = move_info
                else:  # Взятие
                    move_row, move_col, is_capture, cap_row, cap_col = move_info

                if move_row == row and move_col == col:
                    self.make_move(i)
                    return

            # Если кликнули на другую свою шашку
            if ((self.current_player == 'W' and piece in ['W', 'WK']) or
                    (self.current_player == 'B' and piece in ['B', 'BK'])):
                self.select_piece(row, col)
            else:
                # Отменяем выбор
                self.selected_piece = None
                self.valid_moves = []
                self.draw_board()
                self.update_status("Выбор отменен")
        else:
            # Выбираем шашку
            self.select_piece(row, col)

    def select_piece(self, row, col):
        """Выбор шашки для хода"""
        piece = self.board[row][col]

        # Проверяем, что выбрана своя шашка
        if (self.current_player == 'W' and piece not in ['W', 'WK']) or \
                (self.current_player == 'B' and piece not in ['B', 'BK']):
            self.update_status("Выберите свою шашку!")
            return False

        # Проверяем обязательные взятия
        self.must_capture = self.check_any_captures(self.current_player)

        moves, captures = self.get_valid_moves_for_piece(row, col, piece, self.must_capture)

        # Если есть обязательные взятия, показываем только их
        if self.must_capture:
            if not captures:
                self.update_status("У вас есть обязательное взятие!")
                return False
            self.valid_moves = captures
            self.update_status("Обязательное взятие! Выберите куда прыгнуть")
        else:
            if not moves and not captures:
                self.update_status("У этой шашки нет возможных ходов!")
                return False
            self.valid_moves = moves + captures
            self.update_status("Выберите куда ходить")

        self.selected_piece = (row, col)
        self.draw_board()
        return True

    def make_move(self, move_index):
        """Выполнение хода"""
        from_row, from_col = self.selected_piece
        move_info = self.valid_moves[move_index]

        # Определяем тип хода
        if len(move_info) == 3:  # Простой ход (row, col, is_capture)
            to_row, to_col, is_capture = move_info
            cap_row, cap_col = None, None
        else:  # Взятие (row, col, is_capture, cap_row, cap_col)
            to_row, to_col, is_capture, cap_row, cap_col = move_info

        # Сохраняем шашку
        piece = self.board[from_row][from_col]

        # Перемещаем шашку
        self.board[from_row][from_col] = '0'
        self.board[to_row][to_col] = piece

        # Удаляем съеденную шашку
        if is_capture and cap_row is not None and cap_col is not None:
            self.board[cap_row][cap_col] = '0'
            self.captured_pieces.append((cap_row, cap_col))

        # Проверяем превращение в дамку
        if piece == 'W' and to_row == 0:
            self.board[to_row][to_col] = 'WK'
            piece = 'WK'  # Обновляем тип шашки
            self.update_status("Белая шашка стала дамкой!")
        elif piece == 'B' and to_row == 7:
            self.board[to_row][to_col] = 'BK'
            piece = 'BK'  # Обновляем тип шашки
            self.update_status("Черная шашка стала дамкой!")

        # Проверяем возможность продолжения цепочки взятий
        if is_capture:
            # Проверяем, есть ли ещё взятия из новой позиции
            further_captures = self.check_multi_capture_continuation(to_row, to_col, piece)

            if further_captures:
                # Включаем режим цепочки взятий
                self.multi_capture_chain = True
                self.multi_capture_piece = (to_row, to_col)
                self.selected_piece = (to_row, to_col)
                self.valid_moves = further_captures
                self.update_status("Продолжите цепочку взятий! Вы можете рубить ещё")
                self.draw_board()
                return True

        # Если цепочка взятий завершена, завершаем ход
        self.complete_turn()
        return True

    def continue_multi_capture(self, move_index):
        """Продолжение цепочки множественных взятий"""
        if not self.multi_capture_chain:
            return False

        from_row, from_col = self.multi_capture_piece
        move_info = self.valid_moves[move_index]

        # Должно быть взятие
        to_row, to_col, is_capture, cap_row, cap_col = move_info

        # Сохраняем шашку
        piece = self.board[from_row][from_col]

        # Перемещаем шашку
        self.board[from_row][from_col] = '0'
        self.board[to_row][to_col] = piece

        # Удаляем съеденную шашку
        self.board[cap_row][cap_col] = '0'
        self.captured_pieces.append((cap_row, cap_col))

        # Проверяем превращение в дамку (посреди цепочки!)
        if piece == 'W' and to_row == 0:
            self.board[to_row][to_col] = 'WK'
            piece = 'WK'
            self.update_status("Белая шашка стала дамкой во время цепочки взятий!")
        elif piece == 'B' and to_row == 7:
            self.board[to_row][to_col] = 'BK'
            piece = 'BK'
            self.update_status("Черная шашка стала дамкой во время цепочки взятий!")

        # Проверяем возможность продолжения цепочки взятий
        further_captures = self.check_multi_capture_continuation(to_row, to_col, piece)

        if further_captures:
            # Продолжаем цепочку
            self.multi_capture_piece = (to_row, to_col)
            self.selected_piece = (to_row, to_col)
            self.valid_moves = further_captures
            self.update_status(f"Продолжайте! Вы уже съели {len(self.captured_pieces)} шашек")
            self.draw_board()
        else:
            # Цепочка завершена
            self.complete_turn()

        return True

    def complete_turn(self):
        """Завершение хода"""
        # Сбрасываем всё
        self.selected_piece = None
        self.valid_moves = []
        self.multi_capture_chain = False
        self.multi_capture_piece = None
        self.captured_pieces = []

        # Меняем игрока
        self.current_player = 'B' if self.current_player == 'W' else 'W'
        self.update_turn()
        self.update_status(f"Ход переходит к {'черным' if self.current_player == 'B' else 'белым'}")

        # Перерисовываем доску
        self.draw_board()

        # Проверяем окончание игры
        self.check_game_over()

    def update_turn(self):
        """Обновление информации о ходе"""
        player_text = "Ход: Белые" if self.current_player == 'W' else "Ход: Черные"
        self.player_label.config(text=player_text)

    def update_status(self, message):
        """Обновление статусного сообщения"""
        self.status_label.config(text=message)

    def check_game_over(self):
        """Проверка окончания игры"""
        white_pieces = 0
        black_pieces = 0
        white_moves = False
        black_moves = False

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece in ['W', 'WK']:
                    white_pieces += 1
                    if not white_moves:
                        moves, captures = self.get_valid_moves_for_piece(row, col, piece, False)
                        if moves or captures:
                            white_moves = True
                elif piece in ['B', 'BK']:
                    black_pieces += 1
                    if not black_moves:
                        moves, captures = self.get_valid_moves_for_piece(row, col, piece, False)
                        if moves or captures:
                            black_moves = True

        if white_pieces == 0 or not white_moves:
            self.game_over = True
            messagebox.showinfo("Игра окончена!", "ПОБЕДА ЧЕРНЫХ!")
        elif black_pieces == 0 or not black_moves:
            self.game_over = True
            messagebox.showinfo("Игра окончена!", "ПОБЕДА БЕЛЫХ!")

        return self.game_over

    def reset_game(self):
        """Сброс игры"""
        self.initialize_board()
        self.current_player = 'W'
        self.selected_piece = None
        self.valid_moves = []
        self.must_capture = False
        self.game_over = False
        self.multi_capture_chain = False
        self.multi_capture_piece = None
        self.captured_pieces = []
        self.update_turn()
        self.update_status("Новая игра начата!")
        self.draw_board()

    def run(self):
        """Запуск игры"""
        self.window.mainloop()


def main():
    """Точка входа в программу"""
    game = Checkers2D()
    game.run()


if __name__ == "__main__":
    main()
