# dependency wiring (engine/mqtt/audio/cfg)
from fastapi import Request

def get_cfg(request: Request):
    return request.app.state.cfg

def get_engine(request: Request):
    return request.app.state.engine

def get_mqtt(request: Request):
    return request.app.state.mqtt

def get_audio(request: Request):
    return request.app.state.audio

def get_registry(request: Request):
    return request.app.state.registry

def get_bluetooth(request: Request):
    return request.app.state.bluetooth
