import pytest
import src as cre


class TestCreateAbdr:
    def test_one(self):
        c = cre.CreateAbdr()
        c.set_data('bianco-saw595-ax', 8.0, 6)
        c.calculate_abdr()

        print(c.get_results())
        t = 1
        assert c.get_results() == pytest.approx(t)
