SET1 = [1, 2, 3, 4, 5, 6]
SET2 = [1, 2, 3, 4, 5]
SET3 = [1, 2, 3, 4]
SET4 = [1, 2, 3]
SET5 = [1, 2]
SET6 = [1]


class GameProcess:

    def __init__(self, side):
        self.side = side

    def first_throw(self):
        return self.check_win_possibility(self.side)

    def second_throw(self, second_result, winning_numbers, current_bet_amount):

        if second_result in winning_numbers:
            if len(winning_numbers) == 6:
                coefficient = 0.33
            elif len(winning_numbers) == 5:
                coefficient = 0.80
            elif len(winning_numbers) == 4:
                coefficient = 1.20
            elif len(winning_numbers) == 3:
                coefficient = 2.0
            elif len(winning_numbers) == 2:
                coefficient = 3.0
            elif len(winning_numbers) == 1:
                coefficient = 4.0
            else:
                coefficient = 0
            prize = self.find_prize(current_bet_amount, coefficient)
            return prize

        else: return False

    def find_prize(self, summ, coefficient):
        return int(summ) * coefficient


    @staticmethod
    def check_win_possibility(side):
        if side == 1: return SET1
        elif side == 2: return SET2
        elif side == 3: return SET3
        elif side == 4: return SET4
        elif side == 5: return SET5
        elif side == 6: return SET6

    def __del__(self):
        print("Instance was deleted")

class Bets:
    def __init__(self):
        pass