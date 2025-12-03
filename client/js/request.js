import {rsaEnc, rsaDec, publicKey} from "./security.js"

const serverAddress = "http://127.0.0.0:8000"; // TODO temporary local Server
async function sendRequest(method, body){
    let requestParam = {
        method: method,
        mode: "no-cors",
        headers: {
            "content-type": "application/json",
            "Accept": "application/json",
        },
        body: JSON.stringify(body),
    };
    let req = await fetch(serverAddress, requestParam);
    return req;
}

