import {rsaEncText, rsaSign, getPublicKey} from "./security.js"

const serverAddress = "http://127.0.0.1:8000";

export function getServerKey(){
    let serverKey = localStorage.getItem("serverKey");
    if (serverKey != null) {
        serverKey = JSON.parse(serverKey,
            (key, value, context) => {
                if (key == "e" | key == "n"){
                    return BigInt(context.source);
                }
                return value;
            }
        )
    }
    return serverKey;
}

export function getToken(){
    let token = localStorage.getItem("token");
    return token;
}

async function getData(request){
    const data = (await request).text();
    return data;
}

async function sendRequest(file="", method, body, token=null, signature=true){
    let stringBody = JSON.stringify(body);
    let requestParam = null
    if (method == "GET"){
        if (token == null){
            requestParam = {
                method: method,
                headers: {
                    "Accept": "application/json"
                },
            };
        }
        else{
            requestParam = {
                method: method,
                headers: {
                    "Accept": "application/json",
                    "Authorization": "Bearer " + token,
                },
            };
        }
    } 
    else if (signature == false){
        requestParam = {
            method: method,
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: stringBody,
        };
    }
    else if (token == null){
        let json = {"message": stringBody, "signature": rsaSign(stringBody).toString()};
        requestParam = {
            method: method,
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(json),
        };
    }
    else{
        let json = {"message": stringBody, "signature": rsaSign(stringBody).toString()};
        requestParam = {
            method: method,
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer " + token,
                
            },
            body: JSON.stringify(json),
        };
    }
    return await fetch(serverAddress + file, requestParam);
}

// Get public Key Request
export async function publicKeyRequest(){
    const req = sendRequest("/auth/public-key", "GET", {}, false, false);
    let data = JSON.parse(await getData(req));
    localStorage.setItem("serverKey", data.message);
}

// Create Account
export async function createAccountRequest(username, password){
    if (getServerKey() == null) await publicKeyRequest();
    const req = sendRequest("/auth/register", "POST", {
        "username": rsaEncText(username, getServerKey()).toString(),
        "password": rsaEncText(password, getServerKey()).toString(),
        "public_key_e": getPublicKey().e.toString(),
        "public_key_n": getPublicKey().n.toString()
    }, null, false);
    let data = await getData(req);
    return data;
}

// Login
export async function loginRequest(username, password){
    if (getServerKey() == null) await publicKeyRequest();
    const req = sendRequest("/auth/login", "POST", {
        "username": rsaEncText(username, getServerKey()).toString(),
        "password": rsaEncText(password, getServerKey()).toString(),
        "public_key_e": getPublicKey().e.toString(),
        "public_key_n": getPublicKey().n.toString()
    }, null, false);
    let data = await getData(req);
    return data;
}

//Create auction
export async function createAuctionRequest(title, description, price, timestamp){
    if (getServerKey() == null) await publicKeyRequest();
    const req = sendRequest("/create-auction", "POST", {
        "title": title,
        "description": description,
        "price": price,
        "timestamp": timestamp,
    }, getToken());
    let data = await getData(req);
    return data;
}

// Bid request
export async function bidRequest(auctionId, price){
    if (getServerKey() == null) await publicKeyRequest();
    const req = sendRequest("/bid", "POST", {
        "auction_id": auctionId,
        "price": price
    }, getToken());
    let data = await getData(req);
    return data;
}

// Cancel bid request
export async function cancelBidRequest(bidId){
    if (getServerKey() == null) await publicKeyRequest();
    const req = sendRequest("/cancel-bid", "POST", {
        "bid_id": bidId,
    }, getToken());
    let data = await getData(req);
    return data;
}

// Get auction price request
export async function updatePriceRequest(id){
    if (getServerKey() == null) await publicKeyRequest();
    const req = sendRequest("/update-price", "POST", {"auction_id": id}, getToken(), true);
    let data = await getData(req);
    return data;
}


// Get list auction request
export async function auctionListRequest(){
    if (getServerKey() == null) await publicKeyRequest();
    const req = sendRequest("/list-auctions", "POST", {}, getToken(), false);
    let data = await getData(req);
    return data;
}

// Get auction request
export async function auctionRequest(auction_id){
    if (getServerKey() == null) await publicKeyRequest();
    const req = sendRequest("/get-auction", "POST", {
        "auction_id": auction_id
    }, getToken());
    let data = await getData(req);
    return data;
}

// Add Balance request
export async function addBalanceRequest(amount){
    if (getServerKey() == null) await publicKeyRequest();
    const req = sendRequest("/balance", "POST", {"amount": amount}, getToken());
    let data = await getData(req);
    return data;
}

// Get balance request
export async function getBalanceRequest(){
    if (getServerKey() == null) await publicKeyRequest();
    const req = sendRequest("/get-balance", "GET", {}, getToken());
    let data = await getData(req);
    return data;
}