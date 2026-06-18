from abc import ABC, abstractmethod

class BaseAccount(ABC):
    bank_name = "Vietcombank"

    def __init__(self, account_number, owner_name, initial_balance=0):
        self.account_number = account_number
        self.owner_name = owner_name.upper().strip()
        self.__balance = float(initial_balance)

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        self.__balance = value

    @abstractmethod
    def deposit(self, amount): pass

    @abstractmethod
    def withdraw(self, amount): pass

    def __add__(self, other):
        if not isinstance(other, BaseAccount):
            raise TypeError("Chỉ có thể cộng với đối tượng tài khoản khác!")
        return self.balance + other.balance

    def __lt__(self, other):
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance < other.balance

    @staticmethod
    def validate_account_number(account_number):
        return len(account_number) == 10 and account_number.isdigit()

    @classmethod
    def update_bank_name(cls, new_name):
        cls.bank_name = new_name

class SavingsAccount(BaseAccount):
    def __init__(self, account_number, owner_name, balance, interest_rate):
        super().__init__(account_number, owner_name, balance)
        self.interest_rate = interest_rate

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        penalty = amount * 0.02
        total_deduction = amount + penalty
        if self.balance >= total_deduction:
            self.balance -= total_deduction
            return penalty
        raise ValueError("Số dư không đủ cho giao dịch này (bao gồm phí 2%)!")

    def apply_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        return interest

class CreditAccount(BaseAccount):
    def __init__(self, account_number, owner_name, balance, credit_limit):
        super().__init__(account_number, owner_name, balance)
        self.credit_limit = credit_limit

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if (self.balance - amount) >= -self.credit_limit:
            self.balance -= amount
        else:
            raise ValueError("Vượt quá hạn mức thấu chi cho phép!")

class DigitalPremiumMixin:
    def cashback_reward(self, amount):
        if amount > 5_000_000:
            return amount * 0.01
        return 0

class HybridAccount(SavingsAccount, DigitalPremiumMixin):
    def __str__(self):
        return f"HybridAccount: {self.owner_name} (Số dư: {self.balance})"

class VNPayGateway:
    def execute_pay(self, account, amount):
        account.withdraw(amount)
        print(f"[Hệ thống VNPay]: Thanh toán thành công {amount} VND.")

class ViettelMoneyGateway:
    def execute_pay(self, account, amount):
        account.withdraw(amount)
        print(f"[Hệ thống ViettelMoney]: Thanh toán thành công {amount} VND.")

def process_payment(gateway, account, amount):
    if not hasattr(gateway, 'execute_pay'):
        raise AttributeError("Cổng thanh toán không hợp lệ!")
    gateway.execute_pay(account, amount)

def main():
    accounts = []
    current_account = None

    while True:
        print("\n===== VIETCOMBANK DIGIBANK PRO SIMULATOR =====")
        print("1. Mở tài khoản mới | 2. Xem thông tin & MRO | 3. Nạp/Rút | 4. Lãi suất | 5. Gộp/So sánh | 6. Thanh toán | 7. Thoát")
        choice = input("Chọn chức năng (1-7): ")

        if choice == "1":
            print("1. Savings | 2. Credit | 3. Hybrid")
            t = input("Loại: ")
            acc_no = input("Số tài khoản (10 số): ")
            if not BaseAccount.validate_account_number(acc_no):
                print("Số tài khoản không hợp lệ!")
                continue
            name = input("Tên: ")
            if t == "1":
                current_account = SavingsAccount(acc_no, name, 10000000, 0.06)
            elif t == "3":
                current_account = HybridAccount(acc_no, name, 10000000, 0.06)
            accounts.append(current_account)
            print("Mở tài khoản thành công!")

        elif choice == "2":
            if not current_account: print("Chưa có tài khoản!")
            else:
                print(f"Loại: {type(current_account).__name__} | MRO: {[c.__name__ for c in type(current_account).mro()]}")
                print(f"Số dư: {current_account.balance}")

        elif choice == "3":
            g = input("1. Nạp | 2. Rút: ")
            amt = float(input("Số tiền: "))
            if g == "1":
                current_account.deposit(amt)
                if isinstance(current_account, HybridAccount):
                    reward = current_account.cashback_reward(amt)
                    if reward: 
                        current_account.deposit(reward)
                        print(f"Được hoàn: {reward}")
            else:
                try: current_account.withdraw(amt)
                except Exception as e: print(e)

        elif choice == "4":
            if isinstance(current_account, SavingsAccount):
                print(f"Lãi nhận được: {current_account.apply_interest()}")
            else: print("Không hỗ trợ!")

        elif choice == "5":
            if len(accounts) > 1:
                other = accounts[1]
                print(f"Tổng số dư: {current_account + other}")
                print(f"Nhỏ hơn: {current_account < other}")

        elif choice == "6":
            gate = VNPayGateway() if input("1. VNPay | 2. Viettel: ") == "1" else ViettelMoneyGateway()
            process_payment(gate, current_account, 500000)

        elif choice == "7": break

if __name__ == "__main__":
    main()