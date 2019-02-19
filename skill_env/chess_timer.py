from datetime import timedelta, datetime

def _get_time(date_time_in_str):
    dt, _, us= date_time_in_str.partition(".")
    dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    # тот редкий случай когда мы попали на 0 количество милисекунд
    if us =='':
        return dt
    us= int(us.rstrip("Z"), 10)
    return dt + timedelta(microseconds=us)

class ChessTimer(object):
    _players = [
        'Blue',
        'Red',
        'Green',
        'Yellow',
        'Black',
        'White',
        'Brown',
        'Pink'
    ]

    def __init__(self, state:dict)->dict:
        '''конструктор принимаем на вход текущее состояние таймера и
        заполняем свое состояние'''
        init_state = {player:0 for player in self._players}
        init_state['current_player'] = None
        init_state['current_player_name'] = None
        init_state['start_current_step_time'] = None
        # получаем актуальное состояние
        # если чегото не хватает просто простовляем из init_state
        self._state = {key:state[key] if key in state else init_state[key] for key in init_state}


    def step(self):
        current_time = datetime.now()
        # если мы только стартуем и ни один игрок не был выбран
        if self._state['current_player'] == None:
            self._state['current_player'] = 0
            self._state['start_current_step_time'] = current_time
            self._state['current_player_name'] = self._players[self._state['current_player']]
            return self._state
        # получим текущего игрока
        current_player = self._state['current_player']
        # добавим текущему игроку время его хода
        time_delta = current_time - _get_time(self._state['start_current_step_time'])
        self._state[self._players[current_player]] += time_delta.total_seconds()
        # проставим время начала текущего хода
        self._state['start_current_step_time'] = current_time.isoformat()
        # если текущий ход был у последнего игрока
        # переводим на 1 игрока
        # в противном случае на следующего
        if current_player == len(self._players) - 1:
            self._state['current_player'] = 0
        else:
            self._state['current_player'] += 1
        self._state['current_player_name'] = self._players[self._state['current_player']]
        return self._state

    def get_statistic(self):
        current_time = datetime.now()
        def get_statistic_for_player(player):
            if player != self._state['current_player_name']:
                return self._state[player]
            # для текущего игрока накинем текущее время
            current_time = datetime.now()
            current_time_delta = (current_time - _get_time(self._state['start_current_step_time'])).total_seconds()
            return self._state[player] + current_time_delta


        return {player:get_statistic_for_player(player) for player in self._players}

            


