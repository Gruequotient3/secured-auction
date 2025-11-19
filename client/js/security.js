const privateKey = {exp: BigInt(65537), n: BigInt(552876223337)};
const publicKey = {exp: BigInt(73191337793), n: BigInt(552876223337)};

function modularExponentiation(base, exponent, modulo){
    if (modulo === 1n) return 0n;
    let result = 1n;
    
    base = base % modulo;
    while (exponent > 0n) {
        if (exponent % 2n === 1n)
            result = (result * base) % modulo;
        exponent = exponent / 2n;
        base = (base * base) % modulo;
    }
    return result;
}

function rsa(message , {exp, n}){
    return modularExponentiation(message, exp, n);
}

function rsaEnc(message, {exp, n}){
    let encode = stringEncode(message);
    if (encode >= n) {
        console.log("Le message ne remplit pas les conditions de chiffrement");
        return -1;
    }
    return rsa(encode, {exp, n});
}

function rsaDec(message, {exp, n}){
    if (message >= n){
        console.log("Le message ne remplit pas les conditions de déchiffrement");
        return -1;
    }
    let decode = rsa(message, {exp, n});
    return bigIntDecode(decode);
}

function bytesToBigInt(bytes) {
    let result = 0n;
    for (const byte of bytes) {
        result = (result << 8n) + BigInt(byte);
    }
    return result;
}

function bigIntToBytes(value) {
    const bytes = [];
    while (value > 0n) {
        bytes.unshift(Number(value & 0xFFn)); // extrait l’octet de poids faible
        value >>= 8n; // décale de 8 bits
    }
    return Uint8Array.from(bytes);
}

function stringEncode(string){
    const utf8Encode = new TextEncoder();
    return bytesToBigInt(utf8Encode.encode(string));
}

function bigIntDecode(value){
    const utf8Decode = new TextDecoder();
    return utf8Decode.decode(bigIntToBytes(value))
}
