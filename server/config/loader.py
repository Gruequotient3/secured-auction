# FastAPI
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, HTTPException, Form, UploadFile, Depends, File

# Builtins
import os
import re
import time
import aiosqlite


app = FastAPI(title="Secured Auction")
security = HTTPBearer(auto_error=False)
