let privateKey = {exp: BigInt(65537), n: BigInt("78545622709407237783487545989633655198538440915426578299716775810672117132447538742831070614019469886822378020418450406333221149467016550765219847910032020382617138011805481453392680787055727436108966298436735538203181920241919366684715337522820331429740124829409786660157635265372748246706077927075961766161")};

export let publicKey = {exp: BigInt("70942384378869075882600337363083219435846711523366120653907489060547700221568994015661375449832224255163907749250489569282731273942980464309407791893716897751372941400234736989894167287593394213821449288713974578127708977722822911328724028434635949947809415081862128047839003355825672821350209921643386309909"), n: BigInt("78545622709407237783487545989633655198538440915426578299716775810672117132447538742831070614019469886822378020418450406333221149467016550765219847910032020382617138011805481453392680787055727436108966298436735538203181920241919366684715337522820331429740124829409786660157635265372748246706077927075961766161")};


export function rsaEnc(message, {exp, n}){
    let encode = stringEncode(message);
    if (encode >= n) {
        console.log("Le message ne remplit pas les conditions de chiffrement");
        return -1;
    }
    return rsa(encode, {exp, n});
}

export function rsaDec(message){
    if (message >= n){
        console.log("Le message ne remplit pas les conditions de déchiffrement");
        return -1;
    }
    let decode = rsa(message, privateKey);
    return bigIntDecode(decode);
}

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
