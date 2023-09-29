# RSAUtils.encryptedString = function(key, s) {
# 	var a = [];
# 	var sl = s.length;
# 	var i = 0;
# 	while (i < sl) {
# 		a[i] = s.charCodeAt(i);
# 		i++;
# 	}

# 	while (a.length % key.chunkSize != 0) {
# 		a[i++] = 0;
# 	}

# 	var al = a.length;
# 	var result = "";
# 	var j, k, block;
# 	for (i = 0; i < al; i += key.chunkSize) {
# 		block = new BigInt();
# 		j = 0;
# 		for (k = i; k < i + key.chunkSize; ++j) {
# 			block.digits[j] = a[k++];
# 			block.digits[j] += a[k++] << 8;
# 		}x
# 		var crypt = key.barrett.powMod(block, key.e);
# 		var text = key.radix == 16 ? RSAUtils.biToHex(crypt) : RSAUtils.biToString(crypt, key.radix);
# 		result += text + " ";
# 	}
# 	return result.substring(0, result.length - 1); // Remove last space.
# };

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP

class RSAKey:
    def __init__(self, encrypt_component, decrypt_component, modulus) -> None:
        self.encrypt_component = encrypt_component
        self.decrypt_component = decrypt_component
        self.modulus = modulus
        self.chunk_size = 2 * ((len(hex(modulus))-2)//4 - 1)


def encrypted_string(key:RSAKey,s):
    # convert to an array of ascii
    asciis = [ord(character) for character in s]
    
    # pad the array with zeros
    while len(asciis) % key.chunk_size != 0:
        asciis.append(0)

    result = ""

    for i in range(0, len(asciis), key.chunk_size):
        block = []
        block2 = bytes()
        for j in range(0,len(asciis),2):
            block.append(asciis[j] + (asciis[j+1] << 8))
            block2 += (asciis[j] + (asciis[j+1] << 8)).to_bytes(2,'big')
        
        recipient_key = RSA.construct((key.modulus,key.encrypt_component))
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        crypt = int.from_bytes(cipher_rsa.encrypt(block[0].to_bytes(2, 'big')))


        print(block)

"16ecd3e67818f96339ae9ab22aa4ccd2405ed7b74eec76ab19a5d40c4b7f284573205a7a2b66d6206898f6a260bc688a759aafda5672128fb6a0f8df66f65d6e "


if __name__ == "__main__":
    key = RSAKey(0x10001,None,0xbebcaa8382840d5c322750befaf103ac49776a2e14868b11400bba39794f57c10de35676e885505c4d2a08ace7d73cb56080458007e48764fcab4dc635c67153)
    print(encrypted_string(key, '78319wkfj'))
    
    b'8713w9fk\x00j\x00\x00'