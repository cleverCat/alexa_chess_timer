import unittest
from mock import patch


class TestChessTimer(unittest.TestCase):
    def setUp(self):
        import sys
        if 'chess_timer' in sys.modules.keys():
            del sys.modules['chess_timer']
        self._list_module = list(sys.modules.keys())

    def tearDown(self):
        import sys
        current_list_module = list(sys.modules.keys())
        for i in [
                i for i in current_list_module if i not in self._list_module
        ]:
            del sys.modules[i]
        if 'chess_timer' in sys.modules.keys():
            del sys.modules['dhess_timer']

    def test_init(self):
        from chess_timer import ChessTimer
        from datetime import timedelta
        init_state = {
            player: timedelta(microseconds=0).microseconds
            for player in ChessTimer._players
        }
        init_state['current_player'] = None
        init_state['current_player_name'] = None
        init_state['start_current_step_time'] = None
        self.assertEqual(ChessTimer({})._state, init_state)

    def test_init_step(self):

        from datetime import datetime
        current_time = datetime.now()
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = current_time
            from chess_timer import ChessTimer
            state = ChessTimer({}).step()
            self.assertEqual(state['current_player'], 0)
            self.assertEqual(state['start_current_step_time'], current_time)

    def test_step_last_player(self):

        from datetime import datetime
        current_time = datetime.now()
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = current_time
            from chess_timer import ChessTimer
            state = ChessTimer(
                dict(
                    current_player=len(ChessTimer._players) - 1,
                    start_current_step_time=current_time.isoformat())).step()
            self.assertEqual(state['current_player'], 0)

    def test_step(self):

        from datetime import datetime
        from datetime import timedelta

        def _get_time(dt_str):
            dt, _, us = dt_str.partition(".")
            dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
            return dt

        current_time = _get_time(datetime.now().isoformat())
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = current_time
            old_time = current_time - timedelta(minutes=10)
            mock_datetime.strptime.return_value = old_time
            from chess_timer import ChessTimer
            state = ChessTimer(
                dict(
                    current_player=0,
                    start_current_step_time=(old_time).isoformat())).step()
            self.assertEqual(state['current_player'], 1)
            self.assertEqual(state[ChessTimer._players[0]],
                             (current_time - _get_time(
                                 old_time.isoformat())).total_seconds())

    def test_get_statistic(self):
        from datetime import timedelta
        from chess_timer import ChessTimer
        state = ChessTimer(
            dict(Red=timedelta(minutes=10).total_seconds())).get_statistic()
        self.assertEqual(state['Red'] // 60 % 60, 10)


if __name__ == '__main__':
    unittest.main()
