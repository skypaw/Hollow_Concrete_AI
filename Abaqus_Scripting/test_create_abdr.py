import pytest
import src as cre


class TestCreateAbdr:
    def test_one(self):
        c = cre.CreateAbdr()
        c.set_data('bianco-saw595-ax', 8.0, 6)
        c.calculate_abdr()

        print(c.get_results())
        t = [2139.7, 1664.5, 382.9, 662.53, 6392.2, 3859.4, 1114.7, 1655.5, 202.42, 98.973]
        assert c.get_results() == pytest.approx(t, 0.05)
