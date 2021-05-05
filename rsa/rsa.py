import sys
import os
import random

if len(sys.argv) < 2:
    print("provide command")
    exit()

def gen_prime():
    n = 256 # need to fit in 2 byte blocks
    primes = list(range(2, n))

    for i in range(0, n):
        if i >= len(primes):
            break
        x = primes[i]
        for j in range(2, n):
            if x * j > n:
                break
            if x * j in primes:
                primes.remove(x *j)
    while True:
        yield random.choice(primes)

def gen_key_pair():
    def get_filenames():
        i = 1
        while os.path.exists(f"key-{i}-A") or os.path.exists(f"key-{i}-B"):
            i += 1
        return f"key-{i}-A", f"key-{i}-B"

    def gcd(x, y):
        if x == y:
            return x
        return gcd(x - y, y) if x > y else gcd(x, y - x)

    def lcm(x, y):
        return x * y // gcd(x, y)

    def carmichael(x, y):
        return lcm(x - 1, y - 1)

    def gen_coprime(x):
        nums = list(range(2, x - 1))
        random.shuffle(nums)
        coprimes = filter(lambda i: gcd(x, i) == 1, nums)
        return coprimes.__next__()

    def inverse(x, mod):
        # naive
        for y in range(1, mod):
            if x * y % mod == 1:
                return y
        raise "not found"


    pg = gen_prime()
    while True: 
        p, q = pg.__next__(), pg.__next__()
        n = p * q
        if q != p and n > 128: # p, q has to be distinct and their multiple has to be large enough to handle ascii
            break
    print(f"1. Generated 2 distinct primes: P={p}, Q={q}, P * Q = {n}")

    l = carmichael(p, q)
    k1 = gen_coprime(l) # 'e', in practice chosen, e.g. 65537 or 3 and part of public key; coprimality with 'l' ensures it will have a multiplicative inverse in 'mod l'
    k2 = inverse(k1, l)

    print(f"2. lambda={l}, selected coprime to lambda and it's inverse in mod lambda: k1={k1}, k2={k2}")

    a, b = get_filenames()
    with open(a, "w") as f:
        f.write(f"{n},{k1}")
    with open(b, "w") as f:
        f.write(f"{n},{k2}")

    print(f"3. key A: (n={n}, k={k1}) -> file {a}")
    print(f"   key B: (n={n}, k={k2}) -> file {b}")

def ints_to_hex(data):
    def as_two_byte_hex(i):
        s = hex(i)[2:]
        s = (4 - len(s)) * '0' + s
        return s
    return ''.join(map(as_two_byte_hex, data))

def hex_to_ints(data):
    for i in range(0, len(data)//4):
        yield int(data[i*4: i*4 + 4], 16)

def get_key_from_file(key_file):
    with open(key_file, "r") as f:
        line = f.readline().split(',')
        n, exponent = map(int, line)
    return n, exponent

def encrypt(key_file):
    """
    Encrypts 'data' from stdin using key from 'key_file'.
    """
    data = input()
    n, exponent = get_key_from_file(key_file)

    # To encrypt 'data', we need to transform it to a sequence of numbers
    # then encrypt the numbers
    # and finally encoding the numbers to hex:
    #    string -> sequence of ints -> modular_exp -> hex encode
    sequence_of_ints = data.encode()
    encrypted = modular_exp(exponent, n, sequence_of_ints)
    encoded = ints_to_hex(encrypted)
    return encoded


def decrypt(key_file):
    data = input()
    n, exponent = get_key_from_file(key_file)

    # Decryption is basically the same as encryption - just the exponent is differenct
    # First the hex encoded sequence of ints is decoded
    # then the numbers are exponeniated
    # and finally the result is transformed back to characters:
    #      hex encoded -> sequence of ints -> modular_exp -> string
    sequence_of_ints = hex_to_ints(data)
    decrypted = modular_exp(exponent, n, sequence_of_ints)
    decoded = ''.join(map(chr, decrypted))
    return decoded 

def modular_exp(exponent, modulo, message): 
    """
    message is a sequence of numbers

    Exponentiates every number from 'message' to 'exponent' in multiplicative group 'modulo'
    """
    return map(lambda x: x ** exponent % modulo, message)

command = sys.argv[1]
if command == "gen-key-pair":
    gen_key_pair()
elif command == "encrypt":
    print(encrypt(sys.argv[2]))
elif command == "decrypt":
    print(decrypt(sys.argv[2]))
else:
    print(f"unknown command {command}")
