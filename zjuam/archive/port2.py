class BigInt:
    def __init__(self, flag=False):
        if flag:
            self.digits = None
        else:
            self.digits = [0]

    def __add__(self, other):
        result = BigInt()
        carry = 0
        max_len = max(len(self.digits), len(other.digits))

        for i in range(max_len):
            x = self.digits[i] if i < len(self.digits) else 0
            y = other.digits[i] if i < len(other.digits) else 0
            digit_sum = x + y + carry

            result.digits.append(digit_sum % 65536)
            carry = digit_sum // 65536

        if carry > 0:
            result.digits.append(carry)

        return result

    def __sub__(self, other):
        result = BigInt()
        borrow = 0
        max_len = max(len(self.digits), len(other.digits))

        for i in range(max_len):
            x = self.digits[i] if i < len(self.digits) else 0
            y = other.digits[i] if i < len(other.digits) else 0
            digit_diff = x - y - borrow

            if digit_diff < 0:
                digit_diff += 65536
                borrow = 1
            else:
                borrow = 0

            result.digits.append(digit_diff)

        return result

    def __mul__(self, other):
        result = BigInt()

        for i in range(len(self.digits)):
            carry = 0

            for j in range(len(other.digits)):
                product = self.digits[i] * other.digits[j] + carry

                if len(result.digits) <= i + j:
                    result.digits.append(product % 65536)
                else:
                    result.digits[i + j] += product

                carry = product // 65536

            if carry > 0:
                result.digits.append(carry)

        return result

    def __mod__(self, other):
        result = BigInt()
        dividend = 0

        for i in range(len(self.digits) - 1, -1, -1):
            dividend = (dividend * 65536) + self.digits[i]
            quotient = dividend // other

            result.digits.insert(0, quotient)
            dividend = dividend % other

        return result

    def to_string(self, radix=10):
        if radix == 16:
            return ''.join('{:04x}'.format(digit) for digit in reversed(self.digits))
        else:
            return ''.join(str(digit) for digit in reversed(self.digits))


class RSAKeyPair:
    def __init__(self, encryption_exponent, decryption_exponent, modulus):
        self.e = BigInt(flag=True)
        self.e.digits = [int(encryption_exponent, 16)]
        # self.d = BigInt(flag=True)
        # self.d.digits = [int(decryption_exponent, 16)]
        self.m = BigInt(flag=True)
        self.m.digits = [int(modulus, 16)]
        self.chunk_size = 2 * (len(self.m.digits)-1)
        self.radix = 16

    def pow_mod(self, x, y):
        result = BigInt(flag=True)
        result.digits[0] = 1
        a = x
        k = y

        while True:
            if k.digits[0] & 1 != 0:
                result = self.multiply_mod(result, a)

            k = k >> 1
            if k.digits[0] == 0 and len(k.digits) == 1:
                break

            a = self.multiply_mod(a, a)

        return result

    def multiply_mod(self, x, y):
        xy = x * y
        return xy % self.m

    def encrypt_string(self, s):
        a = [ord(c) for c in s]
        
        while len(a) % self.chunk_size != 0:
            a.append(0)

        
        result = ''
        for i in range(0, len(a), self.chunk_size):
            block = BigInt(flag=True)
            for j in range(i, i + self.chunk_size, 2):
                block.digits.insert(0, (a[j + 1] << 8) + a[j])

            crypt = self.pow_mod(block, self.e)
            text = crypt.to_string(self.radix)
            result += text + ' '

        return result.strip()


key = RSAKeyPair('010001', '', '123abcdef')

plaintext = 'Hello, World!'
encrypted = key.encrypt_string(plaintext)
print(encrypted)