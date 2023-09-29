import math

class BigInt:
    def __init__(self, flag=False):
        if flag:
            self.digits = None
        else:
            self.digits = [0 for _ in range(20)]
        self.is_neg = False
    
    def __str__(self):
        return ' '.join(map(str, self.digits))

class RSAKeyPair:
    def __init__(self, encryption_exponent, decryption_exponent, modulus):
        self.e = RSAUtils.biFromHex(encryption_exponent)
        self.d = RSAUtils.biFromHex(decryption_exponent)
        self.m = modulus
        self.chunk_size = 2 * max(len(str(self.m)), 1)  # Adjust chunk size as needed

class RSAUtils:
    @staticmethod
    def biFromDecimal(s):
        is_neg = s[0] == '-'
        i = 1 if is_neg else 0
        result = BigInt()
        while i < len(s) and s[i] == '0':
            i += 1
        if i == len(s):
            return result
        fgl = len(s) - i
        digits = int(s[i:i+15])
        result.digits = [digits]
        i += 15
        while i < len(s):
            result = RSAUtils.biMultiply(result, BigInt(10**15))
            result = RSAUtils.biAdd(result, BigInt(int(s[i:i+15])))
            i += 15
        result.is_neg = is_neg
        return result

    @staticmethod
    def biFromHex(s):
        result = BigInt()
        for i in range(len(s), 0, -4):
            start = max(i - 4, 0)
            digits = int(s[start:i], 16)
            result.digits.append(digits)
        return result

    @staticmethod
    def biHighIndex(x):
        result = len(x.digits) - 1
        while result > 0 and x.digits[result] == 0:
            result -= 1
        return result

    @staticmethod
    def biMultiply(x, y):
        result = BigInt()
        result.digits = [0] * (len(x.digits) + len(y.digits) + 1)
        for i in range(len(x.digits)):
            carry = 0
            for j in range(len(y.digits)):
                product = x.digits[i] * y.digits[j] + result.digits[i+j] + carry
                result.digits[i+j] = product & 0xFFFF
                carry = product >> 16
            result.digits[i + len(y.digits)] = carry
        result.is_neg = x.is_neg != y.is_neg
        return RSAUtils.biNormalize(result)

    @staticmethod
    def biMultiplyByRadixPower(x, n):
        res = BigInt()
        res.digits = x.digits + [0] * n
        return res

    @staticmethod
    def biDivideModulo(x, y):
        nb = RSAUtils.biNumBits(x)
        tb = RSAUtils.biNumBits(y)
        orig_y_is_neg = y.is_neg

        if nb < tb:
            if x.is_neg:
                q = RSAUtils.biCopy(BigInt(1))
                q.is_neg = not y.is_neg
                x.is_neg = False
                y.is_neg = False
                r = RSAUtils.biSubtract(y, x)
                x.is_neg = True
                y.is_neg = orig_y_is_neg
            else:
                q = BigInt()
                r = RSAUtils.biCopy(x)
            return q, r

        q = BigInt()
        r = RSAUtils.biCopy(x)

        t = math.ceil(tb / 16) - 1
        lambda_val = 0
        while y.digits[t] < 0x8000:
            y = RSAUtils.biShiftLeft(y, 1)
            lambda_val += 1
            tb += 1
            t = math.ceil(tb / 16) - 1

        r = RSAUtils.biShiftLeft(r, lambda_val)
        nb += lambda_val

        n = math.ceil(nb / 16) - 1
        b = RSAUtils.biMultiplyByRadixPower(y, n - t)
        while RSAUtils.biCompare(r, b) != -1:
            q.digits[n - t] += 1
            r = RSAUtils.biSubtract(r, b)
        for i in range(n, t, -1):
            ri = r.digits[i] if i < len(r.digits) else 0
            ri1 = r.digits[i - 1] if i - 1 < len(r.digits) else 0
            ri2 = r.digits[i - 2] if i - 2 < len(r.digits) else 0
            yt = y.digits[t] if t < len(y.digits) else 0
            yt1 = y.digits[t - 1] if t - 1 < len(y.digits) else 0

            if ri == yt:
                q.digits[i - t - 1] = 0xFFFF
            else:
                q.digits[i - t - 1] = (ri * (0x10000) + ri1) // yt

            while True:
                c1 = q.digits[i - t - 1] * (yt * 0x10000 + yt1)
                c2 = (ri * (0x100000000) + (ri1 * 0x10000) + ri2)
                if c1 <= c2:
                    break
                q.digits[i - t - 1] -= 1

            b = RSAUtils.biMultiplyByRadixPower(y, i - t - 1)
            r = RSAUtils.biSubtract(r, RSAUtils.biMultiplyDigit(b, q.digits[i - t - 1]))
            if r.is_neg:
                r = RSAUtils.biAdd(r, b)
                q.digits[i - t - 1] -= 1

        r = RSAUtils.biShiftRight(r, lambda_val)
        return q, r

    @staticmethod
    def biAdd(x, y):
        if x.is_neg != y.is_neg:
            y.is_neg = not y.is_neg
            res = RSAUtils.biSubtract(x, y)
            y.is_neg = not y.is_neg
            return res

        result = BigInt()
        carry = 0
        x_digits = x.digits if len(x.digits) > len(y.digits) else y.digits
        y_digits = y.digits if len(x.digits) > len(y.digits) else x.digits
        for i in range(len(x_digits)):
            sum = x_digits[i] + y_digits[i] + carry
            carry = sum >> 16
            result.digits.append(sum & 0xFFFF)
        if carry:
            result.digits.append(carry)
        result.is_neg = x.is_neg
        return RSAUtils.biNormalize(result)

    @staticmethod
    def biSubtract(x, y):
        if x.is_neg != y.is_neg:
            y.is_neg = not y.is_neg
            res = RSAUtils.biAdd(x, y)
            y.is_neg = not y.is_neg
            return res

        if RSAUtils.biCompare(x, y) >= 0:
            result = BigInt()
            borrow = 0
            for i in range(len(x.digits)):
                diff = x.digits[i] - y.digits[i] - borrow
                if diff < 0:
                    diff += 0x10000
                    borrow = 1
                else:
                    borrow = 0
                result.digits.append(diff)
            result.is_neg = x.is_neg
            return RSAUtils.biNormalize(result)
        else:
            return RSAUtils.biNegate(RSAUtils.biSubtract(y, x))

    @staticmethod
    def biShiftLeft(x, n):
        result = BigInt()
        w = math.floor(n / 16)
        carry = 0
        for i in range(len(x.digits)):
            val = x.digits[i]
            val = val << n % 16 | carry
            carry = val >> 16
            result.digits.append(val & 0xFFFF)
        if carry or w > 0:
            result.digits.append(carry)
        result.digits = result.digits[w:]
        return RSAUtils.biNormalize(result)

    @staticmethod
    def biShiftRight(x, n):
        result = BigInt()
        q = math.floor(n / 16)
        r = n % 16
        result.digits = x.digits[q:]
        if r > 0:
            result.digits = [digit >> r for digit in result.digits]
        return RSAUtils.biNormalize(result)

    @staticmethod
    def biNumBits(x):
        if x.is_neg:
            x = RSAUtils.biNegate(x)
        n = RSAUtils.biHighIndex(x)
        d = x.digits[n]
        m = (n + 1) * 16
        result = m
        while result > m - 16:
            if d & 0x8000:
                break
            d <<= 1
            result -= 1
        return result

    @staticmethod
    def biCompare(x, y):
        if x.is_neg != y.is_neg:
            return 1 - 2 * int(x.is_neg)
        for i in range(len(x.digits) - 1, -1, -1):
            if x.digits[i] != y.digits[i]:
                if x.is_neg:
                    return 1 - 2 * int(x.digits[i] > y.digits[i])
                else:
                    return 1 - 2 * int(x.digits[i] < y.digits[i])
        return 0

    @staticmethod
    def biCompareMagnitude(x, y):
        if x.is_neg != y.is_neg:
            return 1 - 2 * int(x.is_neg)
        for i in range(len(x.digits) - 1, -1, -1):
            if x.digits[i] != y.digits[i]:
                return 1 - 2 * int(x.digits[i] < y.digits[i])
        return 0

    @staticmethod
    def biMultiplyDigit(x, y):
        result = BigInt()
        carry = 0
        for i in range(len(x.digits)):
            product = x.digits[i] * y + carry
            result.digits.append(product & 0xFFFF)
            carry = product >> 16
        if carry:
            result.digits.append(carry)
        return RSAUtils.biNormalize(result)

    @staticmethod
    def biModuloByRadixPower(x, n):
        result = BigInt()
        result.digits = x.digits[:n]
        return RSAUtils.biNormalize(result)

    @staticmethod
    def biNormalize(x):
        while len(x.digits) > 0 and x.digits[-1] == 0:
            x.digits.pop()
        if len(x.digits) == 0:
            x.is_neg = False
            x.digits = [0]
        return x

    @staticmethod
    def biNegate(x):
        neg = BigInt()
        neg.digits = x.digits.copy()
        neg.is_neg = not x.is_neg
        return neg

    @staticmethod
    def biCopy(x):
        copy = BigInt()
        copy.digits = x.digits.copy()
        copy.is_neg = x.is_neg
        return copy

    @staticmethod
    def biAdd(x, y):
        if x.is_neg != y.is_neg:
            return RSAUtils.biSubtract(x, RSAUtils.biNegate(y))

        result = BigInt()
        carry = 0
        for i in range(len(x.digits)):
            sum_ = x.digits[i] + y.digits[i] + carry
            carry = sum_ >> 16
            result.digits.append(sum_ & 0xFFFF)
        if carry:
            result.digits.append(carry)
        result.is_neg = x.is_neg
        return RSAUtils.biNormalize(result)

    @staticmethod
    def biSubtract(x, y):
        if x.is_neg != y.is_neg:
            return RSAUtils.biAdd(x, RSAUtils.biNegate(y))

        if RSAUtils.biCompareMagnitude(x, y) >= 0:
            result = BigInt()
            carry = 0
            for i in range(len(x.digits)):
                diff = x.digits[i] - y.digits[i] - carry
                if diff < 0:
                    diff += 0x10000
                    carry = 1
                else:
                    carry = 0
                result.digits.append(diff)
            result.is_neg = x.is_neg
            return RSAUtils.biNormalize(result)
        else:
            return RSAUtils.biNegate(RSAUtils.biSubtract(y, x))

    @staticmethod
    def biModulo(x, y):
        q, r = RSAUtils.biDivideModulo(x, y)
        return r

    @staticmethod
    def biPowMod(x, y, m):
        result = BigInt(1)
        a = x
        k = y
        while RSAUtils.biCompare(k, BigInt(0)) > 0:
            if k.digits[0] & 1:
                result = RSAUtils.biMultiplyMod(result, a, m)
            k = RSAUtils.biShiftRight(k, 1)
            a = RSAUtils.biMultiplyMod(a, a, m)
        return result

    @staticmethod
    def biMultiplyMod(x, y, m):
        return RSAUtils.biModulo(RSAUtils.biMultiply(x, y), m)

    @staticmethod
    def biDivide(x, y):
        return RSAUtils.biDivideModulo(x, y)[0]

    @staticmethod
    def getKeyPair(encryption_exponent, decryption_exponent, modulus):
        return RSAKeyPair(encryption_exponent, decryption_exponent, modulus)

    @staticmethod
    def biFromNumber(i):
        result = BigInt()
        result.is_neg = i < 0
        i = abs(i)
        j = 0
        while i > 0:
            result.digits.append(i & 0xFFFF)
            i = math.floor(i / 0x10000)
            j += 1
        return result

    @staticmethod
    def biMultiplyByRadixPower(x, n):
        result = BigInt()
        result.digits = [0] * n + x.digits
        return RSAUtils.biNormalize(result)

    @staticmethod
    def twoDigit(n):
        return ('0' + str(n)) if n < 10 else str(n)

    @staticmethod
    def encryptedString(key, s):
        a = [ord(c) for c in s]

        while len(a) % key.chunk_size != 0:
            a.append(0)

        al = len(a)
        result = ""
        for i in range(0, al, key.chunk_size):
            block = BigInt()
            j = 0
            for k in range(i, i + key.chunk_size, 2):
                block.digits[j] = a[k] + (a[k+1] << 8)
                j += 1
            crypt = RSAUtils.biPowMod(block, key.e, key.m)
            text = '{:x}'.format(crypt) if key.radix == 16 else str(crypt)
            result += text + " "
        return result.rstrip()

# Test Example
key = RSAUtils.getKeyPair("3", "", "13")

encrypted_str = RSAUtils.encryptedString(key, "Hello, World!")
print("Encrypted String:", encrypted_str)
